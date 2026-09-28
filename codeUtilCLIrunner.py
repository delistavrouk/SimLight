# -*- coding: utf-8 -*-

# Konstantinos Delistavrou 

# usage: python cliRunner.py

import subprocess
from datetime import datetime
#from codeGusLibQueues import *
from DCinc.codeGusLibQueOOP import *
import logging
import os

logging.basicConfig(
    filename=f"CLIRunner_{getTimeStampString()}_Events.log",   # Name of the output file
    filemode='a',                                              # 'a' to append to the file, 'w' to overwrite
    level=logging.DEBUG,                                       # Minimum level of messages to capture
    format='[%(asctime)s - %(levelname)s] %(message)s',        # Log format
    datefmt='%Y-%m-%d %H:%M:%S'                                # Timestamp format
)

# Gets the Current Working Directory of the terminal
dynamic_folder = os.getcwd()

# version 3: 21-6-2026

# configuration parameters ----------------------------------------------

#name, description, version, runs, X, nets, printout, keepeveryNreport, lamdagensaveload, lamdafile, pdfout,   \
#runConfigs, computername, progfolder, distributions, LimitConfigs, LatencyComponents, QHPpercentTrafficSplit,  \
#CheckForRevisits, HardLatencyCap_Q_HP, HardLatencyCap_Q_LP, virtWavCap, considerWCC, WavConvLatPow,             \
#KShortestPaths = readConfigNew("config.txt")

name, description, version, runs, X, nets, printout, keepeveryNreport, lamdagensaveload, lamdafile, pdfout,   \
runConfigs, computername, progfolder, distributions, LimitConfigs, LatencyComponents, QHPpercentTrafficSplit,  \
CheckForRevisits, HardLatencyCap_Q_HP, HardLatencyCap_Q_LP, virtWavCap, WavConvLatPow, KShortestPaths = readConfigNew("config.txt")


#print (f">>> lamdafile = {lamdafile}")

#22-6-2026 do not consider the progfolder but the current working directory instead
progfolder = dynamic_folder

# end of configuration parameters ---------------------------------------

#LatencyComponents = LatencyComponents[0]
#LimitConfigs = LimitConfigs[0]

csv = getTimeStampString()+"_Times"+str(runs)+name

fout = open(csv+".csv","a")
fout.write(description+"\n")
fout.write(len(description)*"~"+"\n")

LatencyTimeUnit4csv = 'micro'+"sec"

#create and write CSV caption

txtCaptions = setTextCaptions(LatencyTimeUnit4csv)

fout.write(txtCaptions)

fout.close()

totalruns = runs * len(distributions) * len(nets) * len(X) * len(runConfigs) * len(LimitConfigs) * len(LatencyComponents) * len(QHPpercentTrafficSplit) * len(WavConvLatPow) * len(KShortestPaths)
decor = "~"*99
print (decor); logging.info(decor)
msg = f"Runs: {totalruns} = Distributions: {len(distributions)} x Networks: {len(nets)} x X: {len(X)} x Program configurations: {len(runConfigs)} x Configurations with limits: {len(LimitConfigs)} x Configurations for different latency of components: {len(LatencyComponents)} x Configurations with different splits of traffic: {len(QHPpercentTrafficSplit)} x Configurations for pairs of latency and power consumption of wavelength converters: {len(WavConvLatPow)} x Number of K parameters for shortest paths: {len(KShortestPaths)} x Repetitions: {runs}."
print (msg); logging.info(msg)
print (decor); logging.info(decor)

decor = "- "*50

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

                                #18-8-2026
                                for WA_Lat_Pow in WavConvLatPow:
                                    WALat = WA_Lat_Pow[0]
                                    WAPow = WA_Lat_Pow[1]

                                    for KshortPath in KShortestPaths:
                                        K = int(KshortPath)

                                        countallprogramsruns += 1                
                                        
                                        if keepeveryNreport < 0:
                                            keepreport = "keepDBonly"
                                        elif keepeveryNreport == 0:
                                            keepreport = "removereport"
                                        elif keepeveryNreport > 0:
                                            if countallprogramsruns > 0 and countallprogramsruns % keepeveryNreport == 0:
                                                keepreport = "keepreport"                        
                                        
                                        #lamdaoutput = "Traffic-Requests-for_"+program+"_"+yr+"-"+mo+"-"+dy+"_"+hr+"-"+mn+"-"+sc+"_Net("+net+")"+"_Run("+str(countallprogramsruns)+")_"+"NumOfQueues("+queue+")_"+lamdafile
                                        if lamdagensaveload=="gensave":
                                            lamdaoutput = f"Traffic-Requests-for_{program}_{getTimeStampString()}_Net({net})_Run({countallprogramsruns}_NumOfQueues({queue})_{lamdafile}"
                                        elif lamdagensaveload=="load":
                                            lamdaoutput = f"{lamdafile}"
                                        #cmd = f"python {program} {net} {x} {csv} {printout} {lamdagensaveload} {lamdaoutput} {pdfout} {queue} {keepreport} {computername} {progfolder} {distribution} {strategy} {fibersperlink} {wavelengthsperfiber} {wavelengthcapacity} {latRouterPort} {latTransponder} {QHPpercent} {CheckForRevisits} {HardLatencyCap_Q_HP} {HardLatencyCap_Q_LP} {virtWavCap} {considerWCC} {WALat} {WAPow} {KShortestPaths}"
                                        cmd = f"python {program} {net} {x} {csv} {printout} {lamdagensaveload} {lamdaoutput} {pdfout} {queue} {keepreport} {computername} {progfolder} {distribution} {strategy} {fibersperlink} {wavelengthsperfiber} {wavelengthcapacity} {latRouterPort} {latTransponder} {QHPpercent} {CheckForRevisits} {HardLatencyCap_Q_HP} {HardLatencyCap_Q_LP} {virtWavCap} {WALat} {WAPow} {K}"
                                        msg = f"Run {countallprogramsruns} of {totalruns}: ~ Command: \"{cmd}\""
                                        print (msg); logging.info(msg)
                                        #subprocess.run(cmd)  
                                        subprocess.run(cmd.split())                                  
                                        print (decor); logging.info(decor)