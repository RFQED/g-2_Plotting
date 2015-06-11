###mtestReadoutAnalysis_strawTruthSanityPlots.root

#!/usr/bin/env python
#atlas_setup root

from ROOT import *

from Plotter import Plotter
from Sample import Sample
from Logging import *
import array

test = True

if test:

    x = Sample( FileName = 'rootFiles/mtestReadoutAnalysis_strawTruthSanityPlots.root', Type = 'h', Sumw2 = False, Label = 'ReadoutAna_strawTruthSanityPlots')

    print x

    x.Type2D = 'COLZ'
    x.LineColour = 4

    samples = [x]
    
    plots = Plotter(samples)
    plots.PlotLegend = False

    # PER EVENT HISTOS

    fname = "plots/mtestReadoutAnalysis/strawTruthSanity"
    
# h_firstStrawHitLayer
    plots.Print("h_firstStrawHitLayer",  xtitle='number of hits', ytitle='events', outname = fname + '/h_firstStrawHitLayer')

# h_firstStrawHitView
    plots.Print("h_firstStrawHitView",  xtitle='hitTime', ytitle='events', outname = fname + '/h_firstStrawHitView')
    
# h_firstStrawHitView
    plots.Print("h_strawHitChanPrimaries_V0_L0",  xtitle='hitTime', ytitle='events', outname = fname + '/h_strawHitChanPrimaries_V0_L0')

# h_firstStrawHitView
    plots.Print("h_strawHitChanPrimaries_V0_L1",  xtitle='hitTime', ytitle='events', outname = fname + '/h_strawHitChanPrimaries_V0_L1')

# h_firstStrawHitView
    plots.Print("h_strawHitChanPrimaries_V1_L0",  xtitle='hitTime', ytitle='events', outname = fname + '/h_strawHitChanPrimaries_V1_L0')

# h_firstStrawHitView
    plots.Print("h_strawHitChanPrimaries_V1_L1",  xtitle='hitTime', ytitle='events', outname = fname + '/h_strawHitChanPrimaries_V1_L1')

# h_firstStrawHitView
    plots.Print("h_strawHitChanSecondaries_V0_L0",  xtitle='hitTime', ytitle='events', outname = fname + '/h_strawHitChanSecondaries_V0_L0')

# h_firstStrawHitView
    plots.Print("h_strawHitChanSecondaries_V0_L1",  xtitle='hitTime', ytitle='events', outname = fname + '/h_strawHitChanSecondaries_V0_L1')

# h_firstStrawHitView
    plots.Print("h_strawHitChanSecondaries_V1_L0",  xtitle='hitTime', ytitle='events', outname = fname + '/h_strawHitChanSecondaries_V1_L0')

# h_firstStrawHitView
    plots.Print("h_strawHitChanSecondaries_V1_L1",  xtitle='hitTime', ytitle='events', outname = fname + '/h_strawHitChanSecondaries_V1_L1')

# h_firstStrawHitView
    plots.Print("h_strawHitCountPerEventPrimaries_V0_L0",  xtitle='hitTime', ytitle='events', outname = fname + '/h_strawHitCountPerEventPrimaries_V0_L0')

# h_firstStrawHitView
    plots.Print("h_strawHitCountPerEventPrimaries_V0_L1",  xtitle='hitTime', ytitle='events', outname = fname + '/h_strawHitCountPerEventPrimaries_V0_L1')  

# h_firstStrawHitView
    plots.Print("h_strawHitCountPerEventPrimaries_V1_L0",  xtitle='hitTime', ytitle='events', outname = fname + '/h_strawHitCountPerEventPrimaries_V1_L0')

# h_firstStrawHitView
    plots.Print("h_strawHitCountPerEventPrimaries_V1_L1",  xtitle='hitTime', ytitle='events', outname = fname + '/h_strawHitCountPerEventPrimaries_V1_L1')

# h_firstStrawHitView
    plots.Print("h_strawHitCountPerEvent_V0_L0",  xtitle='hitTime', ytitle='events', outname = fname + '/h_strawHitCountPerEvent_V0_L0')

# h_firstStrawHitView
    plots.Print("h_strawHitCountPerEvent_V0_L1",  xtitle='hitTime', ytitle='events', outname = fname + '/h_strawHitCountPerEvent_V0_L1')

# h_firstStrawHitView
    plots.Print("h_strawHitCountPerEvent_V1_L0",  xtitle='hitTime', ytitle='events', outname = fname + '/h_strawHitCountPerEvent_V1_L0')

# h_firstStrawHitView
    plots.Print("h_strawHitCountPerEvent_V1_L0",  xtitle='hitTime', ytitle='events', outname = fname + '/h_strawHitCountPerEvent_V1_L0')

# h_firstStrawHitView
    plots.Print("h_strawHitCountPerEvent_V1_L1",  xtitle='hitTime', ytitle='events', outname = fname + '/h_strawHitCountPerEvent_V1_L1')

# h_firstStrawHitView
    plots.Print("h_strawHitPPrimaries_V0_L0",  xtitle='hitTime', ytitle='events', outname = fname + '/h_strawHitPPrimaries_V0_L0')

# h_firstStrawHitView
    plots.Print("h_strawHitPPrimaries_V0_L1",  xtitle='hitTime', ytitle='events', outname = fname + '/h_strawHitPPrimaries_V0_L1')

# h_firstStrawHitView
    plots.Print("h_strawHitPPrimaries_V1_L0",  xtitle='hitTime', ytitle='events', outname = fname + '/h_strawHitPPrimaries_V1_L0')

# h_firstStrawHitView
    plots.Print("h_strawHitPPrimaries_V1_L1",  xtitle='hitTime', ytitle='events', outname = fname + '/h_strawHitPPrimaries_V1_L1')

# h_firstStrawHitView
    plots.Print("h_strawHitPSecondaries_V0_L0",  xtitle='hitTime', ytitle='events', outname = fname + '/h_strawHitPSecondaries_V0_L0')

# h_firstStrawHitView
    plots.Print("h_strawHitPSecondaries_V0_L1",  xtitle='hitTime', ytitle='events', outname = fname + '/h_strawHitPSecondaries_V0_L1')

# h_firstStrawHitView
    plots.Print("h_strawHitPSecondaries_V1_L0",  xtitle='hitTime', ytitle='events', outname = fname + '/h_strawHitPSecondaries_V1_L0')

# h_firstStrawHitView
    plots.Print("h_strawHitPSecondaries_V1_L1",  xtitle='hitTime', ytitle='events', outname = fname + '/h_strawHitPSecondaries_V1_L1')

# h_firstStrawHitView
    plots.Print("h_strawHitTimes",  xtitle='hitTime', ytitle='events', outname = fname + '/h_strawHitTimes')
