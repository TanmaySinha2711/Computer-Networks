#!/usr/bin/env python
import os

# Create a list for all TCP variants
TCP_Variant = ['Tahoe', 'Reno', 'NewReno', 'Vegas']
command = "/course/cs4700f12/ns-allinone-2.35/bin/ns "

# run tcl script for all tcp variants for all rates by passing as args to cmd line
for variant in TCP_Variant:
    for rate in [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]:
        os.system(command + "exp1.tcl " + variant + " " + str(rate))


# calculate throughput of the setup
def get_throughput(variant, rate):
    # open tr output file generated from tcl file
    tcl_file_name = variant + "_output_" + str(rate) + ".tr"
    tcl_file = open(tcl_file_name)
    lines = tcl_file.readlines()
    tcl_file.close()

    sent = []
    received = []
    num_bytes = 0

    for line in lines:
        parse = line.split(" ")
        # note the time a packet in enqueued for node 1 to 2
        if parse[0] == '+' and parse[2] == '0' and parse[3] == '1' and parse[7] == '2':
            send_time = float(parse[1])
            sent.append(send_time)

    for line in lines:
        parse = line.split(" ")
        # note the time a packet in received for node 3 to 4
        if parse[0] == 'r' and parse[2] == '2' and parse[3] == '3' and parse[7] == '2':
            # calculate the total bytes received
            num_bytes += float(parse[5])
            received_time = float(parse[1])
            received.append(received_time)

    # calculate the rtt for this packet
    rtt = float(received.pop() - sent[0])
    # calculate throughput in megabits/second
    throughput = float((num_bytes * 8) / (1024 * 1024)) / rtt
    return throughput


# function to calculate drop rate
def get_packet_drop_rate(variant, rate):
    # open tr output file generated from tcl file
    tcl_file_name = variant + "_output_" + str(rate) + ".tr"
    tcl_file = open(tcl_file_name)
    lines = tcl_file.readlines()
    tcl_file.close()

    send_packet = 0
    receive_packet = 0
    for line in lines:
        parse = line.split(" ")
        if parse[7] == "2":
            if parse[0] == "+" and parse[2] == "0":
                send_packet = send_packet + 1
            if parse[0] == "r" and parse[3] == "3":
                receive_packet = receive_packet + 1

    # calculate packet drop rate
    packet_drop_rate = float(send_packet - receive_packet) / float(send_packet)
    # if no packets were sent do nothing
    if send_packet == 0:
        return 0
    else:
        return packet_drop_rate * 100


# function to calculate latency
def get_latency(variant, rate):
    # open tr output file generated from tcl file
    tcl_file_name = variant + "_output_" + str(rate) + ".tr"
    tcl_file = open(tcl_file_name)
    lines = tcl_file.readlines()
    tcl_file.close()

    # create two dictionaries for send time and receive time
    # (seq.no, time)
    send_time = {}
    received_time = {}

    round_trip_time = 0.0
    num_packets = 0

    for line in lines:
        parse = line.split(" ")
        if parse[7] == "2":
            if parse[0] == "+" and parse[2] == "0":
                # store sent packet's seq number and sent time
                send_time.update({parse[10]: parse[1]})
            if parse[0] == "r" and parse[3] == "0":
                # store received packet's seq number and sent time
                received_time.update({parse[10]: parse[1]})
    all_packets = {packet for packet in send_time.viewkeys() if packet in received_time.viewkeys()}
    for packet in all_packets:
        # calculate total RTT and pkt count
        beg = float(send_time[packet])
        end = float(received_time[packet])
        per_packet_rtt = float(end - beg)
        if per_packet_rtt > 0:
            round_trip_time += per_packet_rtt
            num_packets += 1

    if num_packets == 0:
        return 0
    else:
        return (round_trip_time / num_packets) * 1000


# write to output files
f1 = open('exp1_throughput.txt', 'w')
f2 = open('exp1_packet_drop_rate.txt', 'w')
f3 = open('exp1_latency.txt', 'w')

for cbr in [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]:
    throughput = ''
    packet_drop_rate = ''
    latency = ''
    for variant in TCP_Variant:
        throughput = throughput + '\t' + str(get_throughput(variant, cbr))
        packet_drop_rate = packet_drop_rate + '\t' + str(get_packet_drop_rate(variant, cbr))
        latency = latency + '\t' + str(get_latency(variant, cbr))

    f1.write(str(cbr) + throughput + '\n')
    f2.write(str(cbr) + packet_drop_rate + '\n')
    f3.write(str(cbr) + latency + '\n')

f1.close()
f2.close()
f3.close()

os.system("rm *.tr")
