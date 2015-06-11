#!/usr/bin/env python
#atlas_setup root

from ROOT import *

from Plotter import Plotter
from Sample import Sample
from Logging import *
import array

test = True


if test:

    SiSanity = Sample( FileName = 'rootFiles/mtestGunAnalysis_siliconTruthSanityPlots.root', Type = 'h', Sumw2 = False, Label = 'silicon 1mm')

    print SiSanity

    SiSanity.Type2D = 'COLZ'
    SiSanity.LineColour = 4

    samples = [SiSanity]
    
    plots = Plotter(samples)
    plots.PlotLegend = False
    
    # PER EVENT HISTOS

# NHits per event
    plots.Print("h_siliconNHits",  xtitle='number of hits', ytitle='events', outname = 'plots/SiliconSanity/NHits')

# X Pos per event
    plots.Print("h_siliconXPos",  xtitle='hit position x [mm]', ytitle='events', outname = 'plots/SiliconSanity/localXPos')
    
# Y Pos per event
    plots.Print("h_siliconYPos",  xtitle='hit position y [mm]', ytitle='events', outname = 'plots/SiliconSanity/localYPos')
    
# Z Pos per event
    plots.Print("h_siliconZPos",  xtitle='hit position z [mm]', ytitle='events', outname = 'plots/SiliconSanity/localZPos')
    
# Px per event
    plots.Print("h_siliconPx",  xtitle='P_{x}', ytitle='events', outname = 'plots/SiliconSanity/Px')
    
# Py per event
    plots.Print("h_siliconPy",  xtitle='P_{y}', ytitle='events', outname = 'plots/SiliconSanity/Py')
    
# Pz per event
    plots.Print("h_siliconPz",  xtitle='P_{z}', ytitle='events', outname = 'plots/SiliconSanity/Pz')
    
# Hit times
    plots.Print("h_siliconHitTimes",  xtitle='Hit time [ms]', ytitle='events', outname = 'plots/SiliconSanity/HitTimes')
    
    
# PER LAYER HISTOS
    
# XY Pos histos
    plots.Print("firstLayer/h_siliconXY",  xtitle='hit position x [mm]', ytitle='hit position y [mm]', outname = 'plots/SiliconSanity/XY_layer1')
    plots.Print("secondLayer/h_siliconXY", xtitle='hit position x [mm]', ytitle='hit position y [mm]', outname = 'plots/SiliconSanity/XY_layer2')
    plots.Print("thirdLayer/h_siliconXY",  xtitle='hit position x [mm]', ytitle='hit position y [mm]', outname = 'plots/SiliconSanity/XY_layer3')
    plots.Print("fourthLayer/h_siliconXY", xtitle='hit position x [mm]', ytitle='hit position y [mm]', outname = 'plots/SiliconSanity/XY_layer4')
    
# XZ Pos histos
    plots.Print("firstLayer/h_siliconXZ",  xtitle='hit position x [mm]', ytitle='hit position z [mm]', outname = 'plots/SiliconSanity/XZ_layer1')
    plots.Print("secondLayer/h_siliconXZ", xtitle='hit position x [mm]', ytitle='hit position z [mm]', outname = 'plots/SiliconSanity/XZ_layer2')
    plots.Print("thirdLayer/h_siliconXZ",  xtitle='hit position x [mm]', ytitle='hit position z [mm]', outname = 'plots/SiliconSanity/XZ_layer3')
    plots.Print("fourthLayer/h_siliconXZ", xtitle='hit position x [mm]', ytitle='hit position z [mm]', outname = 'plots/SiliconSanity/XZ_layer4')
    
# YZ Pos histos
    plots.Print("firstLayer/h_siliconYZ",  xtitle='hit position y [mm]', ytitle='hit position z [mm]', outname = 'plots/SiliconSanity/YZ_layer1')
    plots.Print("secondLayer/h_siliconYZ", xtitle='hit position y [mm]', ytitle='hit position z [mm]', outname = 'plots/SiliconSanity/YZ_layer2')
    plots.Print("thirdLayer/h_siliconYZ",  xtitle='hit position y [mm]', ytitle='hit position z [mm]', outname = 'plots/SiliconSanity/YZ_layer3')
    plots.Print("fourthLayer/h_siliconYZ", xtitle='hit position y [mm]', ytitle='hit position z [mm]', outname = 'plots/SiliconSanity/YZ_layer4')
    
# NHits protons histos
    plots.Print("firstLayer/h_siliconNHits_protons",  xtitle='number of proton hits', ytitle='events', outname = 'plots/SiliconSanity/protonNHits_layer1')
    plots.Print("secondLayer/h_siliconNHits_protons", xtitle='number of proton hits', ytitle='events', outname = 'plots/SiliconSanity/protonNHits_layer2')
    plots.Print("thirdLayer/h_siliconNHits_protons",  xtitle='number of proton hits', ytitle='events', outname = 'plots/SiliconSanity/protonNHits_layer3')
    plots.Print("fourthLayer/h_siliconNHits_protons", xtitle='number of proton hits', ytitle='events', outname = 'plots/SiliconSanity/protonNHits_layer4')
    
# Total NHits per layer histos
    plots.Print("firstLayer/h_siliconNHits_layer",  xtitle='number of hits', ytitle='events', outname = 'plots/SiliconSanity/NHits_layer1')
    plots.Print("secondLayer/h_siliconNHits_layer", xtitle='number of hits', ytitle='events', outname = 'plots/SiliconSanity/NHits_layer2')
    plots.Print("thirdLayer/h_siliconNHits_layer",  xtitle='number of hits', ytitle='events', outname = 'plots/SiliconSanity/NHits_layer3')
    plots.Print("fourthLayer/h_siliconNHits_layer", xtitle='number of hits', ytitle='events', outname = 'plots/SiliconSanity/NHits_layer4')
    
