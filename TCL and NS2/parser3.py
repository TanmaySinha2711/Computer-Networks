#!/usr/bin/env python
import os

# array for tcp variants and queue types
tcp_var = ['Reno', 'SACK']
q_var = ['DropTail', 'RED']

cmd = "/course/cs4700f12/ns-allinone-2.35/bin/ns "

# execute the cmd by passing tcp variant and queue type
for var in tcp_var:
    for q in q_var:
        os.system(cmd + "exp3.tcl " + var + " " + q)


# calculate throughput of the setup
def get_throughput(variant, queue):
    # open tr output file generated from tcl file
    tcl_file_name = variant + "_" + queue + "_output.tr"
    tcl_file = open(tcl_file_name)
    lines = tcl_file.readlines()
    tcl_file.close()
    outfile = open('exp3_' + variant + '_' + queue + '_throughput.txt', 'w')

    tcp_sum = 0.0
    udp_sum = 0.0
    time = 0.0
    time_diff = 0.5

    for line in lines:
        parse = line.split(" ")
        if parse[0] == 'r' and parse[3] == '3' and parse[7] == '2':
            # calculate total bits for tcp setup
            tcp_sum += float(parse[5]) * 8
        if parse[0] == 'r' and parse[3] == '5' and parse[7] == '1':
            # calculate total bits for usp setup
            udp_sum += float(parse[5]) * 8

        if float(parse[1]) - time <= time_diff:
            pass
        else:
            throughput1 = float(tcp_sum / (time_diff * 1024 * 1024))
            throughput2 = float(udp_sum / (time_diff * 1024 * 1024))

            # calculate the throughput and write to file
            outfile.write(str(time) + "\t" + str(throughput1) + "\t" + str(throughput2) + "\n")
            time += time_diff
            tcp_sum = 0.0
            udp_sum = 0.0

    outfile.close()


# calculate latency of the setup
def get_latency(variant, queue):
    # open tr output file generated from tcl file
    tcl_file_name = variant + "_" + queue + "_output.tr"
    tcl_file = open(tcl_file_name)
    lines = tcl_file.readlines()
    tcl_file.close()

    outfile = open('exp3_' + variant + '_' + queue + '_latency.txt', 'w')

    # create dictionaries (seq.no, time)
    sent_time1 = {}
    recv_time1 = {}
    sent_time2 = {}
    recv_time2 = {}
    tot_rtt1 = 0.0
    num_packets1 = 0
    tot_rtt2 = 0.0
    num_packets2 = 0
    time = 0.0
    time_diff = 0.5

    for line in lines:
        parse = line.split(" ")
        # for tcp
        if parse[7] == "2":
            # check for sending and receiving time
            if parse[0] == "+" and parse[2] == "0":
                sent_time1.update({parse[10]: parse[1]})
            if parse[0] == "r" and parse[3] == "0":
                recv_time1.update({parse[10]: parse[1]})
        # for udp
        if parse[7] == "1":
            # check for sending and receiving time
            if parse[0] == "+" and parse[2] == "4":
                sent_time2.update({parse[10]: parse[1]})
            if parse[0] == "r" and parse[3] == "5":
                recv_time2.update({parse[10]: parse[1]})

        if float(parse[1]) - time <= time_diff:
            pass
        else:
            packets = {p for p in sent_time1.viewkeys() if p in recv_time1.viewkeys()}
            for p in packets:
                # calculate total RTT and number of packets
                beg = float(sent_time1[p])
                end = float(recv_time1[p])
                per_packet_rtt = float(end - beg)
                if per_packet_rtt > 0:
                    tot_rtt1 += per_packet_rtt
                    num_packets1 += 1

            packets = {p for p in sent_time2.viewkeys() if p in recv_time2.viewkeys()}
            for p in packets:
                # calculate total RTT and number of packets
                beg = float(sent_time2[p])
                end = float(recv_time2[p])
                per_packet_rtt = float(end - beg)
                if per_packet_rtt > 0:
                    tot_rtt2 += per_packet_rtt
                    num_packets2 += 1

            # calculate latency and write to file
            if num_packets1 == 0 or num_packets2 == 0:
                lat_1 = lat_2 = 0
            else:
                lat_1 = float(tot_rtt1 / num_packets1) * 1000
                lat_2 = float(tot_rtt2 / num_packets2) * 1000

            outfile.write(str(time) + '\t' + str(lat_1) + '\t' + str(lat_2) + '\n')
            time += time_diff
    outfile.close()


for v in tcp_var:
    for q in q_var:
        get_throughput(v, q)
        get_latency(v, q)

# remove all the .tr files
os.system('rm *.tr')
