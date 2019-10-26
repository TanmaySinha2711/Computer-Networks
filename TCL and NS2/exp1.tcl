# create our simulator object
set ns [new Simulator]

# read TCP variant as first argument from cmd line
set tcp_variant [lindex $argv 0]
# read CBR rate as 2nd argument from cmd line
set cbr_rate [lindex $argv 1]

# Generate trace file
set tf [open ${tcp_variant}_output_${cbr_rate}.tr w]
$ns trace-all $tf

# Finish process to close all files and connections
proc finish {} {
    global ns tf
    close $tf
    exit 0
}

# create the 6 specified nodes
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]
set n6 [$ns node]

# create links between the nodes
$ns duplex-link $n1 $n2 10Mb 10ms DropTail
$ns duplex-link $n2 $n3 10Mb 10ms DropTail
$ns duplex-link $n3 $n4 10Mb 10ms DropTail
$ns duplex-link $n2 $n5 10Mb 10ms DropTail
$ns duplex-link $n3 $n6 10Mb 10ms DropTail

#Set Queue Size of link (n2-n3) to 10
$ns queue-limit $n2 $n3 10

#Give node position as per given diagram
$ns duplex-link-op $n1 $n2 orient right-down
$ns duplex-link-op $n2 $n3 orient right
$ns duplex-link-op $n2 $n5 orient left-down
$ns duplex-link-op $n3 $n4 orient right-up
$ns duplex-link-op $n6 $n3 orient left-up


# Setup a UDP connection from N2 to N3
set udp [new Agent/UDP]
$ns attach-agent $n2 $udp

#create n3 as traffic sink
set null_2 [new Agent/Null]
$ns attach-agent $n3 $null_2
$ns connect $udp $null_2
$udp set fid_ 1

# Setup a CBR over UDP connection
set cbr [new Application/Traffic/CBR]
$cbr attach-agent $udp
$cbr set type_ CBR
$cbr set packet_size_ 1000
$cbr set rate_ [lindex $argv 1]mb
$cbr set random_ false

# set TCP variant
if {$tcp_variant == "Tahoe"} {
	set tcp [new Agent/TCP]
} elseif {$tcp_variant == "Reno"} {
	set tcp [new Agent/TCP/Reno]
} elseif {$tcp_variant == "NewReno"} {
	set tcp [new Agent/TCP/Newreno]
} elseif {$tcp_variant == "Vegas"} {
	set tcp [new Agent/TCP/Vegas]
}

#create TCP connection from N1 to N4
$ns attach-agent $n1 $tcp
set tcp_sink [new Agent/TCPSink]
$ns attach-agent $n4 $tcp_sink
$tcp set fid_ 2
$ns connect $tcp $tcp_sink

# FTP flow from N1 to N4
set ftp [new Application/FTP]
$ftp attach-agent $tcp
$ftp set type_ FTP

#Schedule times for CBR and FTP agents
$ns at 0.1 "$cbr start"
$ns at 0.2 "$ftp start"
$ns at 9.9 "$ftp stop"
$ns at 10.0 "$cbr stop"

# Calling of Finish procedure after 10 ms
$ns at 10 "finish"

# run script
$ns run

