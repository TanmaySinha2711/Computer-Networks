# Create our Simulator object
set ns [new Simulator]

# read TCP variant from cmd line
set tcp_variant [lindex $argv 0]
# read Queue type from cmd line
set queue [lindex $argv 1]

# Generate trace file
set tf [open ${tcp_variant}_${queue}_output.tr w]
$ns trace-all $tf

# Finish process to close all files and connections
proc finish {} {
	global ns tf
	$ns flush-trace
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

# create links between the nodes based on queue type
if {$queue eq "DropTail"} {
	$ns duplex-link $n1 $n2 10Mb 10ms DropTail
	$ns duplex-link $n2 $n3 10Mb 10ms DropTail
	$ns duplex-link $n5 $n2 10Mb 10ms DropTail
	$ns duplex-link $n4 $n3 10Mb 10ms DropTail
	$ns duplex-link $n6 $n3 10Mb 10ms DropTail
} elseif {$queue eq "RED"} {
	$ns duplex-link $n1 $n2 10Mb 10ms RED
	$ns duplex-link $n2 $n3 10Mb 10ms RED
	$ns duplex-link $n5 $n2 10Mb 10ms RED
	$ns duplex-link $n4 $n3 10Mb 10ms RED
	$ns duplex-link $n6 $n3 10Mb 10ms RED
}

#set queue size
$ns queue-limit	$n1 $n2 10
$ns queue-limit	$n5 $n2 10
$ns queue-limit	$n2 $n3 10
$ns queue-limit	$n4 $n3 10
$ns queue-limit	$n6 $n3 10

# Setup a UDP connection from N5 to N6
set udp [new Agent/UDP]
$ns attach-agent $n5 $udp
set null [new Agent/Null]
$ns attach-agent $n6 $null
$udp set fid_ 1
$ns connect $udp $null

# Setup a CBR over UDP connection
set cbr [new Application/Traffic/CBR]
$cbr attach-agent $udp
$cbr set packet_size_ 1000
$cbr set type_ CBR
$cbr set rate_ 5mb

# Setup a TCP connection between n1 and n4
if {$tcp_variant eq "Reno"} {
	set tcp [new Agent/TCP/Reno]
	set sink [new Agent/TCPSink]
} elseif {$tcp_variant eq "SACK"} {
	set tcp [new Agent/TCP/Sack1]
	set sink [new Agent/TCPSink/Sack1]
}
$tcp set class_ 2
$ns attach-agent $n1 $tcp
$ns attach-agent $n4 $sink
$tcp set fid_ 2
$tcp set packetSize_ 1000
$tcp set maxcwnd_ 200
$tcp set window_ 150
$ns connect $tcp $sink

#setup a FTP agent
set ftp [new Application/FTP]
$ftp attach-agent $tcp

#Schedule times for CBR and FTP agents
$ns at 0.0 "$ftp start"
$ns at 5.0 "$cbr start"
$ns at 20.0 "$cbr stop"
$ns at 25.0 "$ftp stop"

#Call the finish procedure after 25 seconds
$ns at 25.0 "finish"

#Run the simulation
$ns run
