#!/usr/bin/env python
#atlas_setup root

from ROOT import *

from Plotter import Plotter
from Sample import Sample
from Logging import *
import array

test = True


if test:

    StrawSanity = Sample( FileName = 'rootFiles/mtestGunAnalysis_strawTruthSanityPlots.root', Type = 'h', Sumw2 = False, Label = 'straws')

    print StrawSanity

    StrawSanity.Type2D = 'COLZ'
    StrawSanity.LineColour = 4

    samples = [StrawSanity]
    
    plots = Plotter(samples)
    plots.PlotLegend = False
    
    # PER EVENT HISTOS

    fname = "plots/mtestGunAnalysis/StrawSanity"


## h_strawHitProtonSecondaries

# Hit times
    plots.Print("h_strawHitTimes",  xtitle='Hit time [ms]', ytitle='events', outname = fname + '/HitTimes')


# first straw hit layer
    plots.Print("h_firstStrawHitLayer", xtitle='Layer Number', ytitle='events', outname = fname + '/LayerNumberofFirstStrawHitinEvent' )

# first straw  hit view
    plots.Print("h_firstStrawHitView", xtitle='View Number', ytitle='events', outname = fname + '/LayerNumberofFirstStrawHitinView' )

# Straw Number for Hits from Primaries
    plots.Print("h_strawHitChanPrimaries_V0_L0", xtitle='Straw Number For Hits By Primaries V0_L0', ytitle='events', outname = fname + '/h_strawHitChanPrimaries_V0_L0' )   
    plots.Print("h_strawHitChanPrimaries_V0_L1", xtitle='Straw Number For Hits By Primaries V0_L1', ytitle='events', outname = fname + '/h_strawHitChanPrimaries_V0_L1' )
    plots.Print("h_strawHitChanPrimaries_V1_L0", xtitle='Straw Number For Hits By Primaries V1_L0', ytitle='events', outname = fname + '/h_strawHitChanPrimaries_V1_L0' )
    plots.Print("h_strawHitChanPrimaries_V1_L1", xtitle='Straw Number For Hits By Primaries V1_L1', ytitle='events', outname = fname + '/h_strawHitChanPrimaries_V1_L1' )

# Straw Number for Hits from Secondaries
    plots.Print("h_strawHitChanSecondaries_V0_L0", xtitle='Straw Number For Hits By Secondaries V0_L0', ytitle='events', outname = fname + '/h_strawHitChanSecondaries_V0_L0' )
    plots.Print("h_strawHitChanSecondaries_V0_L1", xtitle='Straw Number For Hits By Secondaries V0_L1', ytitle='events', outname = fname + '/h_strawHitChanSecondaries_V0_L1' )
    plots.Print("h_strawHitChanSecondaries_V1_L0", xtitle='Straw Number For Hits By Secondaries V1_L0', ytitle='events', outname = fname + '/h_strawHitChanSecondaries_V1_L0' )
    plots.Print("h_strawHitChanSecondaries_V1_L1", xtitle='Straw Number For Hits By Secondaries V1_L1', ytitle='events', outname = fname + '/h_strawHitChanSecondaries_V1_L1' )

# strawHitCountPerEventPrimaries
    plots.Print("h_strawHitCountPerEventPrimaries_V0_L0", xtitle='Straw Hit Count Per Event By Primaries V0_L0', ytitle='events', outname = fname + '/h_strawHitCountPerEventPrimaries_V0_L0' )
    plots.Print("h_strawHitCountPerEventPrimaries_V0_L1", xtitle='Straw Hit Count Per Event By Primaries V0_L1', ytitle='events', outname = fname + '/h_strawHitCountPerEventPrimaries_V0_L1' )
    plots.Print("h_strawHitCountPerEventPrimaries_V1_L0", xtitle='Straw Hit Count Per Event By Primaries V1_L0', ytitle='events', outname = fname + '/h_strawHitCountPerEventPrimaries_V1_L0' )
    plots.Print("h_strawHitCountPerEventPrimaries_V1_L1", xtitle='Straw Hit Count Per Event By Primaries V1_L1', ytitle='events', outname = fname + '/h_strawHitCountPerEventPrimaries_V1_L1' )

# h_strawHitCountPerEvent
    plots.Print("h_strawHitCountPerEvent_V0_L0", xtitle='Straw Hit Count Per Event By Primaries V0_L0', ytitle='events', outname = fname + '/h_strawHitCountPerEvent_V0_L0' )
    plots.Print("h_strawHitCountPerEvent_V0_L1", xtitle='Straw Hit Count Per Event By Primaries V0_L1', ytitle='events', outname = fname + '/h_strawHitCountPerEvent_V0_L1' )
    plots.Print("h_strawHitCountPerEvent_V1_L0", xtitle='Straw Hit Count Per Event By Primaries V1_L0', ytitle='events', outname = fname + '/h_strawHitCountPerEvent_V1_L0' )
    plots.Print("h_strawHitCountPerEvent_V1_L1", xtitle='Straw Hit Count Per Event By Primaries V1_L1', ytitle='events', outname = fname + '/h_strawHitCountPerEvent_V1_L1' )

# h_strawHitPPrimaries
    plots.Print("h_strawHitPPrimaries_V0_L0", xtitle='Straw Hit Proton Primaries V0_L0', ytitle='events', outname = fname + '/h_strawHitPPrimaries_V0_L0' )
    plots.Print("h_strawHitPPrimaries_V0_L1", xtitle='Straw Hit Proton Primaries V0_L1', ytitle='events', outname = fname + '/h_strawHitPPrimaries_V0_L1' )
    plots.Print("h_strawHitPPrimaries_V1_L0", xtitle='Straw Hit Proton Primaries V1_L0', ytitle='events', outname = fname + '/h_strawHitPPrimaries_V1_L0' )
    plots.Print("h_strawHitPPrimaries_V1_L1", xtitle='Straw Hit Proton Primaries V1_L1', ytitle='events', outname = fname + '/h_strawHitPPrimaries_V1_L1' )

# h_strawHitPSecondaries_V0_L1
    plots.Print("h_strawHitPSecondaries_V0_L0", xtitle='Straw Hit Proton Secondaries V0_L0', ytitle='events', outname = fname + '/h_strawHitPSecondaries_V0_L0' )
    plots.Print("h_strawHitPSecondaries_V0_L1", xtitle='Straw Hit Proton Secondaries V0_L1', ytitle='events', outname = fname + '/h_strawHitPSecondaries_V0_L1' )
    plots.Print("h_strawHitPSecondaries_V1_L0", xtitle='Straw Hit Proton Secondaries V1_L0', ytitle='events', outname = fname + '/h_strawHitPSecondaries_V1_L0' )
    plots.Print("h_strawHitPSecondaries_V1_L1", xtitle='Straw Hit Proton Secondaries V1_L1', ytitle='events', outname = fname + '/h_strawHitPSecondaries_V1_L1' )
    

# h_strawHitProtonSecondaries
    plots.Print("h_strawHitProtonSecondaries", xtitle='Straw Hit Proton Secondaries', ytitle='events', outname = fname + '/h_strawHitProtonSecondaries' )
