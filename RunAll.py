import subprocess

subprocess.Popen("python mtestRecoAnalysis_SiliconRecoPlots.py", shell=True)
subprocess.Popen("python mtestReadoutAnalysis_strawTruthSanityPlots.py", shell=True)
subprocess.Popen("python mtestReadoutAnalysis_strawReadoutSanityPlots.py", shell=True)
subprocess.Popen("python mtestReadoutAnalysis_siliconDigitPlots.py", shell=True)
subprocess.Popen("python mtestRawAnalysis.py", shell=True)
subprocess.Popen("python mtestGunAnalysis_strawTruthSanityPlots.py", shell=True)
subprocess.Popen("python mtestGunAnalysis_siliconTruthSanityPlots.py", shell=True)



print "##### All Done #####"

