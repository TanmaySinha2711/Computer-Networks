#create a new simulator
set ns [new Simulator]

# Read the two TCP variants from cmd line
set tcp_variant1 [lindex $argv 0]
set tcp_variant2 [lindex $argv 1]

# Read CBR rate from cmd line
set cbr_rate [lindex $argv 2]

# Generate the trace file
set tf [open ${tcp_variant1}Vs${tcp_variant2}_output_${cbr_rate}.tr w]
$ns trace-all $tf

# Finish process to close all files and connections
proc finish {} {
	global ns tf tcp
	#$ns flush-trace
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

#Setup a CBR over UDP connection
set cbr [new Application/Traffic/CBR]
$cbr attach-agent $udp
$cbr set type_ CBR
$cbr set packet_size_ 1000
$cbr set rate_ ${cbr_rate}mb
$cbr set random_ false

# set TCP variant for first version
if {$tcp_variant1 == "Reno"} {
	set tcp1 [new Agent/TCP/Reno]
} elseif {$tcp_variant1 == "NewReno"} {
	set tcp1 [new Agent/TCP/Newreno]
} elseif {$tcp_variant1 == "Vegas"} {
	set tcp1 [new Agent/TCP/Vegas]
}

# create TCP connection from N1 to N4
#$tcp1 set class_ 2
$ns attach-agent $n1 $tcp1
set sink1 [new Agent/TCPSink]
$ns attach-agent $n4 $sink1
$ns connect $tcp1 $sink1
$tcp1 set fid_ 2

# set TCP variant for second version
if {$tcp_variant2 eq "Reno"} {
	set tcp2 [new Agent/TCP/Reno]
} elseif {$tcp_variant2 eq "Vegas"} {
	set tcp2 [new Agent/TCP/Vegas]
}

# create TCP connection from N5 to N6
$ns attach-agent $n5 $tcp2
set sink2 [new Agent/TCPSink]
$ns attach-agent $n6 $sink2
$ns connect $tcp2 $sink2
$tcp2 set fid_ 3

#setup a FTP Application
set ftp1 [new Application/FTP]
$ftp1 attach-agent $tcp1
$ftp1 set type_ FTP

set ftp2 [new Application/FTP]
$ftp2 attach-agent $tcp2
$ftp2 set type_ FTP

#Schedule events for the CBR and FTP agents
$ns at 0.1 "$cbr start"
$ns at 0.1 "$ftp1 start"
$ns at 0.1 "$ftp2 start"
$ns at 10.0 "$ftp2 stop"
$ns at 10.0 "$ftp1 stop"
$ns at 10.0 "$cbr stop"

#Call the finish procedure after 10ms
$ns at 10.0 "finish"

#Run the simulation
$ns run

