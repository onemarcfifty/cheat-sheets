## IPv6 cheat sheet ##

This cheat sheet goes together with videos that I have made.

1. [IPv6 from scratch - the very basics of IPv6 explained](https://youtu.be/oItwDXraK1M)
2. [IPv6 explained - SLAAC and DHCPv6 (IPv6 from scratch part 2)](https://youtu.be/jlG_nrCOmJc)
3. [IPv6 with OpenWrt](https://youtu.be/LJPXz8eA3b8)

### Address length and format ###

The IPv6 address is **128 bits** (i.e. 16 bytes) long and is written in **8 groups of 2 bytes** in hexadecimal numbers separated by colons:

    fddd:f00d:cafe:0000:0000:0000:0000:0001

Leading zeros of each block can be omitted, the above address can hence be written like this:

    fddd:f00d:cafe:0:0:0:0:1

We can abbreviate whole blocks of zeros with `::` and write:

    fddd:f00d:cafe::1

This can only be done *once* in order to void ambiguity:

    ff:0:0:0:1:0:0:1 (correct)
    ff::1:0:0:1 (correct)
    ff::1::1 (ambiguous, wrong)

(according to RFC 5952 ff:0:0:0:1::1 is not correct neither because the longest group of zeroes needs to be shortened)

### Protocols ###

| Number | Protocol  | Purpose                                   |
| ------ | --------- | ----------------------------------------- |
|  58    | IPv6-ICMP | Information, Error reporting, diagnostics |
|  6     | TCP       | Stateful - controls if packets arrived    |
| 17     | UDP       | Stateless - streaming applications etc.   |

### Ways to  assign IPv6 addresses ###

**Static** - fixed address  
**SLAAC** - Stateless Address Autoconfiguration (host generates itself)  
**DHCPv6** - Dynamic host configuration protocol (assigned by central server)  

### Scopes and special addresses ###

**GLOBAL** - everything (i.e. the whole internet)  
**UNIQUE LOCAL** - everything in our LAN (behind the internet gateway)  
**LINK LOCAL** - (will never be routed, valid in one collision domain, i.e. on the same switch)  

| range     | Purpose                                        |
| --------- | ---------------------------------------------- |
| ::1/128   | Loopback address (localhost)                   |
| ::/128    | unspecified address                            |
| 2000::/3  | GLOBAL unicast (Internet)                      |
| fc00::/7  | Unique-local (LAN)                             |
| fe80::/10 | Link-Local Unicast (same switch)               |

Always use the smallest possible scope for communication  
A host can have **multiple** addresses in different scopes

### Subnetting ###

| bits (MSB)      | Purpose                                        |
| --------------- | ----------------------- |
| First 48 bits:  | **Network** address     |
| Next 16 bits:   | **Subnet** address      |
| Last 64 bits:   | **Device** address      |

**Network+Subnet = Prefix**

The following address

    2003:1000:1000:1600:1234::1

would have the network `2003:1000:1000`, the subnet `1600`, so together the prefix `2003:1000:1000:1600`. If the ISP provider **delegated** a part of the prefix to me (e.g. `2003:1000:1000:1600/56`) then I could use the subnets from `2003:1000:1000:1600` to `2003:1000:1000:16FF` for my own purposes (i.e. define 256 subnets in this example)

### IPv6 addresses in URIs/URLs ###

Because IPv6 address notation uses colons to separate hextets, it is necessary to encase the address in square brackets in URIs. For example `http://[2a00:1450:4001:82a::2004]`. If you want to specify a port, you can do so as normal using a colon: `http://[2a00:1450:4001:82a::2004]:80`.

This cheat sheet goes together with videos that I have made. [The first video episode is here](https://youtu.be/oItwDXraK1M) (Second episode to come soon)

### Multicast ###

Communication from one node to another is called **unicast**. Communication from one node to many is called **multicast**

The following IPv6 multicast addresses may be used in in the link-local scope:

| range     | Purpose                                        |
| --------- | ---------------------------------------------- |
| ff02::1   | All Nodes in the network segment               |
| ff02::2   | All Routers in the network segment             |
| ff02::fb  | mDNSv6                                         |
| ff02::1:2 | All DHCP Servers and Agents                    |
| ff02::101 | All NTP Servers                                |

A full list [is maintained by the IANA](https://www.iana.org/assignments/ipv6-multicast-addresses/ipv6-multicast-addresses.xhtml)

You can actually ping these addresses, e.g. do a `ping ff02::1`

### ICMP types ###

ICMP does not use ports in order to communicate, but rather **types**. Critical/important types have numbers ranging from 1-127, while rather informational types have the numbers 128 and above. Each **type** can have subtypes or rather **codes** that can be used for further specifications.

Here are some frequently used IPv6 ICMP types:

| type | code | Purpose                                        |
| ---- | ---- | ---------------------------------------------- |
|   0  |      | reserved                                       |
|   1  |      | Destination Unreachable                        |
|   1  |   0  |   no route to destination                      |
|   1  |   2  |   beyond scope of source address               |
|   3  |      | Time Exceeded                                  |
|   3  |   0  |   hop limit exceeded in transit                |

| type | code | Purpose                                        |
| ---- | ---- | ---------------------------------------------- |
| 128  |   0  | Echo Request ("ping")                          |
| 129  |   0  | Echo Reply                                     |
| 133  |   0  | Router Solicitation                            |
| 134  |   0  | Router Advertisement                           |
| 135  |   0  | Neighbor Solicitation                          |
| 136  |   0  | Neighbor Advertisement                         |

A full list [is maintained by the IANA](https://www.iana.org/assignments/icmpv6-parameters/icmpv6-parameters.xhtml)

### DHCPv6 ###

IPv6 addresses can be distributed using the **dynamic host configuration protocol** or **DHCPv6**. If a host wants to obtain an IPv6 address over DHCPv6, then it sends out a **DHCP Solicitation** from UDP port 546 to port 547 on the DHCP multicast address `ff02::1:2`. The Server then replies to the client (from UDP port 547 to UDP port 546) with **DHCP advertisement**. The client then sends out a **DHCP request** and the server finishes with a **DHCP reply**

The DHCPv6 protocol is explained in more detail in [This Wikipedia Article](https://en.wikipedia.org/wiki/DHCPv6)

### DHCPv6 vs. SLAAC ###

Depending on how the router and the client are set up, the client can (and will) use both mechanisms (i.e. SLAAC and DHCP) for IPv6 address allocation. The following table shows the combinations:

<img src=dhcp_slaac.jpg>


### using WireShark ###

Here are some Wireshark filters for IPv6 ICMP, dhcpv6 and Ruter solicit/advertise:

Show ping and ping reply: `icmpv6 and (icmpv6.type==128) or (icmpv6.type==129)` <br>
Router solicit and advertise: `icmpv6 and (icmpv6.type==133) or (icmpv6.type==134)` <br>
Show dhcpv6 traffic: `dhcpv6` <br>
Router solicit/advertise and dhcpv6: `dhcpv6 or (icmpv6 and (icmpv6.type==134) or (icmpv6.type==133))` <br>

### Unicast vs. Multicast vs. Broadcast vs. Anycast ###

In all cases, there is only one sender sending out the information once. **Unicast** means that there is one receiver (point-to-point). **Broadcast** goes to everyone, like it or not. **Multicast** goes to everyone who has subscribed to the Multicast group. **Anycast** goes to the nearest node with that address, but multiple nodes with that address may exist. The delivery of all of these is handled by the switch or router. 
