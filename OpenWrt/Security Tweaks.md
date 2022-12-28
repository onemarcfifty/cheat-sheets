# Some Tweaks to increase security of an OpenWrt device

## Port forwarding INSIDE the LAN for reverse proxy

Typically people use port forwarding (DNAT) in order to make services inside their IPv4 network available to the internet. In order to forward a port you would do the following in LuCi:

- go to Network-Firewall, select the "Port Forwards" tab.
- Add a rule, select the protocol, source zone and external port (i.e. the port that the forward will be listening on or rather that we will forward FROM)
- Set the destination zone and the inteernal IP and port (i.e. the IP and port that we will forward TO)

Save and apply. If you now connect to the "external" IPv4 and port, you will be DNATed ("forwarded") to the destination IPv4/port. This does not work with IPv6. For IPv6 you would use a simple traffic rule.

If you now wanted to use this in your internal LAN, e.g. have a reverse proxy server that sits in your MGMT VLAN and that should proxy all http traffic coming from let's say the LAN zone (for example to ask for a second factor of authentication or the like), you could also use this mechanism.

- Protocol: TCP
- Source Zone: LAN
- External Port: 80
- Destination Zone: MGMT
- Internal IP address: the IP of your Reverse proxy in the MGMT zone, e.g. 10.39.39.170 (assuming your MGMT has the subnet 10.39.39.0/24)
- Internal port: the reverse proxy port, e.g. 8080

Now you just need to make sure that this only triggers when someone wants to connect to the MGMT VLAN, therefore

- select the Advanced Settings tab
- Set the external IP address to the subnet of MGMT, in this case 10.39.39.0/24

Any connection going from the LAN to the MGMT segment on TCP port 80 will now be going over the reverse proxy. In the `/etc/config/firewall` this will look like this:

    config redirect
        option dest 'MGMT'
        option target 'DNAT'
        option name 'LAN PROXY http'
        list proto 'tcp'
        option src 'lan'
        option src_dip '10.39.39.0/24'
        option src_dport '80'
        option dest_ip '10.39.39.171'
        option dest_port '8080'

## Securing a "dumb AP" (device acting as Access point only, no routing)

Theoretically, you don't really need a firewall on a dumb AP. Theoretically. Let's assume that your dumb AP has the VLANS LAN, GUEST, IOT and MGMT. the MGMT interface shall be the interface that you will use to connect to the Webinterface and ssh etc. of your router, the other interfaces are unused. The Access Point shall only act as a bridge between the various Wi-Fi SSIDs and the corresponding VLANs. 

### assigning the services to a specific IP or interface 

What you do not want to happen is that Guests try to connect to the web interface of the AP for example. You could therefore have the LuCI web interface (`uhttpd`) and SSH (`dropbear`) listen only on the Management interface (let's assume our MGMT interface has the IP 10.10.30.123):

    uci set uhttpd.main.listen_http='10.10.30.123:80'
    uci set uhttpd.main.listen_https='10.10.30.123:443'
    uci set dropbear.@dropbear[0].Interface='MGMT'
    uci commit
    /etc/init.d/uhttpd restart
    /etc/init.d/dropbear restart

If you now do a `netstat -tulpn` then the processes should only be listening on the right interface/IP. This process does however have a challenge: If your AP obtains its IP address over DHCP, and if the address has not been obtained at the moment that LuCI wants to start, then your web interface won't be available. You would have to ssh into the router and do a `/etc/init.d/uhttpd start` manually. Note that you can not bind uhttpd to an interface, but rather to an IP address only. Dropbear can be bound to an interface. Another challenge is that if you use DHCP and the dnsmasq process of your main router is down for some reasons, then your interface won't get an IP address at all and the device is not reachable any more.

### Setting all unused interfaces to "unmanaged"

Your network interfaces generally have a static IP address or a dynamic IP address which they receive over DHCP. If you want to hide your access points in the guest and IOT network for example, then set the protocol of those interfaces to "unmanaged". This way the device will be invisible in the corresponding network. You will howevr need at least one interface (MGMT in the above example) that has an IP address in order to be able to manage the device.

### Challenges with IPv6

Even if you set an interface's protocol to "unmanaged", the device wil still get a Link Local IPv6 address (typically fe80::something). So a malicious attacker could still reach the device using that address. In order to switch off even the link local address on a device, you need to go to network-interfaces,then the "devices" tab, edit the corresponding device and untick the "enable IPv6" check box. In UCI you could do this like this:

    uci set network.@device[n].name='wlan2'
    uci set network.@device[n].ipv6='0'
    uci commit

I have however observed that restarting the Wifi does re-assign the Locla Link address, even if the box is unchecked.

### Activating the firewall on a dumb AP

The easiest way that I have found to secure a dumb AP is to use the firewall. Unlike a firewall on an internet gateway, you would not use zones here. That should be managed by the main router. We just want to make sure that the AP is only reachable on one interface (in this example from the Management interface which is linked to the device br-mgmt)

**in LuCI**

- go to Network-Firewall and delete all zones
- Set the default policies to INPUT:DROP, OUTPUT:ACCEPT, FORWARD:DROP
- save, but do not save and apply yet
- create a Traffic rule: Allow TCP, UDP, ICMP from all zones to the device
- on the "advanced settings" tab of the rule, select Match Device: "Inbound device" 
- Set the "Device name" to your management interface (e.g. br-mgmt)
- save and apply

**Command line**

your `/etc/config/firewall` should have the following content:

    config defaults
	    option output 'ACCEPT'
	    option synflood_protect '1'
	    option forward 'DROP'
	    option drop_invalid '1'
	    option input 'DROP'

    config include
	    option path '/etc/firewall.user'

    config rule
	    option name 'allow mgmt'
	    option src '*'
	    option target 'ACCEPT'
	    option direction 'in'
	    option device 'br-mgmt'
	    list proto 'tcp'
	    list proto 'udp'
	    list proto 'icmp'

then restart the firewall `/etc/init.d/firewall restart`

Now you can have your processes (uhttpd, dropbear etc.) listen on 0.0.0.0 and :: but the device will only be reachable from the br-mgmt device.

## IPv6 Subnet masks

If you use IPv6 but you do not have a constant IPv6 prefix (i.e. your ISP gives you a different IPv6 prefix every now and then), then it's quite a challenge to write Firewall rules (because your prefix never is the same). I use DHCP for IPv4 and IPv6 and make sure that my devices get assigned the right subnet and Address Suffix in IPv6. In this case, the sshserver has an IPv4 address of 10.39.39.135 and is in the MGMT subnet/VLAN. IPv6 wise this will always be the 0f subnet and have the last digits of the IPv4 address in IPv6 (e.g. 2003:de:abcd:dd**0f**::**135**). In order to apply a rule to a variable prefix, we can use the following addressing scheme:

    config rule
        list proto 'tcp'
        option src 'lan'
        option dest 'MGMT'
        option target 'ACCEPT'
        option dest_port '22'
        option name 'LAN - Allow sshserver'
        list dest_ip '10.39.39.135'
        list dest_ip '::0f:0:0:0:135/::ff:ffff:ffff:ffff:ffff'

The bitmask (`::ff:ffff:ffff:ffff:ffff`) will only look at the last 72 bits of the address, i.e. 16 bits of the subnet and the host address. The prefix can change but the rule will always apply.
