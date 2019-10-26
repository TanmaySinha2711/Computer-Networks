Project 4: Raw Sockets

Team Name: rish_tan

Team Members:

1. Rishabh Agarwal (NUID: 001215275)

2. Tanmay Sinha    (NUID: 001821288)

Run the following command in ROOT or SUDO mode to run the project:
				./rawhttpget [url]
	Or if you do not want to modify IP tables run just the python program as
				python rawhttpget.py [url]

_____________________________________________________________________________
High Level approach:

The goal was to analyze working of IP, TCP and Ethernet protocol. 

We are using two type of sockets for our code.
Sender Socket: This is of type socket.socket (socket.AF_PACKET, socket.SOCK_RAW, socket.IPPROTO_RAW) 
Receiver Socket: this of the type socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)

We fetch the hostname from the URL specified on the command line. 

We then have a fucntion to fetch MAC address through ARP. The source MAC address is fetched through ifconfig command. 
For destination MAC address we find the gateway IP through route -n command. It is translated to destination hardware address. We then create a ARP header and encapsulate it in an ethernet frame and transmit it.
Further we receive the destination MAC address by waiting for a particular amount of time.

After that we find the source IP from ifconfig and destination IP by hostname.

Next we set random source ports and sequence numbers. We then created sender and receiver sockets.

We then built a TCP segment with checksum = 0 and SYN = 1. This header is then used for creating IP datagram. The IP header was correctly packed using struct library.

We then wait for an ACK from the server (See challenges faced). After getting ACK we send GET request to fetch page data.
______________________________________________________________________________________________
Challenges faced:

Initially our socket kept giving error on bind to 'eth0'. We then realized our VM uses 'ens33'.
We also faced minor difficulties in writing regex for fetching data from ifconfig and extracting valid hostname from url.
The next challenge we faced and still face is not getting the correct ACK from server. We keep retrieving the packets till the sequence number is Ack_num - 1 (till the most recent packet has been ACKed). However, this goes on forever. We never receive the desired ACK packet. As a result a handshake is not established.

Instead we shifted our focus on the extra credit ARP part. We faced some challenges while creating the ARP header. But, after monitoring packets in wireshark, in some tries we succeeded in retrieving the correct destination MAC address through ARP.
________________________________________________________________________________________________________
Individual work:

Tanmay worked on fetching IP and MAC address (without ARP).
Rishabh worked on wireshark monitoring (because of prior experience with wireshark). He then worked on the construction of TCP segment and IP header.
Tanmay worked on transmitting data and dismantling the ethernet frame created. 
We both worked on reception of packets from the server as we were facing many issues with that.
We then switched to the extra credit part of the assignment.

Extra Credit: Rishabh worked on the extra credit part by observing ARP packets in wireshark and extensive research on internet.
_________________________________________________________________________________________
Rework (changes made after consulting TA's:
Our program could not be run as the regular expression we used to check for URL did not accept the log file URL.
We have hard coded the 2mb log file's URL for now.

Right now we are able to get IP , TCP and ARP parts of the code working. After a successful TCP handshake we send a HTTP GET request to the server. However, we do not get anything back from it.

We tried many things but could not find a workaround

_____________________________________________________________________________________
References: 
1) https://stackoverflow.com/questions/3949726/calculate-ip-checksum-in-python
2) https://www.binarytides.com/raw-socket-programming-in-python-linux/
3) https://networkengineering.stackexchange.com/
	questions/3585/what-to-use-as-arp-request-target-hardware-address
4) https://www.geeksforgeeks.org/computer-network-arp-works/