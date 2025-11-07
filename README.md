A simulation of RWA for IPoWDM optical backbone networks by Konstantinos Delistavrou.

codeHybridBypass.py: is the implementation of Hybrid bypass a new latency- and power-aware RWA algorithm for IPoWDM networks utilizing queues of high- and low-priority traffic demands. 

codeDirectBypass.py: is the implementation of Direct Bypass, the power efficient algorithm by G. Shen & R. S. Tucker [1]  that does not apply traffic grooming and serves traffic in a single queue.

codeMultiHopBypass.py: Multi-hop Bypass is the implementation of the power efficient algorithm by G. Shen & R. S. Tucker [1] that applies traffic grooming and serves traffic in a single queue.

codeHottestFirstAndComparison.py: is the implementation of Hottest-first and Comparison power and latency aware algorithm by C. Lee and J.-K. K. Rhee [2]

codeGusLibQueues.py is a library file

For each algorithm you need to utilize a network topology definition (as an input file)

N6L8_STnet_AllWavConv.txt: a small-scale network [1] with wavelength converters ([HasWavConv] has 1s)
N6L8_STnet_NoWavConv.txt: a small-scale network [1] without wavelength converters ([HasWavConv] has 0s)
N14L21_NSFnet_AllWavConv.txt: a medium-scale network [1] with wavelength converters ([HasWavConv] has 1s)
N14L21_NSFnet_NoWavConv.txt: a medium-scale network [1] without wavelength converters ([HasWavConv] has 0s)
N24L43_USnet_AllWavConv.txt: a large-scale network [1] with wavelength converters ([HasWavConv] has 1s)
N24L43_USnet_NoWavConv.txt: a large-scale network [1] with wavelength converters ([HasWavConv] has 0s)

The simulator exports results in a CSV file, a folder with detailed report, DB file, topologies


You may run each algorithm via the command line or use utilCLIrunner to run different configurations in batch mode.

For batch mode use the config.txt file to set runtime configuration and number of execution repetitions. Then run on the command line prompt > python utilCLIrunner.py

Examples of command lines to run the programs

python codeHybridBypass.py N6L8_STnet_AllWavConv.txt 9 Test_Run basicreport gensave TrafficRequests.txt nopdf 2 keepreport Laptop C:\SimLightRun Uniform Hybrid2Q 1  40  100 30  100 50 CheckForRevisits -1.0 -1.0

python codeDirectBypass.py N6L8_STnet_AllWavConv.txt 9 Test_Run basicreport gensave TrafficRequests.txt nopdf 1 keepreport Laptop C:\SimLightRun Uniform Direct1Q

python codeHottestFirstAndComparison.py N6L8_STnet_AllWavConv.txt 9 Test_Run basicreport gensave TrafficRequests.txt nopdf 1 keepreport Laptop C:\SimLightRun Uniform Hottest1Q 1  40  100

python codeMultiHopBypass.py N6L8_STnet_AllWavConv.txt 9 Test_Run basicreport gensave TrafficRequests.txt nopdf 1 keepreport Laptop C:\SimLightRun Uniform MultiHop1Q


[id1]: ## "spam proof e-mail address, type it yourself"
For assistance feel free to contact me at [delistaνrου(α)υοm.edυ.gr][id1]

This repository holds a snapshot of the stable version 2, while development actively continues.

Hybrid Bypass has been updated in November 2025 to:
- apply traffic blocking due to constraints (limited resources, wavelength continuity, hard latency cap)
- simulate the presence or absence of wavelength converters on network nodes
- realize variable traffic splits between the two input traffic queues
- penalize node revisits on traffic grooming
- support variable number of fibers per link, wavelength numbers per fiber, wavelength channel capacities

Comments and remarks are welcome.

Enjoy!	



[1] G. Shen and R. S. Tucker, “Energy-minimized design for IP over WDM networks,” Journal of Optical
Communications and Networking, vol. 1, no. 1, pp. 176–186, 2009.
[2] C. Lee and J.-K. K. Rhee, “Traffic grooming for ip-over-wdm networks: Energy and delay perspectives,” Journal
of Optical Communications and Networking, vol. 6, no. 2, pp. 96–103, 2014.