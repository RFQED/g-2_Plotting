#mtestReadoutAnalysis_strawReadoutSanityPlots.py

#!/usr/bin/env python
#atlas_setup root

from ROOT import *

from Plotter import Plotter
from Sample import Sample
from Logging import *
import array

test = True


if test:

    StrawSanity = Sample( FileName = 'rootFiles/mtestReadoutAnalysis_strawReadoutSanityPlots.root', Type = 'h', Sumw2 = False, Label = 'straws')

    print StrawSanity

    StrawSanity.Type2D = 'COLZ'
    StrawSanity.LineColour = 4

    samples = [StrawSanity]
    
    plots = Plotter(samples)
    plots.PlotLegend = False
    
    # PER EVENT HISTOS


    fname = "plots/mtestReadoutAnalysis/strawReadoutSanity"


## h_strawHitProtonSecondaries

# Hit times
    plots.Print("h_driftTimes",  xtitle='drift time', ytitle='events', outname = fname + '/h_driftTimes')


# first straw hit layer
    plots.Print("h_energy", xtitle='Energy', ytitle='events', outname = fname + '/h_energy' )

# first straw  hit view
    plots.Print("h_strawDigitTimes", xtitle='time', ytitle='events', outname = fname + '/h_strawDigitTimes' )

# first straw  hit view
    plots.Print("h_strawDigitTimes", xtitle='time', ytitle='events', outname = fname + '/h_strawHitTimes' )

