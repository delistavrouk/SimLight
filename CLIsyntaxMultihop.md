| Command line arguments | Value                             | Configuration file sections | Meaning                                               | Command example |
|------------------------|-----------------------------------|-----------------------------|-------------------------------------------------------|-----------------|
| argv[0]                | &lt;program name>                    |                             | (program name)                                        | python codeMultihopBypassQueuesRWA.py N6L8_ShnTckr_a.txt 0 testexperiment detailreport gensave lamda.txt pdfout 1 keepreport Desktop C:\\SimLight Uniform Classic1Q |
| argv[1]                | &lt;network>                         | [Nets_start]...[Nets_end]   | (network)                                             |                 |
| argv[2]                | &lt;X index>                         | [X]                         | (X index)                                             |                 |
| argv[3]                | &lt;experiment name for csv file>    | [Name]                      | (experiment name for csv file)                        |                 |
| argv[4]                | detailreport                      | [Printout]                  | (global printout)                                     |                 |
|                        | basicreport                       |                             | (no printout)                                         |                 |
| argv[5]                | gensave                           | [Lamda]                     | (save lamda matrix to text file)                      |                 |
|                        | load                              |                             | (load lamda matrix from text file)                    |                 |
| argv[6]                | &lt;filename for lamda matrix>       | [LamdaTextFile]             | (filename for lamda matrix)                           |                 |
| argv[7]                | pdfout                            | [PDFout]                    | (save web page to pdf)                                |                 |
|                        | nopdf                             |                             | (do not save web page to pdf)                         |                 |
| argv[8]                | &lt;number of Queues>                | [Queues]                    | (use 1queue or 2 queues)                              |                 |
| argv[9]                | keepreport                        | [KeepEveryNthReport]        | (keep detailreport, if any)                           |                 |
|                        | removepreport                     |                             | (do not keep detailreport, if any)                    |                 |
| argv[10]               | &lt;name of the computer>            | [ComputerName]              | (name of the computer)                                |                 |
| argv[11]               | &lt;program folder under the root    | [ProgramFolder]             | (program folder under the root (Win) or home (Lin)    |                 |
|                        | (Win) or home (Lin) directory>    |                             | directory)                                            |                 |
| argv[12]               | Uniform                           | [Distribution]              | (Uniform traffic demand random data distribution)     |                 |
|                        | Poisson                           |                             | (Poisson traffic demand random data distribution)     |                 |
| argv[13]               | Q0_75_Q1_25                       | [Strategy]                  | (scheduling strategy serve 75% of QHP and 25% of QLP) |                 |
|                        | Q0nextQ1                          |                             | (scheduling strategy serve 100% of QHP and then QLP)  |                 |
|                        | Q1nextQ0                          |                             | (scheduling strategy serve 100% of QLP and then QHP)  |                 |
