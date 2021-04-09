#!/usr/bin/env python
import os

# Create a list for all TCP variants
tcp_var = ['RenoVsReno', 'NewRenoVsReno', 'VegasVsVegas', 'NewRenoVsVegas']
cmd = "/course/cs4700f12/ns-allinone-2.35/bin/ns "

# run tcl script for all tcp variants for all rates by passing as args to cmd line
for variants in tcp_var:
    for rate in [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]:
        variant = variants.split("Vs")
        os.system(cmd + "exp2.tcl " + variant[0] + " " + variant[1] + " " + str(rate))


# calculate throughput of the setup
def get_throughput(variant, rate):
    # open tr output file generated from tcl file
    tcl_file_name = variant + "_output_" + str(rate) + ".tr"
    tcl_file = open(tcl_file_name)
    lines = tcl_file.readlines()
    tcl_file.close()

    # setup 1
    sent1 = []
    received1 = []
    num_bytes1 = 0

    for line in lines:
        parse = line.split(" ")
        # note the time a packet in enqueued for node 1 to 2 for setup 1
        if parse[0] == '+' and parse[2] == '0' and parse[3] == '1' and parse[7] == '2':
            send_time = float(parse[1])
            sent1.append(send_time)

    for line in lines:
        parse = line.split(" ")
        # note the time a packet in received for node 3 to 4 for setup 1
        if parse[0] == 'r' and parse[2] == '2' and parse[3] == '3' and parse[7] == '2':
            # calculate the total bytes received
            num_bytes1 += float(parse[5])
            received_time = float(parse[1])
            received1.append(received_time)

    rtt1 = float(received1.pop() - sent1[0])
    # calculate throughput in megabits/second
    throughput1 = float((num_bytes1 * 8) / (1024 * 1024)) / rtt1

    # setup 2
    sent2 = []
    received2 = []
    num_bytes2 = 0

    for line in lines:
        parse = line.split(" ")
        # note the time a packet in enqueued for node 5 to 2 for setup 2
        if parse[0] == '+' and parse[2] == '4' and parse[3] == '1' and parse[7] == '3':
            send_time = float(parse[1])
            sent2.append(send_time)

    for line in lines:
        parse = line.split(" ")
        # note the time a packet in received for node 3 to 6 for setup 2
        if parse[0] == 'r' and parse[2] == '2' and parse[3] == '5' and parse[7] == '3':
            # calculate the total bytes received
            num_bytes2 += float(parse[5])
            received_time = float(parse[1])
            received2.append(received_time)

    rtt2 = float(received2.pop() - sent2[0])
    # calculate throughput in megabits/second
    throughput2 = float((num_bytes2 * 8) / (1024 * 1024)) / rtt2

    return str(throughput1) + "\t" + str(throughput2)


# function to calculate drop rate
def get_packet_drop_rate(variant, rate):
    # open tr output file generated from tcl file
    tcl_file_name = variant + "_output_" + str(rate) + ".tr"
    tcl_file = open(tcl_file_name)
    lines = tcl_file.readlines()
    tcl_file.close()

    # setup 1
    send_packet1 = 0
    receive_packet1 = 0
    for line in lines:
        parse = line.split(" ")
        if parse[7] == "2":
            if parse[0] == "+" and parse[2] == "0":
                send_packet1 = send_packet1 + 1
            if parse[0] == "r" and parse[3] == "3":
                receive_packet1 = receive_packet1 + 1

    # setup 2
    send_packet2 = 0
    receive_packet2 = 0
    for line in lines:
        parse = line.split(" ")
        if parse[7] == "3":
            if parse[0] == "+" and parse[2] == "4":
                send_packet2 = send_packet2 + 1
            if parse[0] == "r" and parse[3] == "5":
                receive_packet2 = receive_packet2 + 1

    # calculate packet drop rate for both setups
    packet_drop_rate1 = float(send_packet1 - receive_packet1) / float(send_packet1)
    packet_drop_rate2 = float(send_packet2 - receive_packet2) / float(send_packet2)
    if send_packet1 == 0 or send_packet2 == 0:
        return 0
    else:
        return str(packet_drop_rate1 * 100) + "\t" + str(packet_drop_rate2 * 100)


