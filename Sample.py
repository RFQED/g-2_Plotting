import math, re, sys, copy, os 

from odict import OrderedDict
import Utils as utils
from Logging import log, INFO
from ROOT  import gROOT, gStyle, gPad, gDirectory
from ROOT  import TFile, TCanvas, TPostScript, TH1, TLegend 
from ROOT  import TKey, TObject

__author__  = 'Carl Gwilliam'
__version__ = '0.8'

testVerbose = False

# TODO: Check TProfile; Draw should be able to set axis range, norm etc; Allow Draw and Print functions (need to solve canvas update issue)

class Sample(object):
    """
    Implementation of a Sample object which a set of histograms from a file along with specified
    style and plotting attributes.  Samples can be added, subtracted, divided and multiplied and 
    are iterable (iterating over the stored histograms)
    
    Example:
    
    s = Sample(FileName     = 'file.root',
               Label        = 'Data',
               Type         = 'e',
               MarkerColour = 2)
                       
    A particular histogram can be retrived by Get('histname') or printed to file via Draw('histname')

    """
    if testVerbose: print '### in sample', '\n' 

    # Object (rather than instance) variables relavent to all Sample objects
    CutHist     =  ''
    Lumi        =  None   # fb -l
    OutputLevel = INFO    # Default logging level for all samples; will be overriden if set on individual sample
    
    def __init__(self, sample=None, **kwargs):
        """
        Initalise sample object from a set of keyword arguments, or alternatively another sample
        object.  Create the TFile and extract the histograms into the local data structure

        """

        if testVerbose: print 'Sample ### in __init__, kwargs = ', kwargs, 'sample = ', sample
        
        self.FileName    = ''
        self.OutputLevel = Sample.OutputLevel
        self.Label       = 'Data'
        self.Legend      = ''
        self.Type        = ''
        self.Type2D      = ''
        self.TypeGraph   = 'apl'
        self.LineColour  = 0
        self.LineStyle   = 1
        self.LineWidth   = 1        
        self.MarkerColour= 0        
        self.MarkerStyle = 1
        self.MarkerSize  = 0.5
        self.FillStyle   = 0
        self.FillColour  = 0
        self.Scale       = 1        
        self.Sumw2       = False
        self.Normalise   = False
        self.Batch       = True
        self.RemoveDirPatternFromName = False
        self.OnlyLoadPattern = False
        self.DivideOpt   = ''
        self.LegendOpt   = ''
        self.Pattern     = None
        self.File        = None
        self._HistDict   = OrderedDict() #{}
        self._Regexp     = None
        self.XSect       = None
        self.IsData      = False
        self.NonCumul    = False
        self.Dummy       = False
        self.Original    = {}

        # Default init
        # if not sample and not kwargs:
        #     return

        # Consistency
        if sample and kwargs:
            log.error("Cannot supply both a sample class and key-word arguments")
            syd.exit(1)

        if testVerbose: print 'Sample ### passed consistency check'

        
        # Copy init (must Clone the histograms)
        if sample and isinstance(sample, Sample):
            for k, v in sample.__dict__.iteritems(): 
                if not k == '_HistDict':
                    setattr(self, k, v)
                else:
                    # Clone all histograms
                    self._HistDict = OrderedDict() #{}
                    for hkey, hval in getattr(sample, k).iteritems():
                        self._HistDict[hkey] = hval.Clone()                
            return 

        if testVerbose: print 'Sample ### overwriting explicitly set key word arguments, before kwargs.items = ', kwargs.items()
        # Overwrite attributes explicitly set
        for k, v in kwargs.items():
            setattr(self, k, v)  #equivalent to self.k = v
        if testVerbose: print 'Sample ### overwriting explicitly set key word arguments, after kwargs.items = ', kwargs.items()
            
        if testVerbose: print 'Sample ### calling _Batch()'
        # Load file and extract hists
        self._Batch()   # makes sure the hists don't all just pop up at once, i think
        TH1.AddDirectory(False);

        if testVerbose: print 'Sample ### checking file and dir() on ', self.FileName
        if not self.FileAndDir(self.FileName): return
        
        if testVerbose: print 'Sample ### setting lumi scale '
        self._SetLumiScale()

        #if not self.RemoveDirPatternFromName: 
        if testVerbose: print 'Sample ### call to extract ' # self.File was set in file and dir            
        self.Extract(self.File)
        #else:
        #    if testVerbose: print 'Sample ### call to extractHelen ' 
        #    self.ExtractHelen(self.File)
        if testVerbose: print 'Sample #### top histDict = ', self._HistDict, '\n'

        #write original contents to list so we can reset samples, don't write hist dict
        for i in self.__dict__.keys():
            if i == '_HistDict': continue
            if i == 'Original': continue
            self.Original[i] = getattr(self,i)

        #print "Original", self.Original
        return

    #def dump(self):
    #    for i in self.__dict__.keys():
    #        print i, getattr(self,i)

    def FileAndDir(self, filename):
        """
        Take filename of the form file.root:pattern, initialise TFile and compile regexp 
        based on pattern to use in selecting histograms/directories
        """
        if testVerbose : print 'Sample ### in FileAndDir, filename =',filename, 'pattern', self.Pattern
        #
        if self.Pattern and type(self.Pattern) != list : self.Pattern = [self.Pattern]
        if testVerbose : print 'Sample ### in FileAndDir, filename = ', filename, 'pattern (should be list) =', self.Pattern
        
        pattern = None
        if ':' in filename:
            nameAndDir = filename.split(':')
            filename = nameAndDir[0]
            self.Pattern  = ':'.join(nameAndDir[1:])
         
        # If file does not exist leave.  File is Non and hist list is empty
        if not os.path.exists(filename):
            if "FEWZ" in self.Label: return False
            log.warning('Constructed empty sample %s as file %s not found' % (self.Label, filename))
            return False

        log.info('Constructing sample %s from file %s' % (self.Label, filename))

        self.File = TFile(filename)

        # make an object of each string in self.Pattern, self._Regexp is now a list of these objects
        if self.Pattern:  self._Regexp = [re.compile(i) for i in self.Pattern]

        return True
    
    def Extract(self, obj, name = ''):    # obj is a TFile object, name is the folder name, set within here for looping into folders
        """
        Extract those histograms matching self._Regexp from self.File and store in OrderedDict
        """
        if testVerbose : print 'Sample ### in extract, regexp = ', self._Regexp, 'name',name,'obj',obj
        # make the pattern a list if it isn't one already
        PatternHasBeenRemoved = False
        if self.Pattern and type(self.Pattern) != list :
            tmp = self.Pattern
            self.Pattern = [tmp]

        #currently the list thing is working if there is only one element, need to get it working for multiple patterns

        # Loop over object, key is either a folder or a histogram
        for key in obj.GetListOfKeys():
            if testVerbose : print '\n','Sample ### key =', key, 'name', name, 'obj', obj
            subobj = key.ReadObj()
            subname = name + subobj.GetName()            

            PatternHist, PatternDir = False, False
            # search for pattern in folder name and set PatternDir flag to true if there is a match
            if self.Pattern:
                for i in self.Pattern:
                    if (self.RemoveDirPatternFromName or self.OnlyLoadPattern) and key.IsFolder() and (i.strip('/') in subname) : PatternDir = True
                    if PatternDir: continue

            # search for pattern in hists, if found set PatternHist to true
            if self._Regexp:
                IsSubnameInRegExp = any(REObj.search(subname) for REObj in self._Regexp)
                if self._Regexp and not key.IsFolder() and IsSubnameInRegExp: PatternHist=True

            if testVerbose : print 'Sample ### PatternDir = ', PatternDir, 'PatternHist', PatternHist 

            # If the pattern is an exact directory structure optionally remove this
            # from the name to aid plotting across sub dirs
            if PatternDir and not self.OnlyLoadPattern and self.RemoveDirPatternFromPattern:
                log.warning('not adding %s to sample %s'%(subname, self.Label))
                PatternHasBeenRemoved = True
                continue

            # If it's a folder call this function again
            if key.IsFolder():
                self.Extract(subobj, subname + '/')
                continue

            #if the pattern is a hist name optionally remove
            if PatternHist and not self.OnlyLoadPattern and self.RemoveDirPatternFromPattern:
                log.warning('not adding hist %s to sample %s'%(subname,self.Label))
                PatternHasBeenRemoved = True
                continue

            #option to only load either hist or directory if it matches pattern
            if self.OnlyLoadPattern and not PatternDir and not PatternHist:
                continue
                        
            if self.Sumw2: subobj.Sumw2()
            subobj = self._ScaleObj(subobj)

            if testVerbose :  print 'Sample ### adding %s with %s to hist Dict'%(subname,subobj)
            subobj.SetTitle(subname)
            self._HistDict[subname] = subobj

        return

    def _SetLumiScale(self):
        """
        Set scale = Sample.Lumi/(self.CutEntry()/self.XSect) * self.Scale.
        The latter allows an extra scale factor to be supplied in addition
        """

        if testVerbose: print 'Sample ### in SetLumiScale, scale = ', self.Scale, 'cutEntry = ', self.CutEntry(), 'Xsect = ', self.XSect

        # Evaluate scal if given by string
        if isinstance(self.Scale, str):
            self.Scale = eval(self.Scale)

        # Just using scale
        if self.CutEntry()==None or self.XSect==None or Sample.Lumi==None:
            if self.Scale != 1: log.info('%s: Scale = %s' % (self.Label,self.Scale))
            if testVerbose: print 'Sample ### returning 1 from setlumiscale'
            return

        if testVerbose: print 'Sample ### got here'
        sampleLumi = self.CutEntry()/self.XSect
        scale = Sample.Lumi/sampleLumi * self.Scale

        addStr = (' (inc additional = %s)' % self.Scale) if self.Scale != 1 else '' 
        log.info('%s: Events = %s, XSect = %s (fb-1), Lumi = %s (fb-1), Scale = %s %s' %
                 (self.Label, self.CutEntry(), self.XSect, sampleLumi, scale, addStr))

        self.Scale = scale

        return



    def __len__(self):
        "Return number of histograms stored in sample"
        return len(self._HistDict)

    def Clone(self):
        "Clone a sample object copying all its attributes to a new Sample"
        # args = {}
        # for member in self.__dict__: args[member] = getattr(self, member) 
        # return Sample(**args)         
        return Sample(self)        

    def _OpSetProperties(self, lhs, rhs, symbol=''):
        "Reset propoerties on the sample after the operator has been applied"

        lhs.Label     = lhs.Label + symbol + rhs.Label
        lhs.Legend    = '' # Will default to label then
        lhs.FileName  = lhs.FileName + symbol + rhs.FileName
        lhs.Scale     = 1
        return

    def __iadd__(self,rhs):
        "Add histograms in rhs to current sample"

        # Deal with samples not having hists (e.g. files not found)
        if len(rhs._HistDict)==0:   return self
        if len(self._HistDict)==0:  return rhs

        for key, obj in self._HistDict.iteritems():
            self._HistDict[key].Add(rhs._HistDict[key])
        #self._OpSetProperties(self, rhs, '+')
        return self

