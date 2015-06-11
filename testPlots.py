#!/usr/bin/env python
#atlas_setup root
from ROOT import *

from Plotter import Plotter
from Sample import Sample
from Logging import *

testPlots = Sample( FileName = 'rootFiles/mtestGunAnalysis_siliconTruthSanityPlots.root', Type = 'h', Sumw2 = False, Label = 'silicon 1mm')

print SiSanity

SiSanity.Type2D = 'COLZ'
SiSanity.LineColour = 4


testSamples = [SiSanity]

plots = Plotter(samples)
plots.PlotLegend = False

# PER EVENT HISTOS

# NHits per event
plots.Print("h_siliconNHits",  xtitle='number of hits', ytitle='events', outname = 'plots/SiliconSanity/NHits')



#plots.PlotLegend = True
#plots.Print("h_siliconPx", xtitle='#mu p_{x} [mm]', ytitle='Events', outname = 'plots/SiliconSanity/tmp', xmin=-20, xmax=20)
