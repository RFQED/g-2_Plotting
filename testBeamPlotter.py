#!/usr/bin/env python
#atlas_setup root

from ROOT import *
from Plotter import Plotter
from Sample import Sample
from Logging import *
import array
import subprocess #to be able to run bash commands in py



a = Sample(FileName = 'rootFiles/Sas/mtestRecoAnalysis_reconstructedTrackPlots.root',
            Type = 'e',
            Sumw2 = False,
            Label = 'recoTrack')

print a

# load a Tgraph from sample
h_recoTrack = a.Get("hitYTrack")

# inspect elements of Tgraph
for i in range(0, 10):

    #for i in range(0, h_recoTrack.GetN()):

    x, y = Double(0.0), Double(0.0)
    h_recoTrack.GetPoint(i, x, y)
    print "i {0}, x {1}, y {2}".format(i, x, y)

    
    #make your own canvas
    c1 = TCanvas("Canvas", "Canvas", 700, 500)
    c1.Clear()
    c1.SetFillColor(10)
    c1.SetFrameFillColor(10)
    
    # axis range and style
    xmin = -10.0
    xmax = 2000.0
    ymin = -5.0
    ymax = 5.0
    
    h_recoTrack.SetMarkerColor(2)
    h_recoTrack.SetMarkerSize(1.5)
    h_recoTrack.SetMarkerStyle(5)
    tmpx = h_recoTrack.GetXaxis().GetTitleSize()
    tmpy = h_recoTrack.GetYaxis().GetTitleSize()
    h_recoTrack.GetXaxis().SetTitleSize(1.45 * tmpx)
    h_recoTrack.GetYaxis().SetTitleSize(1.45 * tmpy)
    h_recoTrack.GetXaxis().CenterTitle(True)
    h_recoTrack.GetYaxis().CenterTitle(True)
    h_recoTrack.GetYaxis().SetTitleOffset(0.8)
    h_recoTrack.GetXaxis().SetTitleOffset(0.8)
    h_recoTrack.SetTitle(" ")
    h_recoTrack.GetXaxis().SetTitle("x pos of hit in track")
    h_recoTrack.GetYaxis().SetTitle("y pos of hit in track")
    
    
   # text = "ReconstructedTrack in y"
    
    h_recoTrack.GetXaxis().SetRangeUser(xmin, xmax);
    h_recoTrack.GetYaxis().SetRangeUser(ymin, ymax);
    h_recoTrack.Draw("AP")  #draw this first so that the range isn't altered
    
    
    outname = ("recoTrack")
    c1.Print(outname)

    # run bash command to convert ps to pdf
    bashCommand = "ps2pdf " + outname; 
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
