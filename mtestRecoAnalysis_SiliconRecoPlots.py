###mtestRawtoDigits.root

#!/usr/bin/env python
#atlas_setup root

from ROOT import *

from Plotter import Plotter
from Sample import Sample
from Logging import *
import array

test = True

if test:

    x = Sample( FileName = 'rootFiles/mtestRecoAnalysis_siliconRecoPlots.root', Type = 'h', Sumw2 = False, Label = 'mtestRecoAnalysis_SiRecoPlots')

    print x

    x.Type2D = 'COLZ'
    x.LineColour = 4

    samples = [x]
    
    plots = Plotter(samples)
    plots.PlotLegend = False




    # PER EVENT HISTOS

    fname = "plots/mtestRecoAnalysis/Silicon/"
    
# h_firstStrawHitLayer
    plots.Print("EventNum",  xtitle='Event Number', ytitle='', outname = fname + 'EventNum')

# h_firstStrawHitView
    plots.Print("RunNum",  xtitle='RunNum', ytitle='', outname = fname + 'RunNum')

# h_firstStrawHitView
    plots.Print("b_scintTimeNs",  xtitle='time [ns]', ytitle='events', outname = fname + 'b_scintTimeNs')
    
# h_firstStrawHitView
    plots.Print("calibTime",  xtitle='time ', ytitle='events', outname = fname + 'calibTime')

# h_firstStrawHitView
    plots.Print("chargeStripY",  xtitle='', ytitle='', outname = fname + 'chargeStripY')

# h_firstStrawHitView
    plots.Print("chargeStripZ",  xtitle='', ytitle='', outname = fname + 'chargeStripZ')

# h_firstStrawHitView
    plots.Print("f_scintTimeNs",  xtitle='time [ns]', ytitle='', outname = fname + 'f_scintTimeNs')

# h_firstStrawHitView
    plots.Print("l_pedestal",  xtitle='', ytitle='', outname = fname + 'l_pedestal')

# h_firstStrawHitView
    plots.Print("r_pedestal",  xtitle='', ytitle='', outname = fname + 'r_pedestal')

# h_firstStrawHitView
    plots.Print("rawTime",  xtitle='time', ytitle='', outname = fname + 'rawTime')

# h_firstStrawHitView
    plots.Print("trigger_Time",  xtitle='time', ytitle='', outname = fname + 'trigger_Time')

    
