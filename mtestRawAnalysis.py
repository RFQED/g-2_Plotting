###mtestRawAna.root

#!/usr/bin/env python
#atlas_setup root

from ROOT import *

from Plotter import Plotter
from Sample import Sample
from Logging import *
import array

test = True

if test:

    x = Sample( FileName = 'rootFiles/mtestRawAnalysis.root', Type = 'h', Sumw2 = False, Label = 'RawAnalysis')

    print x

    x.Type2D = 'COLZ'
    x.LineColour = 4

    samples = [x]
    
    plots = Plotter(samples)
    plots.PlotLegend = False

    
    # PER EVENT HISTOS

    fname = "plots/mtestRawAnalysis/"
    
# h_firstStrawHitLayer
    plots.Print("channelID",  xtitle='number of hits', ytitle='events', outname = fname + 'channelID')

# h_firstStrawHitView
    plots.Print("hitTime",  xtitle='hitTime', ytitle='events', outname = fname + 'hitTime')

# h_firstStrawHitView
    plots.Print("logicBoardID",  xtitle='hitTime', ytitle='events', outname = fname + 'logicBoardID')
    
# h_firstStrawHitView
    plots.Print("tdcID",  xtitle='hitTime', ytitle='events', outname = fname + 'tdcID')

# h_firstStrawHitView
    plots.Print("triggerTime",  xtitle='hitTime', ytitle='events', outname = fname + 'triggerTime')

    
