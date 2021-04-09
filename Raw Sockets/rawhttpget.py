#! /usr/bin/env python
import subprocess
import socket
import sys
import time
import random
import re
import os
from struct import pack
from struct import unpack

# check if number of arguments is correct in cmd line
if len(sys.argv[0:]) != 2:
    print("Invalid number of arguments.")
    sys.exit()

link = sys.argv[1]

# extract hostname and path
if link.find('http://') != -1:
    try:
        # check if it's a valid hostname
        host_name = "david.choffnes.com"
        path = "/classes/cs4700sp17/2MB.log"
    except IndexError as e:
        host_name = re.findall('http://(.*)', link)[0]
        path = ""
else:
    print("hostname not found. Please check the url")
    sys.exit()


# function to get MAC address of a source and destination device
def fetch_mac_addr():
    hdw = 1  # for ethernet
    prot = 0x0800  # 2 for IPv4
    hdw_addr = 6
    prot_addr = 4
    op_code = 1  # 1 for ARP req

    # ifconfig = subprocess.check_output("/sbin/ifconfig")
    ifconfig = os.popen("/sbin/ifconfig").read()
    mac_addr = os.popen("ifconfig ens33| grep HWaddr | awk '{ print $5 }'").read()
    source_hdw_addr = mac_addr.replace(':', '').strip().decode('hex')
    # print(source_hdw_addr)

    source_ip = re.findall('inet addr:(.*?)\sB', ifconfig)[0]
    source_prot_addr = socket.inet_aton(source_ip)

    dest_hdw_addr = pack('!6B', int('FF', 16), int('FF', 16), int('FF', 16),
                         int('FF', 16), int('FF', 16), int('FF', 16))

    # fetch gateway ip for destination protocol address
    route = os.popen("/sbin/route -n").read()
    gateway_ip_addr = re.findall(r'0.0.0.0(.*)0.0.0.0', route)[0].strip()
    dest_prot_addr = socket.inet_aton(gateway_ip_addr)
    # print(socket.inet_ntoa(dest_prot_addr))

    # build ARP header by packing the desired values
    arp_header = pack('!HHBBH6s4s6s4s', hdw, prot,
                      hdw_addr, prot_addr, op_code,
                      source_hdw_addr, source_prot_addr,
                      dest_hdw_addr, dest_prot_addr)

    # encapsulate ARP header in an ethernet frame
    eth_header = pack('!6s6sH', dest_hdw_addr, source_hdw_addr, 0x0806)
    eth_frame = eth_header + arp_header

    # create AF_INET socket
    try:
        sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
    except socket.error as e:
        print("Error creating socket " + e.strerror)
        sys.exit()
    sock.bind(('ens33', socket.SOCK_RAW))
    sock.send(eth_frame)

    destination_mac = None
    while True:
        if destination_mac is not None:
            sock.close()
            break
        start_time = time.time()
        while destination_mac is None:
            cur_time = time.time()
            if cur_time - start_time > 100:
                sock.send(eth_frame)
                break
            destination_mac = sock.recvfrom(2048)[0][6:12]
    return source_hdw_addr, destination_mac


# functions to fetch source and destination IP addresses
def fetch_ip_addr(host):
    try:
        dest_ip = socket.gethostbyname(host)
    except socket.error as e:
        print("Error message: Invalid Hostname " + e.strerror)
        sys.exit()
    ifconfig = os.popen('/sbin/ifconfig').read()
    source_ip = re.findall('inet addr:(.*?)\sB', ifconfig)[0]
    return source_ip, dest_ip


# function to calculate the checksum
def fetch_checksum(expr):
    check_sum = 0  # init checksum
    i = 0
    count = len(expr)
    while count > 1:
        word = ord(expr[i]) + (ord(expr[i + 1]) << 8)  # fetch integer representation for expr
        i = i + 2
        check_sum = check_sum + word
        count = count - 2
    if count == 1:
        check_sum = check_sum + ord(expr[i])
    check_sum = (check_sum >> 16) + (check_sum & 0xffff)
    check_sum = check_sum + (check_sum >> 16)
    check_sum = ~check_sum & 0xffff  # 2s compliment
    return check_sum


