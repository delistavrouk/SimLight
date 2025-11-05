A simulation of RWA for IPoWDM optical backbone networks by Konstantinos Delistavrou.

Direct Bypass is the implementation of the power efficient algorithm by Shen & Tucker that does not apply traffic grooming and serves traffic in a single queue.

Multi-hop Bypass is the implementation of the power efficient algorithm by Shen & Tucker that applies traffic grooming and serves traffic in a single queue.

Hybrid bypass is a new algorithm that examines power efficiency in compination with low latency and uses two queues for serving traffic. 

Use the config.txt file to set runtime configuration and number of execution repetitions.
Then run on the command line: python utilCLIrunner_v2.py

<!--##Information about the command line parameters and example configurations in [CLIsyntaxDirect.md](./CLIsyntaxDirect.md), [CLIsyntaxMultihop.md](./CLIsyntaxMultihop.md), [CLIsyntaxHybrid.md](./CLIsyntaxHybrid.md).-->

[id1]: ## "spam proof e-mail address, type it yourself"
For assistance feel free to contact me at [delistaνrου(α)υοm.edυ.gr][id1]

This repository holds a snapshot of the stable version 0.193, while development actively continues.

Updated in November 2025 to...
	apply traffic blocking due to constraints (limited resources, wavelength continuity, hard latency cap)
	simulate the presence or absence of wavelength converters on network nodes
	realize variable traffic splits between the two input traffic queues
	penalize node revisits on traffic grooming
	support variable number of fibers per link, wavelength numbers per fiber, wavelength channel capacities
	