# X Pos per layer histos
    plots.Print("firstLayer/h_siliconXPos_local",  xtitle='hit position x [mm]', ytitle='events', outname = 'plots/SiliconSanity/localXPos_layer1')
    plots.Print("secondLayer/h_siliconXPos_local", xtitle='hit position x [mm]', ytitle='events', outname = 'plots/SiliconSanity/localXPos_layer2')
    plots.Print("thirdLayer/h_siliconXPos_local",  xtitle='hit position x [mm]', ytitle='events', outname = 'plots/SiliconSanity/localXPos_layer3')
    plots.Print("fourthLayer/h_siliconXPos_local", xtitle='hit position x [mm]', ytitle='events', outname = 'plots/SiliconSanity/localXPos_layer4')
    
# Y Pos per layer histos
    plots.Print("firstLayer/h_siliconYPos_local",  xtitle='hit position y [mm]', ytitle='events', outname = 'plots/SiliconSanity/localYPos_layer1')
    plots.Print("secondLayer/h_siliconYPos_local", xtitle='hit position y [mm]', ytitle='events', outname = 'plots/SiliconSanity/localYPos_layer2')
    plots.Print("thirdLayer/h_siliconYPos_local",  xtitle='hit position y [mm]', ytitle='events', outname = 'plots/SiliconSanity/localYPos_layer3')
    plots.Print("fourthLayer/h_siliconYPos_local", xtitle='hit position y [mm]', ytitle='events', outname = 'plots/SiliconSanity/localYPos_layer4')
    
# Z Pos per layer histos
    plots.Print("firstLayer/h_siliconZPos_local",  xtitle='hit position z [mm]', ytitle='events', outname = 'plots/SiliconSanity/localZPos_layer1')
    plots.Print("secondLayer/h_siliconZPos_local", xtitle='hit position z [mm]', ytitle='events', outname = 'plots/SiliconSanity/localZPos_layer2')
    plots.Print("thirdLayer/h_siliconZPos_local",  xtitle='hit position z [mm]', ytitle='events', outname = 'plots/SiliconSanity/localZPos_layer3')
    plots.Print("fourthLayer/h_siliconZPos_local", xtitle='hit position z [mm]', ytitle='events', outname = 'plots/SiliconSanity/localZPos_layer4')
    
# Energy per layer
    plots.Print("firstLayer/h_Energy_layer",  xtitle='Particle energy [MeV]', ytitle='events', outname = 'plots/SiliconSanity/Energy_layer1')
    plots.Print("secondLayer/h_Energy_layer", xtitle='Particle energy [MeV]', ytitle='events', outname = 'plots/SiliconSanity/Energy_layer2')
    plots.Print("thirdLayer/h_Energy_layer",  xtitle='Particle energy [MeV]', ytitle='events', outname = 'plots/SiliconSanity/Energy_layer3')
    plots.Print("fourthLayer/h_Energy_layer", xtitle='Particle energy [MeV]', ytitle='events', outname = 'plots/SiliconSanity/Energy_layer4')

# Px per layer histos
    plots.Print("firstLayer/h_siliconPx_local",  xtitle='P_{x}', ytitle='events', outname = 'plots/SiliconSanity/Px_layer1')
    plots.Print("secondLayer/h_siliconPx_local", xtitle='P_{x}', ytitle='events', outname = 'plots/SiliconSanity/Px_layer2')
    plots.Print("thirdLayer/h_siliconPx_local",  xtitle='P_{x}', ytitle='events', outname = 'plots/SiliconSanity/Px_layer3')
    plots.Print("fourthLayer/h_siliconPx_local", xtitle='P_{x}', ytitle='events', outname = 'plots/SiliconSanity/Px_layer4')

# Py per layer histos
    plots.Print("firstLayer/h_siliconPy_local",  xtitle='P_{y}', ytitle='events', outname = 'plots/SiliconSanity/Py_layer1')
    plots.Print("secondLayer/h_siliconPy_local", xtitle='P_{y}', ytitle='events', outname = 'plots/SiliconSanity/Py_layer2')
    plots.Print("thirdLayer/h_siliconPy_local",  xtitle='P_{y}', ytitle='events', outname = 'plots/SiliconSanity/Py_layer3')
    plots.Print("fourthLayer/h_siliconPy_local", xtitle='P_{y}', ytitle='events', outname = 'plots/SiliconSanity/Py_layer4')

# Pz per layer histos
    plots.Print("firstLayer/h_siliconPz_local",  xtitle='P_{z}', ytitle='events', outname = 'plots/SiliconSanity/Pz_layer1')
    plots.Print("secondLayer/h_siliconPz_local", xtitle='P_{z}', ytitle='events', outname = 'plots/SiliconSanity/Pz_layer2')
    plots.Print("thirdLayer/h_siliconPz_local",  xtitle='P_{z}', ytitle='events', outname = 'plots/SiliconSanity/Pz_layer3')
    plots.Print("fourthLayer/h_siliconPz_local", xtitle='P_{z}', ytitle='events', outname = 'plots/SiliconSanity/Pz_layer4')
    

#plots.PlotLegend = True
#plots.Print("h_siliconPx", xtitle='#mu p_{x} [mm]', ytitle='Events', outname = 'plots/SiliconSanity/tmp', xmin=-20, xmax=20)