# function which builds TCP segment based on parameters
def build_tcp_segment(source_port, seq, ack, data_flag, syn, ack_fl, fin, push,
                      data):  # source_port, sequence_num, 0, 0, 0, 1, 0, 0, data
    dest_port = 80  # for http
    offset = 5
    urg_pointer = 0
    syn_flag = syn
    fin_flag = fin
    ack_flag = ack_fl
    push_flag = push
    reset_flag = 0
    window = socket.htons(5840)
    chk_sum = 0

    all_flags = fin_flag
    all_flags += (syn_flag << 1)
    all_flags += (reset_flag << 2)
    all_flags += (push_flag << 3)
    all_flags += (ack_flag << 4)
    all_flags += (urg_pointer << 5)

    new_offset = (offset << 12) + 0 + all_flags
    urg_pointer = 0
    tcp_header = pack('!HHLLHHHH',
                      source_port, dest_port,
                      seq, ack,
                      new_offset, window,
                      chk_sum, urg_pointer)

    # if data is present append it to header length
    if data_flag == 1:
        header_length = len(tcp_header) + len(data)
    else:
        header_length = len(tcp_header)

    new_src_ip = socket.inet_aton(source_ip)
    new_dest_ip = socket.inet_aton(dest_ip)
    prot = socket.IPPROTO_TCP

    new_hdr = pack('!4s4sBBH', new_src_ip, new_dest_ip, 0, prot, header_length)

    if data_flag == 1:
        new_hdr = new_hdr + tcp_header + data
    else:
        new_hdr = new_hdr + tcp_header

    # calculate new checksum
    new_checksum = fetch_checksum(new_hdr)

    # build new header
    new_tcp_header = pack('!HHLLHH',
                          source_port, dest_port,
                          seq, ack,
                          new_offset, window) + pack('H', new_checksum) + pack('!H', urg_pointer)

    tcp_segment = new_tcp_header + data

    return tcp_segment, seq, ack


# function which builds IP datagram by encapsulating TCP segment in it
def build_ip_datagram(tcp_segment):
    version = 4  # ipv4
    header_length = 5
    version_header_length = (version << 4) + header_length
    service_type = 0
    total_length = len(tcp_segment) + 20
    pkt_ID = random.randrange(1500, 2700)
    frag_offset = 0
    ttl = 255
    prot = socket.IPPROTO_TCP
    checksum = 0
    ip_source_ip = socket.inet_aton(source_ip)
    ip_dest_ip = socket.inet_aton(dest_ip)

    header = pack('!BBHHHBBH4s4s',
                  version_header_length, service_type, total_length,
                  pkt_ID, frag_offset,
                  ttl, prot, checksum,
                  ip_source_ip, ip_dest_ip)

    # Calculate IP checksum
    ip_checksum = fetch_checksum(header)

    new_header = pack('!BBHHHBB',
                      version_header_length, service_type, total_length,
                      pkt_ID, frag_offset, ttl, prot) \
                 + pack('H', ip_checksum) + pack('!4s4s', ip_source_ip, ip_dest_ip)

    # IP datagram is created by putting TCP segment inside the IP header
    ip_datagram = new_header + tcp_segment

    return ip_datagram


# build ethernet frame by encapsulating IP datagram in it
def build_ethernet_frame(ip_datagram):
    eth_header = pack('!6s6sH', dest_mac, source_mac, 0x0800)
    return eth_header + ip_datagram


# transmit the built ethernet frame
def transmit(s, src_port, seq_num, ack_num, data_flag, ack_flag, syn_flag, push_flag, data, fin_flag):
    tcp_segment, tcp_seq_num, tcp_ack = build_tcp_segment(src_port, seq_num, ack_num,
                                                          data_flag, syn_flag, ack_flag,
                                                          fin_flag, push_flag, data)
    ip_datagram = build_ip_datagram(tcp_segment)
    eth_frame = build_ethernet_frame(ip_datagram)
    s.send(eth_frame)
    return tcp_seq_num, tcp_ack


# dismantle ethernet packet to get ip datagram and tcp segment
def dismantle_packet(s):
    while True:
        recv_data = s.recv(65000)
        eth_hdr = recv_data[:14]
        destination_mac, src_mac, frame_type = unpack('!6s6sH', eth_hdr)
        if frame_type == 0x0800:
            break

    ip_hdr = recv_data[len(eth_hdr):(len(eth_hdr) + 20)]

    unpacked_ip_hdr = unpack("!BBHHHBBH4s4s", ip_hdr)

    version_header_length = unpacked_ip_hdr[0]
    hdr_length = version_header_length & 0xF
    ip_hdr_length = hdr_length * 4

    tcp_hdr = recv_data[(len(eth_hdr) + ip_hdr_length):(len(eth_hdr) + ip_hdr_length + 20)]
    unpacked_tcp_header = unpack('!HHLLBBHHH', tcp_hdr)

    received_seq_num = unpacked_tcp_header[2]
    received_ack = unpacked_tcp_header[3]
    data_offset = unpacked_tcp_header[4]

    tcp_flags = unpacked_tcp_header[5]
    tcp_flags = bin(tcp_flags)

    fin_flag = tcp_flags[-1]

    tcp_hdr_length = data_offset >> 4
    data_offset = (len(eth_hdr) + ip_hdr_length + tcp_hdr_length * 4)
    data = recv_data[data_offset:]

    return received_seq_num, received_ack, data, fin_flag


