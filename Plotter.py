import math, re, sys

from Sample     import Sample
from Logging    import log, INFO
import Utils as utils
from odict      import OrderedDict
from TexOrPlain import TexOrPlain

#from ROOT import gROOT, gStyle, gPad, gDirectory
#from ROOT import TFile, TCanvas, TPostScript, TH1, TLegend, TPad, TF1 
#from ROOT import TKey, TObject, TLine, TLatex, TGraph, TGraphAsymmErrors, TBox
#from ROOT import TLimit, TConfidenceLevel, TLimitDataSource, TObjArray, TVectorD, TMath, TObjString
#from ROOT import SetOwnership
#from ROOT import kMagenta

from ROOT import *

import array
#from config import fitCB
                        

__author__  = 'Carl Gwilliam'
__version__ = '0.5'

testVerbose = False

# TODO
# Use PsCanvas (should inherit from TCanvas)?

class Plotter(object):
    """
    Class to plot all plots, or a subset sepcified by a regexp, for a set of \"Samples\"
    into a postscript file.  Plotter is iterable (iterating over the stored Samples)

    Example:

    p = Plotter([s1, s2], NPadsX=3, NPadsY=3, OutputPrefix='MyPlots')
    p.Plot()

    """
    
    def __init__(self, samples = [], **kwargs):
        """
        Initalise Plotter object
        """
        if testVerbose: print 'Plotter ### in __init__'
        # Shortcut for lazy people 
        self.Samples = [samples] if isinstance(samples, Sample) else samples

        self.OutputLevel           = INFO
        self.OutputPrefix          = 'Plots'
        self.NPadsX                = 2
        self.NPadsY                = 2
        self.NPadsPerPage          = self.NPadsX*self.NPadsY
        self.PlotLegendOncePerPage = True
        self.PlotLegend            = True
        self.Landscape             = True

        self.Cumulative            = False
        self.CumulOrder            = []
        self.AutoOrderCumul             = []
        self.Normalise             = False
        self.Rebinning             = {}
        self.PrintBin              = {}
        self.MinMax                = {}
        self.XRange                = {}
        self.YRange                = {}
        self.MaxLeeway             = 0.1
        self.ScaleToHist           = ''

        self.OptTitle              = True 
        self.OptStat               = "emrou"  #https://root.cern.ch/root/html/TStyle.html#TStyle:SetOptStat
        self._LogXPattern          = None
        self._LogYPattern          = None
        self._LogZPattern          = None
        self.LeftMargin            = None
        self.RightMargin           = None
        self.TopMargin             = None
        self.BottomMargin          = None
        #self.Canvas                = None

        self.LegendCoords          = [0.55, 0.3, 0.8, 0.4]
        self.rP           = {}
        self.Batch                 = True  

        # Overwrite attributes explicitly set
        for k, v in kwargs.items():
            setattr(self, k, v)

        # Check samples are consistent and valid (file exists)
        self._CheckSamples()

        # Add same to type (deprecated as now done in sample, but should a sample know about this?)
        #self._AddSame()
        log.verbose("Test")

        # Initialise
        if self.Batch: self._Batch()
        self.InitCanvas()
        self.InitPS()
        self.InitLegend(self.LegendCoords)        
        pass

    def InitLegend(self, coords):
        "Initalise legend"
        x1=coords[0]
        y1=coords[1]
        x2=coords[2]
        y2=coords[3]
        self.Legend = TLegend(x1, y1, x2, y2)
        self.Legend.SetFillStyle(0)
        self.Legend.SetBorderSize(0)
        #self.Legend.SetMarkerSize(0.06)
        #self.Legend.SetTextAlign(23)
        #self.Legend.SetTextSize(0.06)
        return

    def InitCanvas(self, width=None, height=None):
        "Initilaise canvas"

        # Set width and height depending on landscape/portrait unless user-defined
        if not width and not height:
            if self.Landscape:
                width  = 800; height = 600
            else:
                width  = 600; height = 800
                #width  = 900; height = 1200

        # Delete canvas if already exists
        if 'Canvas' in dir(self): del self.Canvas
        #a = getattr(self,'Canvas')
         #   del a
        
        # Create canvas
        self.Canvas =  TCanvas("canvas", "canvas", width, height)
        self.Canvas.SetFillColor(10)
        self.Canvas.SetFrameFillColor(10)
        self.Canvas.Divide(self.NPadsX,self.NPadsY)
        #pad = (TPad)
        #print "TWAT", self.Canvas.GetPad(0).SetBottomMargin(1.9)
        
        
        self.Canvas.Hists = []     # To allow passing reference to hists to canvas to avoid python garbage collecting
        self.Canvas.DrawnObjs = [] # To allow passing reference to other objs to canvas to avoid python garbage collecting
        return    

    def InitPS(self, mode = None):
        "Initilaise PostScript file"
        
        # Delete ps file if already exists
        if 'PostScript' in dir(self): del self.PostScript

        if not mode:
            mode = 112 if self.Landscape else 111            
        self.PostScript = TPostScript(self.OutputPrefix + '.ps',mode)
        return

    def SetLogY(self, pattern):
        "Set log y axis for those hists matching pattern" 
        self._LogYPattern = re.compile(pattern)
        return

    def SetLogZ(self, pattern):
        "Set log z axis for those hists matching pattern" 
        self._LogZPattern = re.compile(pattern)
        return 

    def SetLogX(self, pattern):
        "Set log x axis for those hists matching pattern" 
        self._LogXPattern = re.compile(pattern)
        return
    def _PrintCutFlow(self, hist, name):
        
        "Print Bin content"
        if not self.PrintBin: return
        if name in self.PrintBin:


            nb  = hist.GetNbinsX()
        
            for bin in range(0, nb): print "Histogram ",name,"Bin ", bin, " : ", hist.GetBinContent(bin), " +/- ", hist.GetBinError(bin)
        return

    def _Rebin(self, hist, name, rebin=None):
        "Rebin the histograms using args or else self.Rebinning"
            
        if rebin==None:
            # Get overall rebinning if not given as arg
            if not self.Rebinning or not self.Rebinning.has_key(name): return
            rebin = self.Rebinning[name]

        if self._NotImplForGraphs(hist, 'Rebinning'): return 

        # Rationalise rebinning
        nb  = hist.GetNbinsX()
        while (nb%rebin > 0):rebin += 1
        hist.Rebin(rebin)

        return

    def _SetMinMax(self, hist, name, histmax, hmin=None, hmax=None):
        """
        Set hist min and max to user defined values based on args or self.MinMax.  If none given then set 
        maximum to max value of that histogram over all samples
        """

        # Return if histmax not set
        if histmax==None: return

        if self._NotImplForGraphs(hist, 'Min/Max'): return

        # Default max to max value of that histogram over all samples
        hist.SetMaximum(histmax)            

        # User defined min/max. Set to None to not apply (but in this case must apply default max) ...

        # If argument not given use values from self.MinMax, if given
        if self.MinMax and self.MinMax.has_key(name):
            hlimits = self.MinMax[name]
            if hmin == None: hmin = hlimits[0]
            if hmax == None: hmax = hlimits[1] 

        # Leave if neither min/max specified
        if hmin == hmax == None: return  

        # Apply min/max
        if (hmin != None): hist.SetMinimum(hmin)
        if (hmax != None): hist.SetMaximum(hmax)

        return

    def _SetXRange(self, hist, name, xmin = None, xmax = None):
        """
        Set min and max for x axis from args or else self.XRange
        """
        # Take from args if exist or else member
        if xmin == None or xmax == None: 
            if self.XRange and self.XRange.has_key(name): 
                hmin,hmax = self.XRange[name]
                if xmin == None: xmin = hmin
                if xmax == None: xmax = hmax

        # Leave if nothing to do
        if xmin == xmax == None: return

        if xmin == None: xmin = hist.GetXaxis().GetXmin()
        if xmax == None: xmax = hist.GetXaxis().GetXmax()
        hist.SetAxisRange(xmin, xmax, "X")
       # hist.GetXaxis().SetLimits(xmin, xmax)
        return

    def _SetYRange(self, hist, name, ymin = None, ymax = None):
        """
        Set min and max for y axis from args or else self.YRange
        """
        # Take from args if exist or else member
        if ymin == None or ymax == None: 
            if self.YRange and self.YRange.has_key(name): 
                hmin,hmax = self.YRange[name]
                if ymin == None: ymin = hmin
                if ymax == None: ymax = hmax

        # Leave if nothing to do
        if ymin == ymax == None: return

        if ymin == None: ymin = hist.GetYaxis().GetXmin()
        if ymax == None: ymax = hist.GetYaxis().GetXmax()

        #hist.SetAxisRange(ymin, ymax, "Y")
        #hist.GetYaxis().SetLimits(ymin, ymax)
        #hist.SetMaximum(ymax)
        #hist.SetMinimum(ymin)

        hist.GetYaxis().SetRangeUser(ymin,ymax)

        #if xmin: hist.GetYaxis().SetRange(25, 75)#hist.GetXaxis().SetLimits(float(xmin), float(xmax))
        return


    def _Norm(self, hist, norm=None):
        "Normalise hist to unit area based on arg or else self.Normalise"

        # Take from args if exist or else member
        if norm == None:
            norm = self.Normalise

        # Leave if nothing to do
        if not norm: return 

        if self._NotImplForGraphs(hist, 'Normalisation'): return

        if hist.Integral(): hist.Scale(1/float(hist.Integral()))
        return