#    def __add__(self,rhs):
#        "Add histograms in rhs to current sample and create a new sample"
#        s = self.Clone()
#
#        # Deal with samples not having hists (e.g. files not found)
#        if len(rhs._HistDict)==0: return s
#        if len(s._HistDict)==0:   return rhs
#        
#        for key, obj in s._HistDict.iteritems():
#            s._HistDict[key].Add(rhs._HistDict[key])
#        self._OpSetProperties(s, rhs, '+')
#        return s


    def __add__(self,rhs):
        "Add histograms in rhs to current sample and create a new sample"
        s = self.Clone()

        print 'Plotter ### in add for Label = ', self.Label
        # Deal with samples not having hists (e.g. files not found)
        if len(rhs._HistDict)==0: return s
        if len(s._HistDict)==0:   return rhs

        #make copies so elements can be removed without lasting damage
        RhsHistDict = rhs._HistDict
        SHistDict   = s._HistDict

        # make a new OrderedDict that contains only the hists that are in both rhs and self and fill it with those in self
        MinHistDict = OrderedDict()
        for key, obj in SHistDict.iteritems():
            if SHistDict.has_key(key) and RhsHistDict.has_key(key): MinHistDict[key]=obj

        if testVerbose: print 'Sample ### MinHistDict = ', MinHistDict

        #now add rhs to the new ordered dict
        for key, obj in MinHistDict.iteritems():
            MinHistDict[key].Add(RhsHistDict[key])

        self._OpSetProperties(s, rhs, '+')

        #alter the hist dict of copy of self by setting it to the new hist dict created above and return it
        s._HistDict = MinHistDict
        return s

    def __isub__(self,rhs):
        "Subtract histograms in rhs from current sample"
        # Deal with samples not having hists (e.g. files not found)
        if len(rhs._HistDict)==0: return self
        if len(self._HistDict)==0:   return rhs
        
        for key, obj in self._HistDict.iteritems():
            self._HistDict[key].Add(rhs._HistDict[key], -1)
        #self._OpSetProperties(self, rhs, '-')
        return self

    def __sub__(self,rhs):
        "Subtract histograms in rhs from current sample and create a new sample"
        s = self.Clone()
        # Deal with samples not having hists (e.g. files not found)
        if len(rhs._HistDict)==0: return s
        if len(s._HistDict)==0:   return rhs
        for key, obj in s._HistDict.iteritems():
            s._HistDict[key].Add(rhs._HistDict[key], -1)
        self._OpSetProperties(s, rhs, '-')
        return s

    def DivideWithWeightedBinomialErrors(self, num, den, numScale=1., denScale=1.):
        "Divide with binomial errors and correct treatement of weighted events"
        
        eff = num.Clone();
        num.Divide(num, den, numScale, denScale, 'b')

        for i in xrange(1, num.GetNbinsX()+1):

            binEff = eff.GetBinContent(i);
            if binEff > 1: log.warning("Bin content is greater thean 1 for %s !" % eff.GetName())

            numBinContent = num.GetBinContent(i);
            denBinContent = den.GetBinContent(i);
            numBinErrorSq = num.GetBinError(i)**2
            denBinErrorSq = den.GetBinError(i)**2

            binomialError = 0
            if denBinContent == 0:
                binomialError = 0;
            else:
                binomialError = math.sqrt( (1 - 2*binEff) * numBinErrorSq + binEff*binEff * denBinErrorSq);
                binomialError /= denBinContent;

            if binEff == 0: eff.SetBinError(i, 0.);
            else:           eff.SetBinError(i, binomialError);

        return eff

    def Divide(self,num,den, numScale, denScale, opt="", name=""):
        "Divide two hists and add result to hist array"

        # Get numerator
        try:
            numHist = self.Get(num).Clone()
        except KeyError: 
            log.error("Hist %s not found" % num)
            sys.exit(100)

        # Get denomenator
        try:         
            denHist = self.Get(den)
        except:
            log.error("Hist %s not found" % num)
            sys.exit(101)

        # Create name
        if not name: name = num.split('/')[-1] + '%' + den.split('/')[-1]

        # Divide and add to plot with new name        
        if opt=='b2':
            eff = self.DivideWithWeightedBinomialErrors(numHist,denHist, numScale, denScale)
            self._HistDict[name] = eff
        else:
            eff = numHist.Clone()
            eff.Divide(numHist, denHist, numScale, denScale, opt)        
            self._HistDict[name] = eff
            
        eff.SetName(name)
        eff.SetTitle(num + ' % ' + den)
        return eff

    def __idiv__(self,rhs):
        "Divide histograms in current sample by those in rhs"

        # Deal with samples not having hists (e.g. files not found)
        if len(rhs._HistDict)==0: return self
        if len(self._HistDict)==0:   return rhs
        
        for key, obj in self._HistDict.iteritems():
            if self.DivideOpt=='b2':
                self._HistDict[key] = self.DivideWithWeightedBinomialErrors(self._HistDict[key],rhs._HistDict[key])
            else:
                self._HistDict[key].Divide(self._HistDict[key].Clone(), rhs._HistDict[key], 1., 1., self.DivideOpt)
        self._OpSetProperties(self, rhs, '_div_')
        return self

    def __div__(self,rhs):
        "Divide histograms in current sample by those in rhs and create a new sample"
        s = self.Clone()
        
        # Deal with samples not having hists (e.g. files not found)
        if len(rhs._HistDict)==0: return s
        if len(s._HistDict)==0:   return rhs

        # Should also overwriting root's error treatement
        for key, obj in s._HistDict.iteritems():
            if self.DivideOpt=='b2':
                self._HistDict[key] = self.DivideWithWeightedBinomialErrors(s._HistDict[key],rhs._HistDict[key])
            else:
                s._HistDict[key].Divide(s._HistDict[key].Clone(), rhs._HistDict[key], 1., 1., self.DivideOpt)
        self._OpSetProperties(s, rhs, '_div_')
        return s

    def __imul__(self,rhs):
        "Multiply histograms in current sample by those in rhs"

        # Deal with samples not having hists (e.g. files not found)
        if len(rhs._HistDict)==0: return self
        if len(self._HistDict)==0:   return rhs

        for key, obj in self._HistDict.iteritems():
            self._HistDict[key].Multiply(rhs._HistDict[key])
        #self._OpSetProperties(self, rhs, '*')
        return self

    def __mul__(self,rhs):
        "Multiply histograms in current sample by those in rhs and create a new sample"
        s = self.Clone()

        # Deal with samples not having hists (e.g. files not found)
        if len(rhs._HistDict)==0: return s
        if len(s._HistDict)==0:   return rhs

        for key, obj in s._HistDict.iteritems():
            s._HistDict[key].Multiply(rhs._HistDict[key])
        self._OpSetProperties(s, rhs, '*')
        return s
        
    def __str__(self):
        "Return the list of histograms in the current sample for printing"

        s = ''
        prevDepth = 0
        for k in self._HistDict: 
            s += "%s\n" % k

            # depth = k.count('/')*3
            #
            # if depth != prevDepth:
            #     s += (' ' * prevDepth + '/'.join(k.split('/')[:-1]) + '/\n')
            #
            # s += (' ' * depth + "%s\n" % k.split('/')[-1])
            # prevDepth=depth
        return s

    def __iter__(self):
        "Return iterator of underling data structure"
        return self._HistDict.iteritems()

    def next(self):
        "Return next histogram underling data structure"
        self._HistDict.iteritems().next()

    def _AddSame(self, isample):
        """
        Add "same" to plotting type for all sample except the first.
        Explicity remove 'same' for the first sample
        
        For a  graph remove plotting of axis (i.e. 'a').
        """

        self.Type    = self.Type.replace('same', '')
        self.Type2D  = self.Type2D.replace('same', '')

        if isample != 0:
            if not 'same' in self.Type:   self.Type += 'same'
            if not 'same' in self.Type2D: self.Type2D += 'same'
            self.TypeGraph = self.TypeGraph.replace('a', '')

        return

    #def GetMarkerSize(self):
    #    return self.MarkerSize

    #def SetMarkerSize(self, size):
    #    self.MarkerSize = size

    def StyleObj(self, hist, isample):
        """
        Apply style to hist object.  If parameters are not set for a sample pick 
        sensible defaults based on sample number
        """
        lineColour = isample + 1
        if lineColour > 9:
            lineColour += 20 #skips white...

        hist.SetLineColor(self.LineColour if self.LineColour else lineColour)
        hist.SetLineWidth(self.LineWidth)
        hist.SetLineStyle(self.LineStyle)
        hist.SetMarkerColor(self.MarkerColour if self.MarkerColour else lineColour)
        hist.SetMarkerSize(self.MarkerSize)
        hist.SetMarkerStyle(self.MarkerStyle)
        hist.SetFillColor(self.FillColour)
        hist.SetFillStyle(self.FillStyle)

        # Type for 1st sample is e and for remainder is histsame
        if not self.Type: self.Type = 'e' if not isample else 'hist'
        self._AddSame(isample)

        return hist

    def _ScaleObj(self, hist):
        "Scale hist object by self.Scale during extract (if not TGraph)"

        if hist.InheritsFrom('TGraph'): return hist

        hist.Scale(self.Scale)

        return hist

    def ScaleHist(self, hist, scale):
        "Function to apply arbitary user-defined scale to a particular hist"

        # Get hist by name
        if isinstance(hist, str): hist = self.Get(hist)

        if hist.InheritsFrom('TGraph'): return hist

        hist.Scale(scale)

        return hist

    def _Batch(self):
        "Run in batch mode if self.Batch == True"
        if self.Batch:
            TH1.AddDirectory(False);
            gROOT.SetBatch(True);
        return

    def GetCutHist(self, name=''):
        "Get cut flow hist called 'name' or (if not given) specified via Sample.CutHist"
        if not name: name = Sample.CutHist

        if not name:
            #print 'No cut flow histogram name supplied.  Either set the name arg or Sample.CutHists.'
            return None
        
        # Take directly from file to avoid already having been scaled
        hist = self.File.Get(name)
        
        return hist

    def CutEntry(self, name='', bin=1, scale = False):
       """
       Get number of entries from cut flow hist called 'name' or (if not given) specified via Sample.CutHist.
       By default use the 1st bin (i.e. with no cuts applied)
       """
       #         try:
       #             # Get the hist from the sample if it exists (might not if filter)
       #             hist = self[name]
       #         except KeyError:
       #             # Else get it directly from the file
       #             hist = self.File.Get(name)

       # Take directly from file to avoid already having been scaled
       hist = self.GetCutHist(name)
       if not hist: return None

       cutDict = OrderedDict()

       # make list of labels from hist 
       labels = []
       for ibin in xrange(1, hist.GetNbinsX()+1):
           labels.append(hist.GetXaxis().GetBinLabel(ibin))

       # Short cut for last bin in hist and label search
       if isinstance (bin, str):
           if bin != 'last':
  
               if not sum([(bin in label) for label in labels]):

                   log.error('could not find %s in %s' % (bin, hist))
                   sys.exit(100)
                              
               bin = [(bin in label) for label in labels].index(True) + 1
               
           else :  bin = hist.GetNbinsX()
                   
      

       return hist.GetBinContent(bin) * (self.Scale if scale else 1.)
    
    def MakeCutFlow(self, name='', scale=None):
        """
        Make a dictionary of cut names and values for a sample
        """

        #         try:
        #             # Get the hist from the sample if it exists (might not if filter)
        #             hist = self[name]
        #         except KeyError:
        #             # Else get it directly from the file
        #             hist = self.File.Get(name)

        # Default to sample-wide cut hist name if exists
        if not name: name = Sample.CutHist

        # Default to self.Scale
        if not scale: scale = self.Scale

        # Take directly from file to avoid already having been scaled
        hist = self.GetCutHist(name)
        if not hist: return None
        cutDict = OrderedDict()

        try:
            for ibin in xrange(1, hist.GetNbinsX()+1):
                cutName = hist.GetXaxis().GetBinLabel(ibin).replace('_', '\_')
                cutDict[cutName] = (hist.GetBinContent(ibin) * scale, hist.GetBinError(ibin) * scale)
            return cutDict
        except AttributeError:
            log.warning('No such histogram %s' % name)
            raise

        return

    def CutFlow(self, name='', scale=None):
        """
        Print the cut flow for a given sample
        """

        cutDict = self.MakeCutFlow(name=name, scale=scale)

        if cutDict==None: return None

        print "\\hline\\hline"
        print "%s & %s \\\\" % ("Cut".ljust(20), self.Label.center(27))
        print "\\hline\\hline"
        for k,v in cutDict.iteritems():
            print "%s & %11.2f $\\pm$ %9.2f \\\\" % (k.ljust(20), v[0], v[1])
        print "\\hline\\hline"

        return

    def Get(self, name, isample=0):
        """
        Get styled hist called 'name'
        """
        #print name, self._HistDict
        
        try:
            hist = self._HistDict[name]
        except KeyError:
            log.error("No such object %s in %s" %(name,self.Label))
            sys.exit(2)

        hist = self.StyleObj(hist, isample)
        if self.Normalise and hist.Integral(): hist.Scale(1/float(hist.Integral()))

        return hist

    def Draw(self, name=None, func=None, canvas=None):
        """
        Draw a particular histogram 'name' or set of histograms [name] to a canvas
        If a user-defined function of the form func(hist) which returns locals() is 
        given this will be called on hist before drawing
        """

        if not canvas:
            log.error("No canvas given")
            sys.exit(40)

        hist = self.Get(name)

        # User function
        if func: 
            objs = func(hist)
            utils.AttachDrawnObjsToCanvas(objs, canvas)

        # Draw hist
        if hist.InheritsFrom('TH2'):
            hist.Draw(self.Type2D)
        elif hist.InheritsFrom('TGraph'):
            hist.Draw(self.TypeGraph)
        else:
            hist.Draw(self.Type)
            pass
        
        canvas.Update()
        return canvas

    def Print(self, name=None, ext='eps', outname='', nPadsX=1, nPadsY=1, func=None):
        """
        Draw a particular histogram 'name' or set of histograms [name] to a canvas and 
        print to format given by ext. If outname is set then print to this name, else 
        construct name for sample.Label and histrogram name.  If a user-defined function 
        of the form func(hist) which returns locals() is given this will be called on hist 
        before drawing
        """

        # Short cut for lazy people
        name = [name] if isinstance(name, str) else name
        
        # Check enough pads to plot hists
        if len(name) > nPadsX*nPadsY:
            log.error("Number of requested histograms (%s) grater than number of pads (%s)" % (len(name), nPadsX*nPadsY))
            sys.exit(20)

        self._Batch()

        # Setup canvas
        canvas = TCanvas(self.Label + "Canvas", self.Label + "Canvas", 700, 500)
        canvas.SetFrameFillColor(10)
        canvas.SetFillColor(10)
        canvas.Divide(nPadsX,nPadsY)

        # Get hist
        for i,n in enumerate(name):
            canvas.cd(i+1)
            self.Draw(name=n, func=func, canvas=canvas)

        # print canvas
        if not outname: 
            # Use sample and hist name if only one hist requested else just sample name
            if len(name)==1:
                outname = self.Label + '.' + name[0].replace('/', '.').replace(' ', '_')
            else:
                outname = self.Label + '.Plots' 

        outname += ('.' + ext.lower().strip('.'))
        canvas.Print(outname)
        return

    def Write(self, prefix='', name=None, update=False):
        """
        Write out all (modified) hists, or those in name if given, to a new root file
        """
              
        # Short cut for lazy people
        name = [name] if isinstance(name, str) else name

        if not prefix: outfile = self.Label+'.root'
        else:          outfile = prefix.replace('.root', '') + '.root'

        f = TFile(outfile, 'RECREATE') if not update else TFile(outfile, "UPDATE")

        # Special case for passing a hist in (bit of a hack)
        if isinstance(name, TH1):
           name.Write()
           return

        
        for key, hist in self._HistDict.iteritems():
            if name and not key in name: continue

            # Make dirs (last part is hist name)
            for d in key.split('/')[:-1]:                                                
                if not f.GetKey(d): f.mkdir(d)
                f.cd(d)

            hist.Write()

        f.Close()
        return

    def __getitem__(self, key):
        "Return histogram by key"
        try:
            return self._HistDict[key]
        except KeyError:
            raise

    def __contains__(self, name):
        "Does sample contain a paticular hist"
        return name in self._HistDict

    def __getattr__(self, name):
        """                                                                                                                                          
        If a method doesn't exist in Sample instance or class, take the first argument as a hist name                                                
        and attempt to forward the method to that with the remaining arguments. E.g.                                                                 
                                                                                                                                                     
        s.Integral('hist', 0, 10) -> s.Get('hist').Integral(0,10)                                                                                    
        """
        # __getattr__ is only called if method not found in instance or class                                                                        

        def wrapper(*args):
            # Make sure valid for forwarding (i.e. at least two args where second is str identifing a valid hist)                                    
            if len(args) < 2 or not isinstance(args[1], str) or not (args[1] in args[0]):
                raise AttributeError('Sample object has no method %s' % name)

            # Extract sample and hist name from args                                                                                                 
            sample   = args[0]
            histName = args[1]
            args     = args[2:]

            # Get hist from sample                                                                                                                   
            hist = sample.Get(histName)

            # Call method 'name' on hist with remaining args (unpacked)                                                                              
            try:
                return getattr(hist,name)(*args)
            except AttributeError:
                raise AttributeError('Sample object has no method %s and unable to forward to %s' % (name, repr(hist)))

            return

        # Return function with sample arg already implemented                                                                                        
        from functools import partial
        return partial(wrapper,self)

    def __setattr__(self, name, value):
        "Deal with special cases of setting arguments"

        if name == 'OutputLevel':
            # Forward output level to logging class
            object.__setattr__(self, name, value)
            log.setLevel(value)
        elif name == 'IsData':            
            # Automatically non-cumulative if data
            object.__setattr__(self, name, value)            
            self.NonCumul = value
        else:
            object.__setattr__(self, name, value)

        return

    pass