# receive data from server
def receive(sender_socket, receiver_socket, seq_num, src_port, received_data):
    global receiver_seq_num
    receiver_ack_num = None
    while receiver_ack_num != seq_num + 1:
        receiver_seq_num, receiver_ack_num, data, fin_flag = dismantle_packet(receiver_socket)
        print(receiver_seq_num, receiver_ack_num)

    # perform handshake by sending ack to server
    syn = 0
    ack_flag = 1
    seq_num = receiver_ack_num
    ack = receiver_seq_num + 1
    psh = 0
    data_flag = 0
    new_seq_num, new_ack = transmit(sender_socket, src_port, seq_num, ack, data_flag, ack_flag, syn, psh, "", 0)
    print(new_seq_num, new_ack)
    print("NEW")

    # Send http GET request
    psh = 1
    ack_flag = 1
    data_flag = 1
    data = "GET " + path + " HTTP/1.1\r\nAccept: */*\r\nHost: " + host_name + "\r\nConnection: Keep-Alive\r\n\r\n"
    new_seq_num, new_ack = transmit(sender_socket, src_port, seq_num, ack, data_flag, ack_flag, syn, psh, data, 0)

    new_ack = seq_num + len(data)

    # get http response
    nack = None
    while new_ack != nack:
        nack_seq_num, nack, http_data, fin = dismantle_packet(receiver_socket)

    # Check if status code is 200
    if http_data.find("200 OK") != -1:
        received_data = received_data + http_data
        new_ack = nack_seq_num + len(http_data)

        # transmit (send_sock, src_port,seq_num, ack_num, data_flag, ack_flag, syn_flag,push_flag, data, fin_flag)
        new_seq, new_recvd_ack = transmit(sender_socket, src_port, nack, new_ack, 0, ack_flag, 0, 0, "", 0)
        while True:
            while send_new_ack != new_seq:
                new_seq, new_recvd_ack, new_recvd_data, fin = dismantle_packet(receiver_socket)

            received_data = received_data + new_recvd_data

            # calculate the new seq_num and ack number
            length_new_rec_data = len(new_recvd_data)
            new_ack = new_seq + length_new_rec_data

            # if fin is 1 then stop transmitting
            if fin == '1':
                # transmit (send_sock, src_port,seq_num, ack_num, data_flag, ack_flag, syn_flag,
                # push_flag, data, fin_flag)
                transmit(sender_socket, src_port, new_ack, new_seq + 1, 0, ack_flag, 0, 0, "", 1)
                sender_socket.close()
                break
            else:
                # transmit (send_sock, src_port,seq_num, ack_num, data_flag, ack_flag, syn_flag,
                # push_flag, data, fin_flag)
                new_seq, new_recvd_ack = transmit(sender_socket, src_port, new_recvd_ack, new_ack,
                                                  0, ack_flag, 0, 0, "", 0)

        receiver_socket.close()

        # store the html file
        expr = received_data.find("\r\n\r\n")
        log_file = received_data[expr + 4:]
        idx = path.find("/")
        if idx == -1:
            filename = "index.html"
        else:
            filename = path.split("/")[-1]

        f = open(str(filename), "w")
        f.write(log_file)
        f.close()
        sys.exit(0)
    else:
        print("error status on page")
        sys.exit(0)


source_ip, dest_ip = fetch_ip_addr(host_name)
source_mac, dest_mac = fetch_mac_addr()

# set random values for source port and sequence number
source_port = 4545 + random.randrange(0, 4500)
sequence_num = random.randrange(0, 50)
data = ""

# Create a sender side RAW socket for transmission
try:
    sender_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.IPPROTO_RAW)
except socket.error as e:
    print("Error found: " + e.strerror)
    sys.exit()
sender_socket.bind(('ens33', socket.SOCK_RAW))

# Create receiver side RAW socket to receive data
try:
    receiver_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.IPPROTO_TCP)
except socket.error as e:
    print("Error found: " + e.strerror)
    sys.exit()
receiver_socket.bind(('ens33', socket.SOCK_RAW))

# build tcp segment
TCP_segment, TCP_seq_num, TCP_ack_num = build_tcp_segment(source_port, sequence_num, 0, 0, 1, 0, 0, 0, data)

# Build ip datagram and put tcp segment inside it
IP_datagram = build_ip_datagram(TCP_segment)

# Build ethernet frame and put ip datagram inside it
Eth_frame = build_ethernet_frame(IP_datagram)
# print(Eth_frame)
# Start handshake by sending SYN to server
sender_socket.send(Eth_frame)

# get the ACK form server
receive(sender_socket, receiver_socket, TCP_seq_num, source_port, data)