# function to calculate latency
def get_latency(variant, rate):
    # open tr output file generated from tcl file
    tcl_file_name = variant + "_output_" + str(rate) + ".tr"
    tcl_file = open(tcl_file_name)
    lines = tcl_file.readlines()
    tcl_file.close()

    # setup 1
    # create two dictionaries for send time and receive time
    # (seq.no, time)
    send_time1 = {}
    received_time1 = {}

    round_trip_time1 = 0.0
    num_packets1 = 0

    for line in lines:
        parse = line.split(" ")
        if parse[7] == "2":
            if parse[0] == "+" and parse[2] == "0":
                # store sent packet's seq number and sent time
                send_time1.update({parse[10]: parse[1]})
            if parse[0] == "r" and parse[3] == "0":
                # store received packet's seq number and sent time
                received_time1.update({parse[10]: parse[1]})
    all_packets1 = {packet for packet in send_time1.viewkeys() if packet in received_time1.viewkeys()}
    for packet in all_packets1:
        # calculate total RTT and pkt count
        beg = float(send_time1[packet])
        end = float(received_time1[packet])
        per_packet_rtt1 = float(end - beg)
        if per_packet_rtt1 > 0:
            round_trip_time1 += per_packet_rtt1
            num_packets1 += 1

    # setup 2
    # create two dictionaries for send time and receive time
    # (seq.no, time)
    send_time2 = {}
    received_time2 = {}

    round_trip_time2 = 0.0
    num_packets2 = 0
    for line in lines:
        parse = line.split(" ")
        if parse[7] == "2":
            if parse[0] == "+" and parse[2] == "0":
                # store sent packet's seq number and sent time
                send_time2.update({parse[10]: parse[1]})
            if parse[0] == "r" and parse[3] == "0":
                # store received packet's seq number and sent time
                received_time2.update({parse[10]: parse[1]})
    all_packets2 = {packet for packet in send_time2.viewkeys() if packet in received_time2.viewkeys()}
    for packet in all_packets2:
        # calculate total RTT and pkt count
        beg = float(send_time2[packet])
        end = float(received_time2[packet])
        per_packet_rtt2 = float(end - beg)
        if per_packet_rtt2 > 0:
            round_trip_time2 += per_packet_rtt2
            num_packets2 += 1
    # if no packets were received do nothing
    if num_packets1 == 0 or num_packets2 == 0:
        return 0
    return str(float((round_trip_time1 / num_packets1) * 1000)) + "\t" + str(
        float((round_trip_time2 / num_packets2) * 1000))


# write to files for each comparison setup
f1 = open('exp2_RenoVsReno_throughput.txt', 'w')
f2 = open('exp2_RenoVsReno_packet_drop_rate.txt', 'w')
f3 = open('exp2_RenoVsReno_latency.txt', 'w')
f4 = open('exp2_NewRenoVsReno_throughput.txt', 'w')
f5 = open('exp2_NewRenoVsReno_packet_drop_rate.txt', 'w')
f6 = open('exp2_NewRenoVsReno_latency.txt', 'w')
f7 = open('exp2_VegasVsVegas_throughput.txt', 'w')
f8 = open('exp2_VegasVsVegas_packet_drop_rate.txt', 'w')
f9 = open('exp2_VegasVsVegas_latency.txt', 'w')
f10 = open('exp2_NewRenoVsVegas_throughput.txt', 'w')
f11 = open('exp2_NewRenoVsVegas_packet_drop_rate.txt', 'w')
f12 = open('exp2_NewRenoVsVegas_latency.txt', 'w')

for cbr in [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]:
    for variant in tcp_var:
        if variant == "RenoVsReno":
            f1.write(str(cbr) + '\t' + str(get_throughput(variant, cbr)) + '\n')
            f2.write(str(cbr) + '\t' + str(get_packet_drop_rate(variant, cbr)) + '\n')
            f3.write(str(cbr) + '\t' + str(get_latency(variant, cbr)) + '\n')
        if variant == "NewRenoVsReno":
            f4.write(str(cbr) + '\t' + str(get_throughput(variant, cbr)) + '\n')
            f5.write(str(cbr) + '\t' + str(get_packet_drop_rate(variant, cbr)) + '\n')
            f6.write(str(cbr) + '\t' + str(get_latency(variant, cbr)) + '\n')
        if variant == "VegasVsVegas":
            f7.write(str(cbr) + '\t' + str(get_throughput(variant, cbr)) + '\n')
            f8.write(str(cbr) + '\t' + str(get_packet_drop_rate(variant, cbr)) + '\n')
            f9.write(str(cbr) + '\t' + str(get_latency(variant, cbr)) + '\n')
        if variant == "NewRenoVsVegas":
            f10.write(str(cbr) + '\t' + str(get_throughput(variant, cbr)) + '\n')
            f11.write(str(cbr) + '\t' + str(get_packet_drop_rate(variant, cbr)) + '\n')
            f12.write(str(cbr) + '\t' + str(get_latency(variant, cbr)) + '\n')

f1.close()
f2.close()
f3.close()
f4.close()
f5.close()
f6.close()
f7.close()
f8.close()
f9.close()
f10.close()
f11.close()
f12.close()

# remove all .tr files
os.system("rm *.tr")
