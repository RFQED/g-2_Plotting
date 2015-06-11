###mtestReadoutAnalysis_siliconDigitPlots.root

#!/usr/bin/env python
#atlas_setup root

from ROOT import *

from Plotter import Plotter
from Sample import Sample
from Logging import *
import array

test = True

if test:

    x = Sample( FileName = 'rootFiles/mtestReadoutAnalysis_siliconDigitPlots.root', Type = 'h', Sumw2 = False, Label = 'ReadoutAna_siliconTruthSanityPlots')

    print x

    x.Type2D = 'COLZ'
    x.LineColour = 4

    samples = [x]
    
    plots = Plotter(samples)
    plots.PlotLegend = False

    # PER EVENT HISTOS

    fname = "plots/mtestReadoutAnalysis/siliconDigitPlots"

# h_firstSiliconHitLayer
    plots.Print("rawTime",  xtitle='time', ytitle='events', outname = fname + '/rawTime')

# h_firstSiliconHitView
    plots.Print("f_scintTime",  xtitle='hitTime', ytitle='events', outname = fname + '/f_scintTime')
    
# h_firstSiliconHitView
    plots.Print("b_scintTime",  xtitle='hitTime', ytitle='events', outname = fname + '/b_scintTime')

# h_firstSiliconHitView
    plots.Print("calibTime",  xtitle='hitTime', ytitle='events', outname = fname + '/calibTime')

# h_firstSiliconHitView
    plots.Print("eventNumber",  xtitle='hitTime', ytitle='events', outname = fname + '/eventNumber')

# h_firstSiliconHitView
    plots.Print("eventNumber",  xtitle='hitTime', ytitle='events', outname = fname + '/eventNumber')




