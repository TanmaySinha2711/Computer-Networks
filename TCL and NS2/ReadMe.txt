Project 3: Performance Analysis of TCP Variants


Team Name: rish_tan


Team Members:

1. Rishabh Agarwal (NUID: 001215275)

2. Tanmay Sinha    (NUID: 001821288)


Running each parser will execute the TCL files with all the required arguments. They do not need to be executed separately.
Execute in the following way: 	./parser<x>.py
												OR
								python parser<x>.py
							where x can take values (1, 2, 3) depending on the experiment
							Example: python parser1.py  or ./parser1.py

High Level Approach:
1) The project had 3 parts. 
2) In first part we compared the tcp variants in presence of congestion by altering the CBR.
3) In 2nd part we had to compare the fairness among various tcp variants under varying congestion.
4) in 3rd part we had to compare the queuing methods DropTail and RED for SACK and Reno variants for a constant CBR flow.
5) For each part we created a parser which functions similarly.	It just reads and parses required data for each experiment.
6) We then created a parser in python which automatically sends command line argument the tcl file and executes them. Then it parses each .tr file. Required data is parsed and used to calculate throughput, latency, and packet drop rate. The parser then deletes all the .tr files
7) We then created an excel spreadsheet of the results obtained and made graphs from the results 


Challenges faced:
1) We had no prior experience of working on TCL. The link in the references and the starter link given in project helped us a lot.
2) The next challenge faced was analyzing the trace file. We were also stuck when we saw packets being sent from node0 as we did not have a node0 in our setup. We then realized the count starts from node0.
3) We then figured out what each column in the trace file represents
4) The next challenge we faced was to parse the required data. Figuring out what data we required for each experiment took us the longest time

Overview of steps taken in testing the program:
1) A trace file was used to check the ns2 simulation
2) We verified the graph we plotted with the trace output


Distribution of work:
The tcl part was understood by both of us and coded by Rishabh. Both of them understood what had to be parsed and used for each experiment. Tanmay created the parser script as he had experience with parsing text files in python. Both of us evaluated and analyzed the results. Rishabh generated the graphs and worked on making the report with Tanmay.
