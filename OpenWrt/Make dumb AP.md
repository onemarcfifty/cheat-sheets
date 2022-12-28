# Making a dumb AP

**convert a vanilla OpenWrt router into a dumb AP**

A "dumb AP" does not have routing functionality, i.e. it will act as an access point only. These are the steps that need to be taken:

1. Connect the network to the LAN interface
2. give the AP an address in the existing LAN (static or DHCP)
3. remove all DHCP, DNS, firewall

**in LuCi**

1. Network-Interfaces
2. Change IP of LAN interface or set protocol to DHCP client
3. DHCP Server tab, click "ignore interface"
4. Save/Apply, connect to the new IP of the router/AP
5. System-Startup
6. Stop and disable dnsmasq, firewall, odhcpd
7. Network-interfaces
8. remove WAN and WAN6
9. devices tab
10. optionally add the wan port to the lan bridge (br-lan)
11. save and apply

Now you can attach all Wifi interfaces to the LAN network

**scripted**

    #!/bin/ash

    # Turn an OpenWrt router with factory settings into a dumb access point
    # as outlined in https://openwrt.org/docs/guide-user/network/wifi/dumbap

    # use at your own risk !!!!
    # backup your router first !!!!
    # script expects factory settings !!!!


    # these services do not run on dumb APs
    for i in firewall dnsmasq odhcpd; do
    if /etc/init.d/"$i" enabled; then
        /etc/init.d/"$i" disable
        /etc/init.d/"$i" stop
    fi
    done


    # Now switch the lan interface to DHCP client

    uci set network.lan.proto='dhcp'
    uci delete network.wan
    uci delete network.wan6
    uci delete network.lan.ipaddr
    uci delete network.lan.netmask

    # change the host name to "WifiAP"

    uci set system.@system[0].hostname='WifiAP'


    echo '#####################################################################'
    echo 'the script has disabled firewall, dns and dhcp server on this device'
    echo 'and switched the protocol of the lan interface to dhcp client'
    echo 'you can now connect the LAN port of this device to the LAN port'
    echo 'of your main Router. Check the IP address of the WifiAP system'
    echo 'and connect to that new IP address in order to run the'
    echo 'second script. This device is now rebooting'
    echo 'the host name of the device is now WifiAP, so you might also'
    echo 'try ping WifiAP or ssh WifiAP or the like'
    echo '#####################################################################'

    # commit all changes

    uci commit

    # remove the firewall config

    mv /etc/config/firewall /etc/config/firewall.unused

    # reboot the device

    reboot

## Telling the AP that it is not a Router any more

With he above, the "dumb AP" does not have any router functionality any more. However - if you are using VLANs (like for example guest, iot, lan) then your Access point will have a leg in each of these networks. We therefore need to be sure that it does not act as a router and forward packages between the segments. In order to turn off IPv4 and IPv6 forwarding (and reply to the ff02::2 address and the like), add the following to `/etc/sysctl.conf` file:

    net.ipv4.ip_forward=0
    net.ipv6.conf.default.forwarding=0
    net.ipv6.conf.all.forwarding=0