#     def _AddSame(self):
#         """
#         Add "same" to plotting type for all sample except the first.
#         Explicity remove 'same' for the first sample
#         
#         For a  graph remove plotting of axis (i.e. 'a').
#         """
# 
#         self.Samples[0].Type    = self.Samples[0].Type.replace('same', '')
#         self.Samples[0].Type2D  = self.Samples[0].Type2D.replace('same', '')
# 
#         for s in self.Samples[1:]:
#             if not 'same' in s.Type:   s.Type += 'same'
#             if not 'same' in s.Type2D: s.Type2D += 'same'
#             s.TypeGraph = s.TypeGraph.replace('a', '')
# 
#         return

    def _CheckSamples(self):
        "Check there is at least one sample and they have the same size"

        # Must be at least one sample
        if not self.Samples:
            log.error("No samples defined. Exiting!")
            sys.exit(1)


        # Samples must be valid (file exits + some hists) and have the same size
        for i,s in enumerate(self.Samples):

            if s.File == None or len(s) == 0:
                if s.Dummy and len(s) > 0 : continue
                
                log.warning('* Skipping sample %s' % s.Label)
                self.Samples.remove(s)
                continue

            #if i != 0 and len(s) != len(self.Samples[0]):
            #    log.error("Samples have different lenghts.  Exiting")

            #    sys.exit(2)

        log.info('Constructed Plotter with %s samples:' % len(self.Samples))
        log.info(', '.join([s.Label for s in self.Samples]))
        return

    def _CheckBins(self, hist, nbins, sample):
        "Check histogrm has the same number of bins for all samples"

        nb = hist.GetN() if hist.InheritsFrom('TGraph') else hist.GetSize()

        if nb != nbins:
            log.warning("Histogram %s has different number of bins in %s sample: %s vs %s. Skipping" % (hist.GetName(), sample.Label, nb, nbins))
            #sys.exit(3)
            return False
        return True 

    def _Batch(self):
        "Plot in batch mode if self.Batch == True"

        if self.Batch: 
            TH1.AddDirectory(False);
            gROOT.SetBatch(True);
        return

    def GetSamples(self, include=[]):
        """
        
        """

        if not include:
            return self.Samples

        filteredSample = [s for s in self.Samples if s.Label in include]

        if not len(filteredSamples):
            log.warning("No samples selected after filtering.  Ignoring filtering")
            return self.Samples

        # if the first sample is not plotted this will invalidate the AddSame.
        # This should instead be done on-the-fly
        #self._AddSame()

        return filteredSamples

    def SumSamples(self, sampleNames = [], label = 'Sum'):
        """
        Sum the samples whos names are provided and create a new Sample named
        'label' and add it to the plotter
        """
        
        # Need to be able to 'get' sample so can modify plotting properties

        if not sampleNames: 
            log.error("No sample names given.  Exiting")
            sys.exit(4)

        isample=0
        for s in self.Samples:
            if not s.Label in sampleNames: continue

            if not isample:
                # Clone first sample in list
                sum = Sample(s)  
                sum.Label = label
            else:
                # Add all other samples
                sum += s
                
            isample += 1

        # Add summed sample to list
        self.Samples.append(sum)
        self._AddSame()

        return

    def _NormToHist(self, hist, sample, name):
        """
        Normalise histograms by area based on self.ScaleToHist.  This takes the genral form
        'sample1/hist1%sample2:hist2', where only sample1 is required, and then scales all
        hisograms except those in sample1 by the result.  Allowed forms and how the scale is
        calculated are:

        'sample1':
                   Each hist in every other sample is scaled by the ratio of its integral
                   in the current sample to that of the corresponding hist in sample1

        'sample1:hist1':
                   Each hist in every other sample is scaled by the ratio of the integral
                   of hist1 int he current sample to that of hist1 in sample1

        'sample1%sample2':
                   Each hist in every sample other than sample1 is scaled by the ratio of
                   its integral in sample2 to that of the corresponding hist in sample1

        'sample1:hist1%sample2:hist2':
                   Each hist in every sample other than sample1 is scaled by the ratio of
                   the integral of hist1 in sample2 to that of hist1 in sample1                 
        
        """

        if not self.ScaleToHist: return

        # Decode sample/hist names ...

        # Set num (and optionally den) strings
        try:
            num,den = self.ScaleToHist.split('%')
        except:
            num = self.ScaleToHist
            den = ''

        # Set num samples and hist name.  If hist is not present use current hise
        try:
            numSample, numName = num.split(':')
        except ValueError:
            numSample = num
            numName   = name

        if den:
            # Set den samples and hist name.  If hist is not present use current hise
            try:
                denSample, denName = den.split(':')
            except ValueError:
                denSample = den
                denName   = name
        else:
            # If no den was given use the current sample and the same name as the num
            denSample = sample.Label
            denName   = numName

        # Calculate result and scale
        numHist = self[numSample][numName]
        denHist = self[denSample][denName]                

        if not sample.Label == numSample and denHist.GetSumOfWeights():            
            hist.Scale(numHist.GetSumOfWeights()/float(denHist.GetSumOfWeights()))

        return

    def _LogX(self, name, logx=None):
        "Log X axis depending on args or self.LogXPattern"
        if logx == None: 
            logx = True if (self._LogXPattern and self._LogXPattern.search(name)) else False
        gPad.SetLogx(logx)
        return

    def _Margins(self):
        "Set pad margins"

        if self.LeftMargin:   gPad.SetLeftMargin(self.LeftMargin)
        if self.RightMargin:  gPad.SetRightMargin(self.RightMargin)
        if self.TopMargin:    gPad.SetTopMargin(self.TopMargin)
        if self.BottomMargin: gPad.SetBottomMargin(self.BottomMargin)

        return

    def _LogY(self, name, logy=None):
        "Log Y axis depending on args or self.LogYPattern"
        if logy == None: 
            logy = True if (self._LogYPattern and self._LogYPattern.search(name)) else False
        gPad.SetLogy(logy)
        return

    def _Cumulative(self, cumul=None):
        "Plots hists cumulative based on args or self.Cumulative"
        if cumul == None: cumul = self.Cumulative
        return cumul

    def _AutoOrderCumul(self, AutoOrderCumul=None):
        "orders samples according to their hihjest entry"
        if AutoOrderCumul == None: AutoOrderCumul = self.AutoOrderCumul
        return AutoOrderCumul

    def Plot(self, name = '', veto = '', func=None):
        """
        Plot the histograms.  If no 'name' is given plot all the histograms in the sample, otherwise
        treat 'name' as a regexp to limit the histograms to be plotted.  If a user-defined function of 
        the form func(hist) which returns locals() is given this will be called on hist before drawing 
        """

        self._Batch()
        
        # Canvas 
        #canvas =  TCanvas("canvas", "canvas", 700, 500)
        #canvas.SetFillColor(10)
        #canvas.SetFrameFillColor(10)
        #self.InitCanvas()
        if self.Canvas:
            self.Canvas.Divide(self.NPadsX,self.NPadsY)        
        self.NPadsPerPage = self.NPadsX*self.NPadsY  # Recompute in case changed since init

        # PostScript
        #filename = self.OutputPrefix + '.' + name.replace('/', '.').rstrip('.') + '.ps'
        #filename = self.OutputPrefix + '.ps'
        #postScript = TPostScript(filename,111)
        self.InitPS()  # Need to be done here to respect changes to output prefix but then won't respect user changes
        self.PostScript.NewPage()

        # Pattern
        pattern = None
        if name: pattern = re.compile(name)

        # Veto pattern
        vpattern = None
        if veto: vpattern = re.compile(veto)

        # Loop over histograms
        iPad = 1
        #histClones = []
        for histname, _ in self.Samples[0]:
            
            # Plot only certain hists depending on pattern or veto pattern
            if pattern and not pattern.search(histname): continue
            if vpattern and vpattern.search(histname): continue

            # Change page if have alread filled pads
            if iPad == (self.NPadsPerPage+1):
                self.Canvas.Update()
                self.PostScript.NewPage()
                iPad=1
                if self.Canvas:
                    self.Canvas.Clear()
                    self.Canvas.Divide(self.NPadsX,self.NPadsY)
                pass

            # Plot (need to check same number of bins)
            if self.Canvas:
                self.Canvas.cd(iPad)      

            # keep ref to histClones to prevent python cleaning up before drawn
            #histClones.append(self._PlotHist(histname, func=func))
            self._PlotHist(histname, func=func)

            # Draw legend
            if self.PlotLegend and (iPad==1 or not self.PlotLegendOncePerPage):
                self.Legend.Draw()

            iPad+=1
            pass
        
        # Finalise canvas and postscript
        if self.Canvas:
            self.Canvas.Update()
        self.PostScript.NewPage()
        self.PostScript.Close()
        return

    def _OrderCumul(self, name, AutoOrderCumul):
        "given a list of hists, it orders them in terms of the highest y axis entry"
        if not AutoOrderCumul: return []
        b = []
        tmp =[]
        
        
        if not self.AutoOrderCumul: self.AutoOrderCumul = self.Samples
        
        for i,s in enumerate(self.AutoOrderCumul):
            if isinstance(s, str):s = self[s]
            hist = s.Get(name, i).Clone()
            a = hist.GetMaximum()
            tmp.append(a)
            tmp.sort()
           # print tmp.index(a)
            b.insert(tmp.index(a),s)
           # print b
        
        #b = str(a)
        return b
        
    def _MakeCumul(self, name, cumul):
        if not cumul: return {}, None

        histmax    = None
        sumhist    = None
        cumulHists = {}


        if not self.CumulOrder: self.CumulOrder = self.Samples
      
       # if self.AutoOrder:
       #     for i,s in enumerate(self.AutoOrder)
        for i,s in enumerate(self.CumulOrder):
            
            if s.NonCumul: continue
            
            # Convert name to Sample instance and get hist
            if isinstance(s, str): s = self[s]                
            hist = s.Get(name, i).Clone()

            # Maximum
            currentHmax= hist.GetMaximum()
            if histmax==None: histmax = currentHmax
            else:             histmax += currentHmax

            if sumhist==None:
                sumhist = hist.Clone()
                cumulHists[s.Label] = hist
                #print s.Label, hist[13]
            else:
                hist.Add(sumhist)
                sumhist = hist.Clone()
                cumulHists[s.Label] = hist 
                #print s.Label, hist[13]

        return cumulHists, histmax

    
    def _PlotHist(self,name='', xtitle=None, ytitle=None, logx=None, logy=None, xmin=None, xmax=None, ymin=None, ymax=None, 
                  hmin=None, hmax=None, rebin=None, norm=None, AutoOrderCumul=None, cumul = None, func=None, ratio=None, noXAxis=None, absol=None, fit=None, band=None):
        """
        Plot a single histogram for all samples again allowing a user-defind function func(hist)
        """
        gStyle.SetOptStat(self.OptStat)
        gStyle.SetOptTitle(self.OptTitle)
        gStyle.SetPalette(1)

        self.Legend.Clear()            

        firstHist  = None
        histmax    = None
        datamax    = None

        if AutoOrderCumul:
            OrderedList = self._OrderCumul(name, AutoOrderCumul)
            cumul = self._Cumulative(OrderedList.reverse())
            cumulHists, histmax = self._MakeCumul(name, OrderedList.reverse())

        # Cumulative histograms in order given by self.CumulOrder
        else:
            cumul = self._Cumulative(cumul)
            cumulHists, histmax = self._MakeCumul(name, cumul)

        ratioList = []

        for i,s in enumerate(self.Samples):
            # Clone so original not changed if want to draw multiple time
            # (keep ref to clone in canvas to prevent python cleaning up before drawn)
            
            if cumul and not s.NonCumul:
                hist = cumulHists[s.Label]
                s.StyleObj(hist, i)  # Needed to get same
            else:
                hist = s.Get(name, i).Clone()

            if absol:
                from config import absolute
                nameOrig = name
                hist = absolute(s.Get(name,i))

            self.Canvas.Hists.append(hist)
            if not i: firstHist = hist
            #print "TEST", i, self.Canvas.Hists

            # Check number of bins are consistent, else skip hist for that sample
            if not i: nbins = hist.GetN() if hist.InheritsFrom('TGraph') else hist.GetSize()
            else:
                if not self._CheckBins(hist, nbins, s): return histClones #sys.exit(3)

            # Rebinning (must do  before set max)
            self._Rebin(hist, name, rebin) 

            # Normalise (must do  before set max)
            self._Norm(hist, norm)

            # Norm by hist area (must do  before set max)
            self._NormToHist(hist, s, name)

            # Minimum/Maximum (need to set the *first* hist to get it to update)
            if not cumul:
                currentHmax= hist.GetMaximum()
                if currentHmax > histmax: histmax = currentHmax
            
            # Min/Max
            #self._SetMinMax(firstHist, name, histmax*(1 + self.MaxLeeway), hmin, hmax)  # Should protect against histmax not being set
            
            # Legend
            if self.PlotLegend:
                #self.Legend.SetEntrySeparation(0.05)
                entry = s.Label if not s.Legend else s.Legend
                #print "separation", self.Legend.GetEntrySeparation()
                #self.Legend.AddEntry(hist,entry, self._LegendMarker(s))
                #hist.SetMarkerStyle(34)
                #entry = "hhh"
                #s.MarkerSize = 0.05
                #print "mareker style for ", s.Label, self._LegendMarker(s), "length", len(self.Samples), "type", s.Type
                self.Legend.AddEntry(hist,entry, self._LegendMarker(s))

                #this is a hack because for some reason when there is just one entry the marker size on the legend is massive...
                #if len(self.Samples) == 1:  self.Legend.AddEntry(hist," ", " ")
                #self.Legend.AddEntry(hist,entry, "f")
                    
            # Margin
            #gPad.SetRightMargin(0.15)
            
            # Axis ranges, only do for first hist

            if not i:
                self._SetXRange(hist, name, xmin, xmax)
                self._SetYRange(hist, name, ymin, ymax)

            # Log scales
            self._LogX(name, logx)
            self._LogY(name, logy)
            if self._LogZPattern and self._LogZPattern.search(name): gPad.SetLogz(True)
            
            # margins
            self._Margins()
            
            # Titles
            if xtitle and ytitle:
                #print "title x offeset", hist.GetXaxis().GetTitleOffset(), "\n"
                tmpx = hist.GetXaxis().GetTitleSize()
                tmpy = hist.GetYaxis().GetTitleSize()
                hist.GetXaxis().SetTitleSize(1.45 * tmpx);
                hist.GetYaxis().SetTitleSize(1.45 * tmpy);
                hist.GetXaxis().SetTitleOffset(0.8)

            if xtitle: hist.SetXTitle(xtitle)
            if ytitle: hist.SetYTitle(ytitle)
            
            # User function
            if func:  
                objs = func(hist)
                utils.AttachDrawnObjsToCanvas(objs, self.Canvas)
            
            if ratio:
                #hist.GetXaxis().SetLabelOffset(999)
                ratioList.append(hist)
                continue
                            
            if noXAxis:
                hist.GetXaxis().SetLabelOffset(999)
            
            # Draw histogram
            if hist.InheritsFrom('TH2'):
                hist.Draw(s.Type2D)
            elif hist.InheritsFrom('TGraph'):
                hist.Draw(s.TypeGraph)
            else:

                if band:
                    # draw up and down shifted hists as band
                    # add the stat error also, point will be drawn indicating statistical error
                    uphist = s.Get(name+"pdfup", i).Clone()
                    dohist = s.Get(name+"pdfdo", i).Clone()
                    
                    numbins = hist.GetXaxis().GetNbins()
                    
                    x =[]
                    xdo = []
                    xup = []
                    nom = []
                    sysup = []
                    sysdo = []
                    statup = []
                    statdo = []
                    statsysup = []
                    statsysdo = []
                    
                    
                    for i in range(1,numbins+1):
                        #print "nom", hist.GetBinContent(i), "up", uphist.GetBinContent(i), "do", dohist.GetBinContent(i)
                        x.append(hist.GetBinCenter(i))
                        xdo.append( abs(hist.GetBinLowEdge(i) - hist.GetBinCenter(i)) )
                        xup.append( abs(hist.GetXaxis().GetBinUpEdge(i) - hist.GetBinCenter(i)) )
                        #xdo.append(0.5)
                        #xup.append(0.5)
                        nom.append(hist.GetBinContent(i))
                        statup.append(hist.GetBinError(i))
                        statdo.append(hist.GetBinError(i))
                        #sysup.append(0.1)
                        #sysdo.append(0.1)
                        sysup.append( abs(uphist.GetBinContent(i) - hist.GetBinContent(i)) )
                        sysdo.append( abs(dohist.GetBinContent(i) - hist.GetBinContent(i)) )
                        #print "uphist", uphist.GetBinContent(i), "dohist", dohist.GetBinContent(i), "nom", hist.GetBinContent(i), "diff do", abs(hist.GetBinContent(i) - dohist.GetBinContent(i))
                    
                    addStatError = True
                    if addStatError:
                        for i in range(1, numbins+1):
                            statsysup.append(sysup[i-1] + hist.GetBinError(i))
                            statsysdo.append(sysdo[i-1] + hist.GetBinError(i))
                    
                    #hist.Draw("hist")
                    #print "nom", nom[10]
                    #print "sysup", sysup[10]
                    #print "sysdo", sysdo[10]
                    
                    sysgraph = TGraphAsymmErrors(numbins, array.array("f",x), array.array("f",nom), array.array("f",xdo), array.array("f",xup), array.array("f",sysdo), array.array("f",sysup))
                    statgraph = TGraphAsymmErrors(numbins, array.array("f",x), array.array("f",nom), array.array("f",xdo), array.array("f",xup), array.array("f",statdo), array.array("f",statup))
                    statsysgraph = TGraphAsymmErrors(numbins, array.array("f",x), array.array("f",nom), array.array("f",xdo), array.array("f",xup), array.array("f",statsysdo), array.array("f",statsysup))
                    lc = hist.GetLineColor()
                    sysgraph.SetFillColor(kRed)
                    sysgraph.SetFillStyle(3002)
                    statgraph.SetFillColor(kBlue)
                    statsysgraph.SetFillColor(lc+30)
                    statsysgraph.SetFillStyle(3002)
                    hist.Draw(s.Type)  #draw this first so that the range isn't altered
                    statsysgraph.Draw("2 same")
                    #statgraph.Draw("2 same")
                    #sysgraph.Draw("2 same")
                    #hist.Draw(s.Type +" same")
                    hist.Draw("p same")
                    SetOwnership(sysgraph,False)
                    SetOwnership(statgraph,False)
                    SetOwnership(statsysgraph,False)
                    
                else:
                    hist.Draw(s.Type)
                    
                if fit:
                    
                    Gaussian = "GAUSS" in fit
                    CB = "CB" in fit
                    dG = "dG" in fit
                    LCBG = "LCBG" in fit
                    doubleCB = "dCB" in fit
                    cbonly = "cbonly" in fit
                    dcbactual = "dcbActual" in fit
                    freeMean = "dcbFreeMean" in fit
                    expo = "exp" in fit
                    gaussExp = "gaussExp" in fit
                    quad = "quad" in fit
                    asymm_quad = "asymm" in fit

                    if not Gaussian and not CB and not dG and not LCBG and not doubleCB and not dcbactual and not expo and not freeMean and not gaussExp and not quad and not asymm_quad and not cbonly:
                        print "no option set for fit, defaulting to gaussian"

                    if dG:
                        gfit = TF1("Gaussian","gaus",fit[0],fit[1])
                        hist.Fit(gfit,"RQN")
                        height1, centre1, width1 = gfit.GetParameter(0), gfit.GetParameter(1), gfit.GetParameter(2)
                        
                        from config import doubleGauss as dg
                        dgFit = TF1("dg",dg, fit[0], fit[1], 5)
                        height2 = height1 / 3
                        width2 = width1*2
                        dgFit.SetParameters(height1, centre1, width1, height2, centre1, width2)
                        hist.Fit(dgFit,"RQN")

                        height1, centre1, width1, height2, width2 = dgFit.GetParameter(0), dgFit.GetParameter(1), dgFit.GetParameter(2), dgFit.GetParameter(3), dgFit.GetParameter(4)
                        a = hist.GetLineColor()
                        
                        #g1 = TF1("gauss", "[0] / sqrt(2.0 * TMath::Pi()) / [2] * exp(-(x-[1])*(x-[1])/2./[2]/[2])", fit[0], fit[1])
                        from config import gauss
                        g1 = TF1("gauss", gauss, fit[0], fit[1], 3)
                        g1.SetParameters(height1, centre1, width1)
                        g1.FixParameter(0, height1)
                        g1.FixParameter(1, centre1)
                        g1.FixParameter(2, width1)
                        hist.Fit(g1,"RQN")
                        g1.SetLineColor(2)
                        g1.Draw("SAME")
                        
                        g2 = TF1("gauss", gauss, fit[0], fit[1], 3)
                        g2.SetParameters(height2, centre1, width2)
                        g2.FixParameter(0, height2)
                        g2.FixParameter(1, centre1)
                        g2.FixParameter(2, width2)
                        hist.Fit(g2,"RQN")
                        g2.SetLineColor(4)
                        g2.Draw("SAME")

                        #g2 = TF1("gauss", "[0] / sqrt(2.0 * TMath::Pi()) / [2] * exp(-(x-[1])*(x-[1])/2./[2]/[2])", fit[0], fit[1])
                        dgFit.SetLineColor(a)
                        dgFit.Draw("SAME")

                        print "FIT: sample", s.Label, "height1", height1, "width1", width1 , "height2", height2, "width2", width2, "centre", centre1

                        if "BOX" in fit:
                            size = 0.04
                            x = 0.65
                            y = 0.65
                            
                            LTX = TLatex()
                            LTX.SetNDC(1)
                            LTX.SetTextSize(size)
                            text1 = "mean:{mean:.5f}".format(mean=centre1)
                            LTX.DrawLatex(x,y,text1)

                    if Gaussian:
                        gfit = TF1("Gaussian","gaus",fit[0],fit[1])
                        h = hist.GetMaximum()
                        hist.Fit(gfit,"RQN")
                        height, centre, width = gfit.GetParameter(0), gfit.GetParameter(1), gfit.GetParameter(2)
                        #print "FIT: sample", s.Label, "gfit height", height, "centre", centre, "width", width
                        a = hist.GetLineColor()
                        gfit.SetLineColor(a+1)
                        gfit.Draw("SAME")

                        for i in fit:
                            if type(i)==type({}):
                                i["width"] = width
                                i["centre"] = centre
                        
                        if "BOX" in fit:
                            size = 0.04
                            x = 0.65
                            y = 0.65
                            
                            LTX = TLatex()
                            LTX.SetNDC(1)
                            LTX.SetTextSize(size)
                            text1 = "centre:{centre:.5f}".format(centre=centre)
                            text2 = "width:{width:.5f}".format(width=width)
                            LTX.DrawLatex(x,y,text1)
                            LTX.DrawLatex(x,y*(0.95),text2)
                            

                    if CB:
                        from config import fitCB
                        #from config import fCB

                        #histHalfInt = hist.Integral() / 2.0
                        height_guess = hist.GetMaximum()
                        mean_guess = 91.2 if fit[0] < 10000 else 91200.0
                        width_guess = 3.0 if fit[0] < 10000 else 3000.0
                        
                        myCB = TF1("fitCB", fitCB , fit[0] , fit[1] , 7)
                        myCB.SetParName(0, "norm"   )
                        myCB.SetParName(1, "alpha"  )
                        myCB.SetParName(2, "n"      )
                        myCB.SetParName(3, "mean"   )
                        myCB.SetParName(4, "sigma"  )
                        myCB.SetParName(5, "c"      )
                        myCB.SetParName(6, "slope"  )
                        myCB.FixParameter(2, 1)
                        #norm and sigma taken from MC gaussian fit (between 87000 and 95000), mean is PDG Z mass value
                        myCB.FixParameter(1, 1.1) # this is always fixed...
                        myCB.FixParameter(5, 0.0) # this is always fixed...
                        myCB.FixParameter(6, 0.0) # this is always fixed...
                        myCB.SetParameters(height_guess, 1.1, 1.0, mean_guess, width_guess, 0.0, 0.0 )

                        hist.Fit(myCB,"RQN")
                        norm1, alpha1, n1, mean1  = myCB.GetParameter(0), myCB.GetParameter(1), myCB.GetParameter(2), myCB.GetParameter(3)
                        sigma1, c1, slope1 = myCB.GetParameter(4), myCB.GetParameter(5), myCB.GetParameter(6)  
                        print "\n","FIT: sample ", s.Label, "norm", norm1,"alpha", alpha1, "n", n1, "mean",mean1,"sigma",sigma1,"c",c1,"slope",slope1 
                        
                        a = hist.GetLineColor()
                        myCB.SetLineColor(a)
                        myCB.Draw("SAME")

                    if expo:
                        def fitexpo(x, par):
                            xnew = x[0]
                            xnew = xnew
                            initial = par[0]
                            tau     = par[1]
                            #factor  = par[2] # so that the exponent has no units
                            #const   = par[2]
                            return initial * math.exp(tau * xnew ) 
                        
                        myexp = TF1("fitexpo", fitexpo, fit[0], fit[1], 2)
                        initial_guess = hist.GetBinContent(1)
                        factor = (fit[0] + fit[1]) / 2.0 
                        
                        myexp.SetParLimits(0, 0.0, 15 * initial_guess)
                        myexp.SetParLimits(1, -90.0, 0.0)
                        #myexp.FixParameter(2, factor)
                        #myexp.SetParLimits(2, factor/2, 2*factor) 

                        #myexp.SetParameters(initial_guess,-0.1, factor)
                        myexp.SetParameters(initial_guess, -0.1)

                        hist.Fit(myexp,"RQN")
                        initial = myexp.GetParameter(0)
                        tau = myexp.GetParameter(1)
                        #expNorm = myexp.GetParameter(2)
                        
                        myexp.SetLineColor(2)
                        myexp.Draw("SAME")

                        def expo(x, par):
                            return initial * math.exp(tau * x[0]) 

                        #myexpFull = TF1("expo",expo, fit[0], fit[1], 1)
                        myexpFull = TF1("expo",expo, fit[0], 160, 1)
                        hist.Fit(myexpFull,"RQN")
                        myexpFull.SetLineColor(2)
                        myexpFull.SetLineStyle(3)
                        myexpFull.Draw("SAME")

                        #print "Exp fit ", initial, tau, expNorm,"tau error", myexp.GetParError(1),  "integral 60 < mm < 120 = ", myexpFull.Integral(60000,160000) / myexpFull.Integral(40000,160000)
                        print "Exp fit ", initial, tau, "tau error", myexp.GetParError(1),  "integral 60 < mm < 120 = ", myexpFull.Integral(60,160) / myexpFull.Integral(40,160)

                        for i in fit:
                            if type(i) == type({}):
                                i["initial"] = initial
                                i["tau"] = tau 
                                i["tauError"] = myexp.GetParError(1)
                                #i["tauError1"] = abs((tau/expNorm)) * sqrt( pow((tau/myexp.GetParError(1)), 2) + pow((expNorm/myexp.GetParError(2)), 2) )
                                #i["tauError2"] = sqrt(pow((tau/expNorm),2) * ( pow((tau/myexp.GetParError(1)), 2) + pow((expNorm/myexp.GetParError(2)), 2) )  )
                    
                    if doubleCB:
                        #first fit an exponential initial * exp (c + tau x)

                        def fitexpo(x, par):
                            xnew = x[0]
                            xnew = xnew
                            initial = par[0]
                            tau     = par[1]
                            factor  = par[2] # so that the exponent has no units
                            #const   = par[2]
                            return initial * math.exp(tau * (xnew/factor)) 
                        
                        myinitialexp = TF1("fitexpo", fitexpo, fit[0], fit[1], 3)

                        initial_guess = hist.GetBinContent(1)
                        factor = (fit[0] + fit[1]) / 2.0 
                        
                        myinitialexp.SetParLimits(0, 0.0, 10 * initial_guess)
                        myinitialexp.SetParLimits(1, -1.0, 0.0)
                        #myinitialexp.FixParameter(0, 0.0004)
                        myinitialexp.FixParameter(2, factor) 
                        myinitialexp.SetParameters(initial_guess,-0.1,factor)

                        hist.Fit(myinitialexp,"RQN")

                        initial = myinitialexp.GetParameter(0)
                        tau = myinitialexp.GetParameter(1)
                        expNorm = myinitialexp.GetParameter(2)

                        print "initial exp ", initial, tau, expNorm

                        from config import fitDoubleCB

                        myCB = TF1("fitCB", fitDoubleCB, fit[0],fit[1], 11)
                        myCB.SetParName(0, "alpha1"   )
                        myCB.SetParName(1, "n1"  )
                        myCB.SetParName(2, "mean"   )
                        myCB.SetParName(3, "CBwidth1"  )
                        myCB.SetParName(4, "n2"  )
                        myCB.SetParName(5, "CBwidth2"  )
                        myCB.SetParName(6, "expN"      )
                        myCB.SetParName(7, "expAlpha"  )
                        myCB.SetParName(8, "N1"  )
                        myCB.SetParName(9, "N2"  )
                        myCB.SetParName(10, "expNorm"  )

                        histHalfInt = hist.Integral() / 2.0
                        mean_guess = 91.2 if fit[0] < 10000 else 91200.0
                        width_guess = 3.0 if fit[0] < 10000 else 3000.0
                        
                        myCB.FixParameter(0, 1.1) # this is always fixed...
                        myCB.FixParameter(6, initial)
                        myCB.FixParameter(7, tau)
                        myCB.FixParameter(10, expNorm) 
                        #myCB.SetParLimits(0, 0.0,1.1)
                        myCB.SetParLimits(1, 0.0,10.0)
                        myCB.SetParLimits(2, fit[0], fit[1])
                        myCB.SetParLimits(3, width_guess / 3, 10 * width_guess)
                        myCB.SetParLimits(4, 0.0, 1.0)
                        myCB.SetParLimits(5, width_guess / 3, 10 * width_guess)
                        #myCB.SetParLimits(6, 0.0, 0.1)
                        #myCB.SetParLimits(7, -10.0,0.0)
                        myCB.SetParLimits(8, 0.0, 3 * histHalfInt)
                        myCB.SetParLimits(9, 0.0, histHalfInt)
                        
                        #norm and sigma taken from MC gaussian fit (between 87000 and 95000), mean is PDG Z mass value
                                            #0  1      2           3           4     5            6       7      8          9
                        myCB.SetParameters(1.1, 1.0, mean_guess, width_guess, 1.0, width_guess, initial, tau, histHalfInt, histHalfInt/4, expNorm )

                        hist.Fit(myCB,"RQN")

                        #norm = " - "

                        f_alpha1  = myCB.GetParameter(0)
                        f_n1      = myCB.GetParameter(1) 
                        f_mean    = myCB.GetParameter(2) 
                        f_width1  = myCB.GetParameter(3)
                        #alph  = myCB.GetParameter(4)
                        f_n2      = myCB.GetParameter(4) 
                        f_width2  = myCB.GetParameter(5)
                        f_expN    = myCB.GetParameter(6)
                        f_expAlp  = myCB.GetParameter(7)
                        f_N1      = myCB.GetParameter(8)
                        f_N2      = myCB.GetParameter(9)
                        f_expNorm = myCB.GetParameter(10)


                        print s.Label,"FIT alpha1", f_alpha1, "n1", f_n1, "mean", f_mean, "width", f_width1, "N1", f_N1
                        print s.Label,"n2", f_n2, "width2",f_width2,"expN",f_expN,"expAlpha",f_expAlp,"N1",f_N1,"N2",f_N2, '\n' 
                        
                        a = hist.GetLineColor()

                        from config import singleCB

                        def CB1(x, par):
                            return singleCB(x[0], f_alpha1, f_n1, f_mean, f_width1, f_N1)

                        def CB2(x, par):
                            return singleCB(x[0], f_alpha1, f_n2, f_mean, f_width2, f_N2)

                        def expo(x, par):
                            #return 0.002 
                            return f_expN * math.exp(f_expAlp*(x[0]/f_expNorm)) 

                        myCB.SetLineColor(a)
                        myCB.Draw("SAME")

                        myexp = TF1("expo",expo, fit[0], fit[1], 1)
                        hist.Fit(myexp,"RQN")
                        myexp.SetLineColor(a+1)
                        myexp.Draw("SAME")

                        #myinitialexp.SetLineColor(a+4)
                        #myinitialexp.SetLineStyle(2)
                        #myinitialexp.Draw("SAME")

                        myCB1 = TF1("CB1",CB1, fit[0], fit[1], 1)
                        hist.Fit(myCB1,"RQN")
                        myCB1.SetLineColor(a+2)
                        myCB1.Draw("SAME")

                        myCB2 = TF1("CB2",CB2, fit[0], fit[1], 1)
                        hist.Fit(myCB2,"RQN")
                        myCB2.SetLineColor(a+3)
                        myCB2.Draw("SAME")

                        if len(fit) > 3:
                            #print "HERE", f_mean/1000.0, hist.GetTitle().split("/")[3]
                            fit[2][hist.GetTitle().split("/")[3]] = f_mean/1000.0
                            
                    if LCBG:
                        #first fit a straight line to get slope and intercept
                        from config import fitLine
                        
                        myLine = TF1("fitLine", fitLine, fit[0], fit[1], 2)
                        myLine.SetParName(0, "slope")
                        myLine.SetParName(1, "intercept")
                        #myLine.SetParameters(-0.005/600.0, 0.01)

                        nbins = hist.GetXaxis().GetNbins()
                        slope_guess = hist.GetBinContent(nbins) - hist.GetBinContent(1) / (fit[0] - fit[1])
                        intercept_guess = hist.GetBinContent(1)
                        myLine.SetParameters(slope_guess, intercept_guess)

                        hist.Fit(myLine,"RQN")

                        slope  = myLine.GetParameter(0)
                        intercept = myLine.GetParameter(1)

                        print '\n', s.Label, hist.Integral()
                        print "after line fit slope ", slope, "intercept ", intercept 

                        #now fix slope and intercept, fit line + gauss
                        from config import fitLinePlusGauss

                        myLPG = TF1("fitLPG", fitLinePlusGauss, fit[0], fit[1], 5)
                        myLPG.SetParName(0, "norm")
                        myLPG.SetParName(1, "mean")
                        myLPG.SetParName(2, "width")
                        myLPG.SetParName(3, "slope")
                        myLPG.SetParName(4, "intercept")
                        #myLPG.FixParameter(1, 91200)

                        zm = 91.2 if fit[0] < 1000 else 91200.0
                        width_guess = 3.0 if fit[0] < 1000 else 3000.0
                        norm_guess = hist.GetMaximum()
                        
                        #myLPG.SetParameters(0.08, zm, 3000.0, slope, intercept)
                        myLPG.SetParameters(norm_guess, zm, width_guess, slope, intercept)
                        
                        hist.Fit(myLPG,"RQN")

                        norm  = myLPG.GetParameter(0)
                        mean  = myLPG.GetParameter(1)
                        width = myLPG.GetParameter(2)
                        slope = myLPG.GetParameter(3)
                        intercept = myLPG.GetParameter(4)
                        
                        print "after line + gauss fit norm", norm, "mean", mean, "width", width, "slope ", slope, "intercept ", intercept 

                        from config import fitCBPlusG
                        
                        myCB = TF1("fitCB", fitCBPlusG , fit[0] , fit[1] , 9)
                        myCB.SetParName(0, "norm"   )
                        myCB.SetParName(1, "alpha"  )
                        myCB.SetParName(2, "n"      )
                        myCB.SetParName(3, "mean"   )
                        myCB.SetParName(4, "CBwidth"  )
                        myCB.SetParName(5, "intercept"      )
                        myCB.SetParName(6, "slope"  )
                        myCB.SetParName(7, "GaussNorm"  )
                        myCB.SetParName(8, "GaussWidth"  )

                        myCB.FixParameter(1, 1.1) # this is always fixed...
                        #myCB.FixParameter(3, mean)
                        #myCB.FixParameter(5, intercept)
                        #myCB.FixParameter(6, slope)
                        #myCB.FixParameter(7, norm)
                        #myCB.FixParameter(8, width)
                        myCB.SetParLimits(2, 0.0,5.0)

                        #if intercept < 0: intercept = 0.0
                        
                        #norm and sigma taken from MC gaussian fit (between 87000 and 95000), mean is PDG Z mass value
                        myCB.SetParameters(norm_guess, 1.1, 1.0, mean, width_guess, intercept, slope, norm, width )

                        hist.Fit(myCB,"RN")

                        #norm = " - "
                        CBnorm  = myCB.GetParameter(0)
                        alpha1 = myCB.GetParameter(1)
                        n1     = myCB.GetParameter(2) 
                        mean1  = myCB.GetParameter(3) 
                        sigma1 = myCB.GetParameter(4) 
                        intercept1   = myCB.GetParameter(5) 
                        slope1 = myCB.GetParameter(6)
                        norm1     = myCB.GetParameter(7)
                        width1     = myCB.GetParameter(8)

                        print s.Label,"FIT norm", CBnorm, "alpha", alpha1, "n", n1, "mean", mean1, "sigma",sigma1, "intercept",intercept1,"slope",slope1,"gauss norm",norm1,"gauss width", width1, '\n' 
                        a = hist.GetLineColor()
                        
                        #myLine.SetLineColor(a)
                        #myLine.Draw("SAME")
                        #myLPG.SetLineColor(a+2)
                        #myLPG.Draw("SAME")
                        #myCB.SetLineColor(a+3)
                        #myCB.Draw("SAME")
                        myCB.SetLineColor(a)
                        myCB.Draw("SAME")

                        if len(fit) > 3:
                            #print "HERE", mean1/1000.0, hist.GetTitle().split("/")[3]
                            fit[2][hist.GetTitle().split("/")[3]] = mean1/1000.0

                    if cbonly:
                        # just a single CB, no exponetial
                        from config import fitCBactual as fitCB
                    
                        myCB = TF1("fitCB", fitCB, fit[0],fit[1], 5)
                        myCB.SetParName(0, "alpha1"   )
                        myCB.SetParName(1, "n"  )
                        myCB.SetParName(2, "mean"   )
                        myCB.SetParName(3, "CBwidth"  )
                        myCB.SetParName(4, "N"  )

                        lowBinNum  = hist.FindBin(fit[0])
                        highBinNum = hist.FindBin(fit[1])
                        height_guess = hist.Integral(lowBinNum, highBinNum)
                        height_guess = hist.GetMaximum()
                        mean_guess = 91.187 if fit[0] < 10000 else 91187.0
                        width_guess = 3.0 if fit[0] < 10000 else 3000.0
                        
                        myCB.FixParameter(0, 1.1) # this is always fixed...
                        #myCB.SetParLimits(0, 0.0,1.1)
                        myCB.SetParLimits(1, 0.0,100.0)
                        myCB.SetParLimits(2, fit[0], fit[1])
                        myCB.SetParLimits(3, width_guess / 5, 10 * width_guess)
                        myCB.SetParLimits(4, height_guess / 20, 2 * height_guess)
                        
                                             #0  1      2           3           4     5            6            7      
                        myCB.SetParameters(1.1, 1.0, mean_guess, width_guess, height_guess)
                        
                        hist.Fit(myCB,"RQN")
                        
                        f_alpha1, f_n1, f_mean, f_width1, f_N  = myCB.GetParameter(0), myCB.GetParameter(1), myCB.GetParameter(2), myCB.GetParameter(3), myCB.GetParameter(4)   
                
                        print "\n", "FIT:", s.Label, "alpha1", f_alpha1, "n1", f_n1, "mean", f_mean, "width", f_width1, "N", f_N
                        a = hist.GetLineColor()
                    
                        myCB.SetLineColor(a+1)
                        myCB.Draw("SAME")

                        tL = TLine(f_mean, 1e-8 , f_mean, 1.1 * height_guess)
                        tL.SetLineColor(a+1)
                        tL.SetLineStyle(3)
                        tL.Draw("SAME")
                        SetOwnership(tL, False)

                        tL = TLine(mean_guess, 1e-8 , mean_guess, 1.1 * height_guess)
                        tL.SetLineColor(5)
                        tL.SetLineStyle(3)
                        tL.Draw("SAME")
                        SetOwnership(tL, False)

                        if "BOX" in fit:
                            size = 0.04
                            x = 0.65
                            y = 0.65
                            
                            LTX = TLatex()
                            LTX.SetNDC(1)
                            LTX.SetTextSize(size)
                            text1 = "mean:{mean:.5f}".format(mean=f_mean)
                            LTX.DrawLatex(x,y,text1)

                        
                        if len(fit) > 3:
                            print "HERE",
                            for l in fit:
                                if type(l) == type({}):
                                    #print hist.GetTitle().split("/")
                                    if hist.GetTitle().split("/")[0] == "EtaHists":
                                        l[hist.GetTitle().split("/")[1]] = f_mean/1000.0
                                    else:
                                        l[hist.GetTitle().split("/")[3]] = f_mean/1000.0
                                        l[hist.GetTitle().split("/")[3]+"_err"] =  myCB.GetParError(2)/1000.0

                    if dcbactual:
                        # just a double CB, no exponetial
                        from config import fitdCB as fitdCB
                    
                        myCB = TF1("fitCB", fitdCB, fit[0],fit[1], 8)
                        myCB.SetParName(0, "alpha1"   )
                        myCB.SetParName(1, "n1"  )
                        myCB.SetParName(2, "mean"   )
                        myCB.SetParName(3, "CBwidth1"  )
                        myCB.SetParName(4, "n2"  )
                        myCB.SetParName(5, "CBwidth2"  )
                        myCB.SetParName(6, "N1"  )
                        myCB.SetParName(7, "N2"  )

                        lowBinNum  = hist.FindBin(fit[0])
                        highBinNum = hist.FindBin(fit[1])
                        height_guess = hist.Integral(lowBinNum, highBinNum)
                        height_guess = hist.GetMaximum()
                        mean_guess = 91.187 if fit[0] < 10000 else 91187.0
                        width_guess = 3.0 if fit[0] < 10000 else 3000.0
                        
                        myCB.FixParameter(0, 1.1) # this is always fixed...
                        #myCB.SetParLimits(0, 0.0,1.1)
                        myCB.SetParLimits(1, 0.0,100.0)
                        myCB.SetParLimits(2, fit[0], fit[1])
                        myCB.SetParLimits(3, width_guess / 5, 10 * width_guess)
                        myCB.SetParLimits(4, 0.0, 100.0)
                        myCB.SetParLimits(5, width_guess / 5, 10 * width_guess)
                        myCB.SetParLimits(6, height_guess / 10, 2 * height_guess)
                        myCB.SetParLimits(7, height_guess / 20, 2 * height_guess)
                        
                                             #0  1      2           3           4     5            6            7      
                        myCB.SetParameters(1.1, 1.0, mean_guess, width_guess, 1.0, width_guess, height_guess, height_guess/3.0)
                        
                        hist.Fit(myCB,"RQN")
                        
                        f_alpha1, f_n1, f_mean, f_width1  = myCB.GetParameter(0), myCB.GetParameter(1), myCB.GetParameter(2), myCB.GetParameter(3)   
                        f_n2, f_width2, f_N1, f_N2  = myCB.GetParameter(4), myCB.GetParameter(5), myCB.GetParameter(6), myCB.GetParameter(7)   
                
                        print "\n", "FIT:", s.Label, "alpha1", f_alpha1, "n1", f_n1, "mean", f_mean, "width", f_width1, "n2", f_n2, "width2", f_width2, "N1", f_N1, "N2", f_N2, "hg", height_guess
                        a = hist.GetLineColor()
                    
                        from config import singleCB
                        
                        def CB1(x, par):
                            return singleCB(x[0], f_alpha1, f_n1, f_mean, f_width1, f_N1)
                    
                        def CB2(x, par):
                            return singleCB(x[0], f_alpha1, f_n2, f_mean, f_width2, f_N2)
                    
                        myCB.SetLineColor(a+1)
                        myCB.Draw("SAME")
                        
                        myCB1 = TF1("CB1",CB1, fit[0], fit[1], 1)
                        hist.Fit(myCB1,"RQN")
                        myCB1.SetLineColor(a+2)
                        myCB1.Draw("SAME")
                    
                        myCB2 = TF1("CB2",CB2, fit[0], fit[1], 1)
                        hist.Fit(myCB2,"RQN")
                        myCB2.SetLineColor(a+3)
                        myCB2.Draw("SAME")

                        tL = TLine(f_mean, 1e-8 , f_mean, 1.1 * height_guess)
                        tL.SetLineColor(a+1)
                        tL.SetLineStyle(3)
                        tL.Draw("SAME")
                        SetOwnership(tL, False)

                        tL = TLine(mean_guess, 1e-8 , mean_guess, 1.1 * height_guess)
                        tL.SetLineColor(5)
                        tL.SetLineStyle(3)
                        tL.Draw("SAME")
                        SetOwnership(tL, False)

                        if "BOX" in fit:
                            size = 0.04
                            x = 0.65
                            y = 0.65
                            
                            LTX = TLatex()
                            LTX.SetNDC(1)
                            LTX.SetTextSize(size)
                            text1 = "mean:{mean:.5f}".format(mean=f_mean)
                            LTX.DrawLatex(x,y,text1)

                        
                        if len(fit) > 3:
                            print "HERE",
                            for l in fit:
                                if type(l) == type({}):
                                    l[hist.GetTitle().split("/")[3]] = f_mean/1000.0

                    if freeMean:
                        # just a double CB, no exponetial, no shared mean...
                        from config import fitdCB2
                    
                        myCB = TF1("fitCB", fitdCB2, fit[0],fit[1], 9)
                        myCB.SetParName(0, "alpha1"   )
                        myCB.SetParName(1, "n1"  )
                        myCB.SetParName(2, "mean1"   )
                        myCB.SetParName(3, "CBwidth1"  )
                        myCB.SetParName(4, "n2"  )
                        myCB.SetParName(5, "CBwidth2"  )
                        myCB.SetParName(6, "N1"  )
                        myCB.SetParName(7, "N2"  )
                        myCB.SetParName(8, "mean2")

                        lowBinNum  = hist.FindBin(fit[0])
                        highBinNum = hist.FindBin(fit[1])
                        height_guess = hist.Integral(lowBinNum, highBinNum)
                        height_guess = hist.GetMaximum()
                        mean_guess = 91.187 if fit[0] < 10000 else 91187.0
                        width_guess = 3.0 if fit[0] < 10000 else 3000.0
                        
                        myCB.FixParameter(0, 1.1) # this is always fixed...
                        #myCB.SetParLimits(0, 0.0,1.1)
                        myCB.SetParLimits(1, 0.0,10.0)
                        myCB.SetParLimits(2, fit[0], fit[1])
                        myCB.SetParLimits(3, width_guess / 3, 10 * width_guess)
                        myCB.SetParLimits(4, 0.0, 1.0)
                        myCB.SetParLimits(5, width_guess / 3, 10 * width_guess)
                        myCB.SetParLimits(6, height_guess / 3, 2 * height_guess)
                        myCB.SetParLimits(7, height_guess / 5, 2 * height_guess)
                        myCB.SetParLimits(8, fit[0], fit[1])
                        
                                             #0  1      2           3           4     5            6            7      
                        myCB.SetParameters(1.1, 1.0, mean_guess, width_guess, 1.0, width_guess, height_guess, height_guess/3.0, mean_guess)
                        
                        hist.Fit(myCB,"RQN")
                        
                        f_alpha1, f_n1, f_mean, f_width1  = myCB.GetParameter(0), myCB.GetParameter(1), myCB.GetParameter(2), myCB.GetParameter(3)   
                        f_n2, f_width2, f_N1, f_N2  = myCB.GetParameter(4), myCB.GetParameter(5), myCB.GetParameter(6), myCB.GetParameter(7)   
                        f_m2 = myCB.GetParameter(8)
                
                        print "\n", "FIT:", s.Label, "alpha1", f_alpha1, "n1", f_n1, "mean", f_mean, "width", f_width1, "n2", f_n2, "width2", f_width2, "N1", f_N1, "N2", f_N2, "hg", height_guess, "m2", f_m2
                        a = hist.GetLineColor()
                    
                        from config import singleCB, singleGauss
                        
                        def G1(x,par):
                            return singleGauss(x[0], f_mean, f_width1, f_N1)
                    
                        def CB1(x, par):
                            return singleCB(x[0], f_alpha1, f_n1, f_mean, f_width1, f_N1)
                    
                        def CB2(x, par):
                            return singleCB(x[0], f_alpha1, f_n2, f_m2, f_width2, f_N2)
                    
                        myCB.SetLineColor(a+1)
                        myCB.Draw("SAME")

                        myG1 = TF1("G1",G1, fit[0], fit[1], 1)
                        hist.Fit(myG1,"RQN")
                        myG1.SetLineColor(a+2)
                        myG1.Draw("SAME")
                        
                        #myCB1 = TF1("CB1",CB1, fit[0], fit[1], 1)
                        #hist.Fit(myCB1,"RQN")
                        #myCB1.SetLineColor(a+2)
                        #myCB1.Draw("SAME")
                    
                        myCB2 = TF1("CB2",CB2, fit[0], fit[1], 1)
                        hist.Fit(myCB2,"RQN")
                        myCB2.SetLineColor(a+3)
                        myCB2.Draw("SAME")

                        tL = TLine(f_mean, 1e-8 , f_mean, 1.1 * height_guess)
                        tL.SetLineColor(a+2)
                        tL.SetLineStyle(3)
                        tL.Draw("SAME")
                        SetOwnership(tL, False)

                        tL = TLine(f_m2, 1e-8 , f_m2, 1.1 * height_guess)
                        tL.SetLineColor(a+3)
                        tL.SetLineStyle(3)
                        tL.Draw("SAME")
                        SetOwnership(tL, False)

                        tL = TLine(mean_guess, 1e-8 , mean_guess, 1.1 * height_guess)
                        tL.SetLineColor(5)
                        tL.SetLineStyle(3)
                        tL.Draw("SAME")
                        SetOwnership(tL, False)
                        
                        if len(fit) > 3:
                            #print "HERE", f_mean/1000.0, hist.GetTitle().split("/")[3]
                            fit[2][hist.GetTitle().split("/")[3]] = f_mean/1000.0

                    if gaussExp:
                        # just a double CB, no exponetial, no shared mean...
                        from config import fitGaussExp
                    
                        myFit = TF1("fitCB", fitGaussExp, fit[0],fit[1], 5)
                        myFit.SetParName(0, "mean"   )
                        myFit.SetParName(1, "width"  )
                        myFit.SetParName(2, "N1"   )
                        myFit.SetParName(3, "N2"  )
                        myFit.SetParName(4, "tau"  )

                        lowBinNum  = hist.FindBin(fit[0])
                        highBinNum = hist.FindBin(fit[1])
                        height_guess = hist.Integral(lowBinNum, highBinNum)
                        height_guess = hist.GetMaximum()
                        mean_guess = 91.187 if fit[0] < 10000 else 91187.0
                        width_guess = 3.0 if fit[0] < 10000 else 3000.0
                        tau_guess = -1.0/fit[0]
                        
                        myFit.SetParLimits(0, fit[0], fit[1])
                        myFit.SetParLimits(1, width_guess / 3, 10 * width_guess)
                        myFit.SetParLimits(2, height_guess / 3, 2 * height_guess)
                        myFit.SetParLimits(3, height_guess / 5, 2 * height_guess)
                        myFit.SetParLimits(4, 5*tau_guess, 0.0)

                                             #0               1      2           3                  4     5            6            7      
                        myFit.SetParameters(mean_guess, width_guess, height_guess, height_guess/3.0, tau_guess)
                        
                        hist.Fit(myFit,"RQN")

                        mean, width, N1, N2, tau = myFit.GetParameter(0),myFit.GetParameter(1),myFit.GetParameter(2),myFit.GetParameter(3),myFit.GetParameter(4)
                
                        print "\n", "FIT:", s.Label, "mean", mean, "width", width, "N1", N1, "N2", N2, "tau", tau
                        a = hist.GetLineColor()
                    
                        from config import singleGauss
                        
                        def G1(x,par):
                            return singleGauss(x[0], mean, width, N1)

                        def Exp1(x,par):
                            return N1 * math.exp(tau * x[0])
                    
                        myFit.SetLineColor(a+1)
                        myFit.Draw("SAME")

                        myG1 = TF1("G1",G1, fit[0], fit[1], 1)
                        hist.Fit(myG1,"RQN")
                        myG1.SetLineColor(a+2)
                        myG1.Draw("SAME")
                        
                        myExp = TF1("exp",Exp1, fit[0], fit[1], 1)
                        hist.Fit(myExp,"RQN")
                        myExp.SetLineColor(a+3)
                        myExp.Draw("SAME")

                        tL = TLine(mean, 1e-8 , mean, 1.1 * height_guess)
                        tL.SetLineColor(a+2)
                        tL.SetLineStyle(3)
                        tL.Draw("SAME")
                        SetOwnership(tL, False)

                        tL = TLine(mean_guess, 1e-8 , mean_guess, 1.1 * height_guess)
                        tL.SetLineColor(5)
                        tL.SetLineStyle(3)
                        tL.Draw("SAME")
                        SetOwnership(tL, False)
                        
                        if len(fit) > 3:
                            #print "HERE", f_mean/1000.0, hist.GetTitle().split("/")[3]
                            fit[2][hist.GetTitle().split("/")[3]] = f_mean/1000.0

                    if quad:
                        from config import quad

                        myFit = TF1("quad", quad, fit[0], fit[1], 3)

                        myFit.SetParName(0, "p0"   )
                        myFit.SetParName(1, "p1"  )
                        myFit.SetParName(2, "p2"   )

                        p0_guess = 2000.0
                        p1_guess = -15000.0
                        p2_guess = -p1_guess * 2 # due to approximate constraint f'(x) = 0 at x = 1/4

                        #myFit.SetParLimits(0, fit[0], fit[1])
                        #myFit.SetParLimits(1, width_guess / 3, 10 * width_guess)
                        #myFit.SetParLimits(2, height_guess / 3, 2 * height_guess)

                        myFit.SetParameters(p0_guess, p1_guess, p2_guess)
                        
                        hist.Fit(myFit,"RQN")
                        a = hist.GetLineColor()
                        myFit.SetLineColor(a+1)
                        myFit.Draw("SAME")
                        p0, p1, p2  = myFit.GetParameter(0), myFit.GetParameter(1), myFit.GetParameter(2)
                        for i in fit:
                            if type(i)==type({}):
                                i["p0"] = p0
                                i["p1"] = p1
                                i["p2"] = p2
                    
                    if asymm_quad:
                        def tmpfunc(x,par):
                            xnew = x[0]
                            p0   = par[0]
                            p1   = par[1]
                            p2   = par[2]
                            p3   = par[3]

                            #quadratic part
                            expo1 = math.exp(p1 * (x[0] - p3))

                            #exponential part to account for asymmetry, make it so it dominates as x -> p1 and beyond
                            expo2 = math.exp(p2 * (x[0] - p3))
                            #expo2 = 0.0
                            return p0 * (expo1 + expo2)

                        def tmpfunc1(x,par):
                            xnew = x[0]
                            p0   = par[0]
                            p1   = par[1]
                            p2   = par[2]
                            p3   = par[3]
                            p4   = par[4]
                            p5   = par[5]

                            #quadratic part
                            expo1 = p0 * math.exp(p1 * (x[0] - p3))

                            #exponential part to account for asymmetry, make it so it dominates as x -> p1 and beyond
                            expo2 = p4 * math.exp(p2 * (x[0] - p5))
                            #expo2 = 0.0
                            return expo1 + expo2

                        
                        myFit = TF1("quad", tmpfunc1, fit[0], fit[1], 6)

                        myFit.SetParName(0, "expNorm"  )
                        myFit.SetParName(1, "tau1"  )
                        myFit.SetParName(2, "tau2"  )
                        myFit.SetParName(3, "offset"  )
                        myFit.SetParName(4, "expNorm2"  )
                        myFit.SetParName(5, "offset2"  )
                        
                        p0_guess = 0.5 
                        p1_guess = 550.0
                        p2_guess = -200.0
                        p3_guess = 0.23
                        p4_guess = 0.5
                        p5_guess = 0.23

                        myFit.SetParLimits(0, 0.0, 0.9)       
                        myFit.SetParLimits(1, 600, 100)
                        myFit.SetParLimits(2,-300,-100)        #
                        #myFit.FixParameter(2, 0.0)  
                        #myFit.SetParLimits(3, fit[0], fit[1]) #minimum should be somewhere within  fit range
                        myFit.SetParLimits(3, 0.01, 2.00) #minimum should be somewhere within  fit range
                        myFit.SetParLimits(4, 0.0, 0.9)
                        myFit.SetParLimits(5, 0.01, 2.00) 
                        myFit.SetParameters(p0_guess, p1_guess, p2_guess, p3_guess, p4_guess, p3_guess)
                        
                        hist.Fit(myFit,"RQN")
                        a = hist.GetLineColor()
                        myFit.SetLineColor(a+1)
                        myFit.Draw("SAME")

                        p0, p1, p2, p3, p4, p5 = myFit.GetParameter(0), myFit.GetParameter(1), myFit.GetParameter(2), myFit.GetParameter(3), myFit.GetParameter(4), myFit.GetParameter(5)

                        #def tmpe1(x, par):
                        #    expo = p0 * math.exp(p1 * (x[0] - p3))
                        #    return expo
                        #
                        #def tmpe2(x, par):
                        #    expo = p4 * math.exp(p2 * (x[0] - p5))
                        #    return expo
                        #
                        #myExp1 = TF1("q1",tmpe1, fit[0], fit[1], 1)
                        #hist.Fit(myExp1,"RQN")
                        #myExp1.SetLineColor(a+2)
                        #myExp1.Draw("SAME")
                        #
                        #myExp2 = TF1("exp",tmpe2, fit[0], fit[1], 1)
                        #hist.Fit(myExp2,"RQN")
                        #myExp2.SetLineColor(a+3)
                        #myExp2.Draw("SAME")


                        for i in fit:
                            if type(i)==type({}):
                                i["p0"] = p0
                                i["p1"] = p1
                                i["p2"] = p2
                                i["p3"] = p3
                                i["p4"] = p4
                                i["p5"] = p5
                        
                        #if "BOX" in fit:
                        #    size = 0.04
                        #    x = 0.65
                        #    y = 0.65
                        #    
                        #    LTX = TLatex()
                        #    LTX.SetNDC(1)
                        #    LTX.SetTextSize(size)
                        #    text1 = "centre:{centre:.5f}".format(centre=centre)
                        #    text2 = "width:{width:.5f}".format(width=width)
                        #    LTX.DrawLatex(x,y,text1)
                        #    LTX.DrawLatex(x,y*(0.95),text2)
        if ratio:
            return ratioList
        return
        #return histClones
    
    def _LegendMarker(self, sample):
        """
        Set Lengend type depending on plot type
        """

        # Use that from sample if set
        if sample.LegendOpt:  return sample.LegendOpt

        # otherwise make a guess
        marker = "le"
        if "hist" in sample.Type: marker = 'le'
        #if "h" in sample.Type: marker = 'l'
        if sample.FillStyle != 0: marker = "f"

        return marker    

    def Draw(self,name='', canvas=None, xtitle=None, ytitle=None, logx=None, logy=None, xmin=None, xmax=None, ymin=None, ymax=None, 
             hmin=None, hmax=None, rebin=None, norm=None, AutoOrderCumul=None, cumul = None, func=None, ratio=None, noXAxis=None, absol=None, fit=None, band=None):

        """
        Draw a particular histogram 'name' for all samples to a canvas 
        If a user-defined function of the form func(hist) which returns locals() 
        is given this will be called on hist before drawing
        """       
        
        # Take canvas passed in, else use Plotter.gCanvas
        if not canvas:
            if self.gCanvas:
                canvas = self.gCanvas
            else:
                log.error('No canvas supplied and self.gCanvas not defined')
                sys.exit(40)

        #print "in draw", canvas
        #Change HERE for ratio plot
        if noXAxis : canvas.cd()
        if ratio:
            canvas.cd()
            return self._PlotHist(name=name, xtitle=xtitle, ytitle=ytitle, logx=logx, logy=logy, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, 
                                  hmin=hmin, hmax=hmax, rebin=rebin, norm=norm, AutoOrderCumul=AutoOrderCumul, cumul = cumul, func=func, ratio=True, absol=absol, band=band)

        # Draw hist + legend onto canvas
        self._PlotHist(name=name, xtitle=xtitle, ytitle=ytitle, logx=logx, logy=logy, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, 
                       hmin=hmin, hmax=hmax, rebin=rebin, norm=norm, AutoOrderCumul=AutoOrderCumul, cumul = cumul, func=func, noXAxis=noXAxis,absol=absol,fit=fit, band=band)
        #self._PlotHist(name=name, xtitle=xtitle, ytitle=ytitle, logx=logx, logy=logy, rebin=rebin, func=func)
        if self.PlotLegend:
            #h = TH1F("e","e",2,0,1)
            #h.SetLineColor(2)
            #leg = TLegend(0.1,0.1,0.3,0.3)
            #leg.AddEntry(h,"test","ple")
            #leg.Draw()
            #leg.SetTextSize(0.15)
            #SetOwnership(leg,False)
            #self.Legend.SetTextSize(0.015)
            self.Legend.Draw()
        canvas.Update()
        return canvas

    def RatioPrint(self, histList='', name='', ext = 'eps', outname='', xtitle=None, ytitle=None, logx=None, logy=None, 
                   xmin=None, xmax=None, ymin=None, ymax=None, hmin=None, hmax=None, rebin=None, norm=None, AutoOrderCumul=None, cumul = None, func=None, latex=None):
        
        if not len(histList) == 2:
            print "can't make ratio hist with histList length of ", len(histList)
            return

        c1 = TCanvas("c1","example",700,700)
        SetOwnership(c1,False)

        #pad1 is same plot as would have been drawn by Print.
        pad1 = TPad("pad1","pad1",0,0.31,1,1)
        pad1.SetBottomMargin(0)
        pad1.Draw()

        self.Draw(name=name, canvas=pad1, xtitle=xtitle, ytitle=ytitle, logx=logx, logy=logy, xmin=xmin, xmax=xmax, 
                  ymin=ymin, ymax=ymax, hmin=hmin, hmax=hmax, rebin=rebin, norm=norm, AutoOrderCumul=AutoOrderCumul, cumul = cumul, func=func, noXAxis=True)
            
        c1.cd()

        #pad 2 is for ratio histogram
        pad2 = TPad("pad2","pad2",0,0,1,0.3)
        pad2.SetTopMargin(0)
        pad2.SetBottomMargin(0.2)
                
        pad2.Draw()
        pad2.cd()

        a = histList[0].Clone()

        a.Sumw2()
        a.SetStats(0)
        histList[1].Sumw2()

        a.Rebin(1)
        histList[1].Rebin(1)
        
        a.Divide(histList[1])

        #exception for the case where nominator and denominator have opposite signs
        for i in range (1,a.GetXaxis().GetNbins()+1):
            if a.GetBinContent(i) < 0:
                #print "TWATTTTTTT"
                a.SetBinContent(i, abs(a.GetBinContent(i)))

        ratio_ymin = 0.5
        ratio_ymax = 1.8
        ratio_title = "data/MC"

        if self.rP == None : self.rP = {}
        for i in self.rP:
            if i == "ymin" : ratio_ymin = self.rP[i]
            if i == "ymax" : ratio_ymax = self.rP[i]
            if i == "ytitle" : ratio_title = self.rP[i] 

        # to test errors of divided hists uncomment...
        #for i in range (1,a.GetXaxis().GetNbins()+1):
        #    # set the error on the ratio to sqrt of the sum of the squares of the errors on each hist...
        #    mll = a.GetBinCenter(i)
        #    con1 = histList[0].GetBinContent(i)
        #    err1 = histList[0].GetBinError(i)
        #    con2 = histList[1].GetBinContent(i)
        #    err2 = histList[1].GetBinError(i)
        #    error = 0.0
        #    if not con1 == 0.0 and not con2 == 0.0: error = a.GetBinContent(i) * math.sqrt(pow( (err1/con1), 2) + pow( (err2/con2), 2))
        #    #print "TESTING", i, mll, "bin content", a.GetBinContent(i), "bin err", a.GetBinError(i), con1, err1, con2, err2, error
        
        a.SetAxisRange(xmin, xmax, "X")
        a.SetAxisRange(ratio_ymin, ratio_ymax, "Y")
        a.GetYaxis().SetTitle(ratio_title)

        a.GetYaxis().SetNdivisions(5,5,0,True);
	a.GetYaxis().SetTitleSize(0.10);
	a.GetYaxis().SetTitleOffset(0.35);
	a.GetYaxis().SetLabelSize(0.06);

        a.GetXaxis().SetTitleSize(0.10);
	a.GetXaxis().SetTitleOffset(0.85);
	a.GetXaxis().SetLabelSize(0.08);

        a.Draw("")

        #draw line at 1
	l1 = TLine(xmin,1,xmax,1)
	l1.SetLineStyle(2)
	#l1.SetLineWidth(3.0)
	l1.SetLineColor(2)
        l1.Draw("")
        c1.cd()

        # Print canvas
        if not outname: 
            # Use prefix and hist name if only one hist else just prefix
            if len(name)==1:
                outname = self.OutputPrefix + '.' + name[0].replace('/', '.').replace(' ', '_')
            else:
                outname = self.OutputPrefix
        outname += ('.' + ext.lower().strip('.'))

        if latex:
            size = 0.08
            x = 0.15
            y = 0.15
            if latex[1]: size = latex[1]
            if latex[2]: x = latex[2]
            if latex[3]: y = latex[3]

            LTX = TLatex()
            LTX.SetNDC(1)
            LTX.SetTextSize(size)
            text = latex[0]
            LTX.DrawLatex(x,y,text)



        #print "PRINTING", outname
        c1.Print(outname)

        return

    def Print(self, name='', ext = 'eps', nPadsX=1, nPadsY=1, outname='', xtitle=None, ytitle=None, logx=None, logy=None, 
              xmin=None, xmax=None, ymin=None, ymax=None, hmin=None, hmax=None, rebin=None, norm=None, AutoOrderCumul=None, cumul = None, func=None, ratio=None, absol=None,
              fit=None, rP=None, latex=None, band=None, LHCb=None):

        """
        Draw a particular histogram 'name' or histograms [name] for all samples to a canvas and print to format given by ext. 
        If outname is set then print to this name, else construct name for sample.Labeland histrogram 
        name.  If a user-defined function of the form func(hist) which returns locals() is given this will be called on hist before 
        drawing

        ratio works by having Draw return a list of 2 hists, and forwarding a call to RatioPrint, which sorts out the canvas and does the ratio hist.
        """

        # Short cut for lazy people
        name = [name] if isinstance(name, str) else name        
        # Check enough pads to plot hists
        if len(name) > nPadsX*nPadsY:
            log.error("Number of requested histograms (%s) grater than number of pads (%s)" % (len(name), nPadsX*nPadsY))
            sys.exit(20)


        # Setup canvas
        #if 'Canvas' in dir(self):
            #a = getattr(self,'Canvas')
            #del a
            #del self.Canvas
            #print dir(self)

        w = 700
        h = 500

        ## for some reason to do with canvas this fixes things...
        dir(self)
        
        canvas = TCanvas("Canvas", "Canvas", w, h)
        canvas.Clear()
        canvas.SetFillColor(10)
        canvas.SetFrameFillColor(10)
        canvas.Divide(nPadsX,nPadsY)

        #canvas.Update()
        #canvas.cd()
        #self.Canvas=canvas
        
        self.rP = rP
        
        # Draw hists
        for i,n in enumerate(name):
            if ratio:
                canvas.cd(i+1)
                b = self.Draw(name=n, canvas=canvas, xtitle=xtitle, ytitle=ytitle, logx=logx, logy=logy, xmin=xmin, xmax=xmax, 
                              ymin=ymin, ymax=ymax, hmin=hmin, hmax=hmax, rebin=rebin, norm=norm, AutoOrderCumul=AutoOrderCumul, cumul = cumul, func=func, ratio=True, absol=absol, band=band)
                     
                self.RatioPrint(histList=b, name=n,  ext = ext, outname=outname, xtitle=xtitle, ytitle=ytitle, logx=logx, logy=logy, 
                           xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, hmin=hmin, hmax=hmax, rebin=rebin, norm=norm, AutoOrderCumul=AutoOrderCumul, cumul = cumul, func=func, latex=latex)
                return

            else:
                canvas.cd(i+1)
                self.Draw(name=n, canvas=canvas, xtitle=xtitle, ytitle=ytitle, logx=logx, logy=logy, xmin=xmin, xmax=xmax, 
                          ymin=ymin, ymax=ymax, hmin=hmin, hmax=hmax, rebin=rebin, norm=norm, AutoOrderCumul=AutoOrderCumul, cumul = cumul, func=func,absol=absol, fit=fit, band=band)
                #self.Draw(name=n, xtitle=xtitle, ytitle=ytitle, logx=logx, logy=logy, rebin=rebin, func=func, canvas=canvas)
                #self._PlotHist(name=n, xtitle=xtitle, ytitle=ytitle, logx=logx, logy=logy, rebin=rebin, func=func)
                #if self.PlotLegend: self.Legend.Draw()    

            #canvas.Update()

        # Print canvas
        if not outname: 
            # Use prefix and hist name if only one hist else just prefix
            if len(name)==1:
                outname = self.OutputPrefix + '.' + name[0].replace('/', '.').replace(' ', '_')
            else:
                outname = self.OutputPrefix
        outname += ('.' + ext.lower().strip('.'))

        if latex:
            size = 0.08
            x = 0.15
            y = 0.15
            if latex[1]: size = latex[1]
            if latex[2]: x = latex[2]
            if latex[3]: y = latex[3]

            LTX = TLatex()
            LTX.SetNDC(1)
            LTX.SetTextSize(size)
            text = latex[0]
            LTX.DrawLatex(x,y,text)

        if LHCb:
            lhcb = TBox(2.0, 0.0, 4.5, 1.0)
            lhcb.SetFillColor(8)
            lhcb.SetFillStyle(3704)
            lhcb.SetLineColor(1)        
            lhcb.Draw("SAME")
            

        #if band:
            #hist.Draw(s.Type)
            #from graph import gr
            #canvas = gr(canvas)
            #canvas.SaveAs(outname)
            #return
            #return
        #canvas.Update()
        canvas.Print(outname)



        return

    def Write(self, prefix='', name=None, hack="", update=False):
        """
        Write out all (modified) hists, or those in name if given, to a new root file.
        Will get a separate file for each sample.
        """
        # Special case for passing a hist in (bit of a hack)
        if isinstance(name, TH1):
           for s in self.Samples:
               s.Write()
               return
     
        # Short cut for lazy people
        name = [name] if isinstance(name, str) else name

        for s in self.Samples:
            if not prefix: outfile = s.Label+'.root'
            else:          outfile = prefix.rstrip('.root') + '.' + s.Label + '.root'

            print "Writing hist", outfile, name
            if hack:
                #print "doing a dodgy hack", hack
                for i,v in enumerate(name):
                    s.Get(name[i]).SetNameTitle(hack[i],hack[i])
            
            s.Write(outfile, name, update=update)
        return

    def Get(self, name):
        """
        Get array of styled hists called 'name' for all samples
        """

        histArray = []
        for i,s in enumerate(self.Samples):
            hist = s.Get(name, i)
            hist.SetName(s.Label + '.' + name)
            histArray.append(hist)
            pass
        return histArray

    def _CellFormat(self, val, format = '%10.5g', latex=True):
        s = (format % val).strip()  

        form = TexOrPlain(latex)

        if 'e' in s:
            rs = re.search(r'e(-?)(?:[+]?)(?:[0]*)([1-9]+)([0-9]*)', s)
            beginning = s[:s.index('e')]
            return '%s %s 10^%s%s%s' % (beginning, form.times, form.grpbeg, "".join(rs.groups()), form.grpend)
        else:
            rs = re.search(r'(-?)(?:[0]*)([0-9]+)(\.?)([0-9]*)$(?:[0]*)', s)
            return "%s" % "".join(rs.groups())

    def CutFlow(self, name='', samples = [], scale=None, prefix = None, format='%10.5g', latex=False, colWidth=35):
        """
        Print the cut flow for specified (or all if non-given) samples
        """

        # If list of samples not given use self.Samples
        if not samples: samples = self.Samples

        # Make dictionary of cut names and list of values per sample
        cuts = OrderedDict()
        for s in samples:
            cutDict = s.MakeCutFlow(name=name, scale=scale)
            if cutDict == None: return
            for k,v in cutDict.iteritems():
                try:
                    cuts[k].append(v)
                except KeyError:
                    cuts[k] = [v]

        form = TexOrPlain(latex, len(samples)+1)

        if not latex: form.rowsep = form.rowsep*((colWidth + len(form.colsep))*(len(samples)+1) + len(form.colsep))
        
        header = '%s%s%s%s%s' % (form.rowstart, "Cut".ljust(colWidth), form.colsep, 
                                 form.colsep.join([s.Label.center(colWidth) for s in samples]), form.rowend)

        table = '%s\n%s\n%s\n' % (form.rowsep,header, form.rowsep)

        for cutName,cutList in cuts.iteritems():
            row = "%s%s" % (form.rowstart, cutName.ljust(colWidth))
            for cut in cutList: 
                rowCell = "%s%s %s %s%s" % (form.math, self._CellFormat(cut[0], format, latex), form.pm, 
                                            self._CellFormat(cut[1], format, latex), form.math)
                row += "%s%s" % (form.colsep, rowCell.center(colWidth))

            row   += '%s\n' % form.rowend
            table += row

        table += '%s' % form.rowsep

        if not prefix:
            print table
        else:
            filename = prefix.rstrip('.') + form.ext 
            f = open(filename, 'w')
            f.write(form.filebeg)
            f.write(table)
            f.write(form.fileend)
        return

    def Limit(self, histname, signal, background, data = None, discovery = False, nexp = 50000):
        """
        """
        # Short cut for lazy people
        signal     = [signal] if isinstance(signal, Sample) else signal
        background = [background] if isinstance(background, Sample) else background

        # Set signal(s), bacround(s), sum and data
        sigHist = signal[0].Get(histname)
        for s in signal[1:]: sigHist.Add(s.Get(histname))

        bkgHist = background[0].Get(histname)
        for s in background[1:]: bkgHist.Add(s.Get(histname))                        

        totHist = bkgHist.Clone()
        totHist.Add(sigHist)

        if data: dataHist = data.Get(histname)
        else:    dataHist = bkgHist.Clone()

        # Compute limit
        es = TVectorD(2); eb = TVectorD(2)
        es[0] = es[1] = eb[0] = eb[1] = 0

        errName = TObjArray()
        err1 = TObjString("err1"); err2 = TObjString("err2");
        errName.Add(err1); errName.Add(err2);
        
        dataSource = TLimitDataSource(sigHist,bkgHist,dataHist,es,eb,errName);
        conf = TLimit.ComputeLimit(dataSource,nexp);

        # Print
        print "1-Cls  : ", 1-conf.CLs(), "\nClsb   : ", conf.CLsb(), "\nClb    : ",conf.CLb()
        print "1-<Cls>  : ", 1-conf.GetExpectedCLs_b(), "\n<Clsb>   : ", conf.GetExpectedCLsb_b(), "\n<Clb>    : ", conf.GetExpectedCLb_b()

        sigAtlas = math.sqrt(2)*TMath.ErfInverse(1-2*(conf.CLb() if discovery else conf.CLs()))
        sigLep   = math.sqrt(2)*TMath.ErfInverse(1-2*(conf.CLb() if discovery else conf.CLs())) 

        print 'Significance:  ATLAS = ', sigAtlas, ', LEP = ', sigLep

        return sigAtlas

    def Divide(self,num,den, numScale, denScale, opt="", name=""):
        "Divide two hists for all samples and add result to hist array"
        hists = [s.Divide(num, den, numScale, denScale, opt) for s in self.Samples ]
        return hists

    def _NotImplForGraphs(self, hist, operation=''):
        if hist.InheritsFrom('TGraph'):
            if operation: log.warning('%s not implemented for TGraphs.  Skipping' % operation)
            return True
        else:
            return False
    
    def __iter__(self):
        "Return iterator of underling data structure"
        return self.Samples.__iter__()

    def next(self):
        "Return next histogram underling data structure"
        self.Samples.__iter__().next()

    def __str__(self):
        "Return list of samples for printing"
        s = "List of samples:\n"
        s += '\n'.join([s.Label for s in self.Samples])
        return s

    def __getitem__(self, idx):
        "Return sample by index or key"

        if isinstance(idx, str):
            # Find by key 
            for s in self.Samples:
                if s.Label==idx: return s
            raise KeyError
        else: 
            # Find by index
            try:
                return self.Samples[idx]
            except IndexError:
                raise

    def __contains__(self, name):
        "Does plotter contain a paticular sample"
        import operator
        return reduce(operator.or_,[s.Label==name for s in self.Samples])

    def __setattr__(self, name, value):
        "Deal with special cases of setting arguments"

        if name == 'OutputLevel':
            object.__setattr__(self, name, value)
            log.setLevel(value)
        else:
            object.__setattr__(self, name, value)

        return

    pass
