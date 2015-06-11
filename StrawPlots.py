#!/usr/bin/env python
#atlas_setup root
from ROOT import *

from Plotter import Plotter
from Sample import Sample
from Logging import *
import array

test = False

if test:

    SiSanity = Sample( FileName = 'rootFiles/mtestGunAnalysis_siliconTruthSanityPlots.root', Type = 'h', Sumw2 = False, Label = 'silicon 1mm')

    print SiSanity

    SiSanity.Type2D = 'COLZ'
    SiSanity.LineColour = 4


    samples = [SiSanity]
    
    plots = Plotter(samples)
    plots.PlotLegend = False

else:
    Straw_1 = [21.9, 16.2, 26.7, 18.4, 18.0, 27.2, 28.3, 19.2, 46.4, 27.8, 22.1]
    Straw_2 = [20.9, 23.5, 56.4, 62.4, 21.9, 27.5, 47.5, 22.9, 33.0, 27.5, 68.4]
    Straw_3 = [29.6, 24.2, 50.6, 20.7, 32.9, 47.1, 20.8, 31.3, 35.3, 20.4]
    Straw_4 = [201, 19.8, 24.8, 22.6, 22.9, 23.0, 23.5, 26.6, 18.9, 32.1, 50.6]
    Straw_5 = [20.7, 21.8, 23.1, 26.1, 25.6, 24.3, 20.9, 24.9, 22.0, 22.8, 16.5]
    Straw_6 = [30.7, 26.5, 23.4, 37.7, 42.4, 25.9, 21.0, 26.8, 20.6, 23.0]
