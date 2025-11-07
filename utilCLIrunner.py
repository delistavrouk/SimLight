# -*- coding: utf-8 -*-

# Konstantinos Delistavrou 

# usage: python cliRunner.py

import subprocess
from datetime import datetime
from codeGusLibQueues import *

# version 2

# configuration parameters ----------------------------------------------

name, description, version, runs, X, nets, printout, keepeveryNreport, lamdagensaveload, lamdafile, pdfout, runConfigs, computername, progfolder, distributions, LimitConfigs, LatencyComponents, QHPpercentTrafficSplit, CheckForRevisits, HardLatencyCap_Q_HP, HardLatencyCap_Q_LP = readConfigNew("config.txt")

# end of configuration parameters ---------------------------------------

#LatencyComponents = LatencyComponents[0]
#LimitConfigs = LimitConfigs[0]

# using now() to get current time
current_time = datetime.now()
 
yr = str(current_time.year)
mo = str(current_time.month)
dy = str(current_time.day)
hr = str(current_time.hour)
mn = str(current_time.minute)
sc = str(current_time.second)

csv = yr+"-"+mo+"-"+dy+"_"+hr+"-"+mn+"-"+sc+"_Times"+str(runs)+name

fout = open(csv+".csv","a")
fout.write(description+"\n")
fout.write(len(description)*"~"+"\n")

LatencyTimeUnit4csv = 'micro'+"sec"

#create and write CSV caption

txtCaptions = setTextCaptions(LatencyTimeUnit4csv)

fout.write(txtCaptions)

fout.close()

totalruns = runs * len(distributions) * len(nets) * len(X) * len(runConfigs) * len(LimitConfigs) * len(LatencyComponents) * len(QHPpercentTrafficSplit)
print (f"Runs: {totalruns} = Distributions: {len(distributions)} x Networks: {len(nets)} x X: {len(X)} x Program configurations: {len(runConfigs)} x Configurations with limits: {len(LimitConfigs)} x Configurations for different latency of components: {len(LatencyComponents)} x Configurations with different splits of traffic: {len(QHPpercentTrafficSplit)} x Repetitions: {runs}.")

countallprogramsruns = 0

for countprogramruns in range(runs):
    for distribution in distributions:
        for net in nets:
            for x in X:
                for runconf in runConfigs:
                    program = runconf[0]
                    queue = runconf[1]
                    strategy = runconf[2]

                    for limconf in LimitConfigs:
                        fibersperlink = limconf[0]
                        wavelengthsperfiber = limconf[1]
                        wavelengthcapacity = limconf[2]

                        for latcomp in LatencyComponents:
                            latRouterPort = latcomp[0]
                            latTransponder = latcomp[1]

                            for QHPpercent in QHPpercentTrafficSplit:
                                
                                countallprogramsruns += 1                
                                
                                if keepeveryNreport < 0:
                                    keepreport = "keepDBonly"
                                elif keepeveryNreport == 0:
                                    keepreport = "removereport"
                                elif keepeveryNreport > 0:
                                    if countallprogramsruns > 0 and countallprogramsruns % keepeveryNreport == 0:
                                        keepreport = "keepreport"                        
                                
                                lamdaoutput = "Traffic-Requests-for_"+program+"_"+yr+"-"+mo+"-"+dy+"_"+hr+"-"+mn+"-"+sc+"_Net("+net+")"+"_Run("+str(countallprogramsruns)+")_"+"NumOfQueues("+queue+")_"+lamdafile
                                print ('Run',countallprogramsruns,'of',totalruns,': ~ Command: "python', program, net, x, csv, printout, lamdagensaveload, lamdaoutput, pdfout, queue, keepreport, computername, progfolder, distribution, strategy, fibersperlink, wavelengthsperfiber, wavelengthcapacity, latRouterPort, latTransponder, QHPpercent, CheckForRevisits, HardLatencyCap_Q_HP, HardLatencyCap_Q_LP, '"')
                                subprocess.run(["python ", program, net, x, csv, printout, lamdagensaveload, lamdaoutput, pdfout, queue, keepreport, computername, progfolder, distribution, strategy, fibersperlink, wavelengthsperfiber, wavelengthcapacity, latRouterPort, latTransponder, QHPpercent, CheckForRevisits, str(HardLatencyCap_Q_HP), str(HardLatencyCap_Q_LP)])
                                
