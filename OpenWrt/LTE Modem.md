# using LTE Modems with OpenWrt

OpenWrt supports LTE modems. Generally speaking you can use two types of hardware here

1. USB dongles
2. mPCIe modems

Both will be seen as USB devices!

The first decision that you need to make is which protocol you want to use. Basically you can chose between

1. QMI
2. MBIM
3. PPP (not recommended)
4. cdc-ether
5. ncm
6. ecm
7. RNDIS


What works best for your config depends on the modem. The Huawei USB dongles work best with cdc_ether, the Quectel Modems work well with QMI or MBIM. I have personally made best experience with QMI with my Quectel EP-06 modem.

## The challenge with LTE modems

If you browse the forums, then you will find a LOT of posts from various people who say that sometimes their config is working and sometimes not. Many say that it seems to be arbitrary. The real challenge here is that the LTE modems are in fact very often Android devices. That means that they do have a complete built in operating system and - very much like a phone or tablet - act as an independent system. The challenge here is that you never really know what STATE the LTE modem is in. 

- is it initialized?
- is it connected?
- does it have an IP address assigned?
- is it waiting for a PIN?

OpenWrt - very much like any other software - or I should rather say the scripts that come with the various software packages (QMI, MBIM etc...) try to figure out which state the modem is in and send commands to the modem based on their assumptions. That sometimes works and sometimes it doesn't. I'll show a brute-force solution further down this page.

## how to communicate with the modem

Depending on the protocol that you are using, there are various methods to communicate with the modem:

1. AT commands sent over the "serial" line (i.e. the emulated serial terminal on the /dev/ttyUSBx)
2. command line clients (mbimcli or qmicli)
3. The modem's web page (cdc_ether modems very often show a web interface on 192.168.1.1 or the like)

## how to start

Start with <a href=https://openwrt.org/docs/guide-user/network/wan/wwan/start>This article on the OpenWrt site</a> - you should get a rough idea which software modules to install etc. Unfortunately, there is no good LuCI interface for the modems like we would have it in <a href=https://www.ofmodemsandmen.com/>Rooter</a> or even <a href=https://www.openmptcprouter.com/>OpenMPTCPRouter</a> Generally, as a first step you should get to a point where you can use minicom or screen on /dev/ttyUSBx and send a simple AT Command such as ATZ and potentially have the modem reply with OK. For this typically you need to have some of the following software packages installed:

- kmod-usb-serial (mandatory)
- kmod-usb-acm
- kmod-usb-net-cdc-ether
- kmod-usb-net-cdc-mbim
- kmod-usb-net-cdc-ncm
- kmod-usb-net-qmi-wwan
- kmod-usb-serial-option
- kmod-usb-serial-qualcomm
- kmod-usb-serial-sierrawireless
- kmod-usb-serial-wwan
- kmod-usb-wdm

Depending on the protocol you would then need to install

- qmi-utils, uqmi, libqmi, luci-proto-qmi
- mbim-utils, umbim, libmbim

Now you can initialize the modem with something like

    qmicli --device=/dev/cdc-wdm0 --wds-start-network="ip-type=4,apn=web.vodafone.de" --client-no-release-cid

At that point you should then get a wwan0 device or the like which you can add to network - interfaces and also assign to the WAN zone.

Now - if you repeat the command or if your modem is in an unknown state, then you might get to the weird results listed above. For this I have added a kind of brute-force script to my environment that powers off the modem (to be sure that it is in a defined state) and initializes the connection. Powering off your modem is not trivial neither, because even rebooting your router might not disconnect the modem (you remember, it is a fully-blown Android device!). Luckily doing some research, it turned out that my Quectel Modem has an AT command to do this: `AT+QPOWD`

So what I did was that I modified the `/etc/crontabs/root` file to restart the network every 24 hours like this:

    00 3 * * * /etc/init.d/network restart && logger "network restarted" && /etc/ltemodem.sh

I do a restart of the network service followed by the execution of `/etc/ltemodem.sh` which has the following content:

    #!/bin/ash

    #########################################################################
    # LTE Modem init sequence
    #########################################################################

    # first down the wwan interface to make sure no uqmi running

    logger "LTE Modem init sequence started"

    ifdown WWAN

    # kill stale uqmi processes
    while pidof uqmi
        do kill `pidof uqmi`
        sleep 2
    done

    # reset Modem

    echo "AT+QPOWD" >/dev/ttyUSB2
    sleep 25

    # now wwan0 device gets created but needs to be enabled for raw IP

    ip link set dev wwan0 down
    echo Y > /sys/class/net/wwan0/qmi/raw_ip
    ip link set dev wwan0 up
    sleep 5

    # uqmi gets stuck so we use qmicli

    #uqmi -d /dev/cdc-wdm0 --start-network web.vodafone.de --autoconnect
    qmicli --device=/dev/cdc-wdm0 --wds-start-network="ip-type=4,apn=web.vodafone.de" --client-no-release-cid >/dev/null 2>&1

    # and finally up the interface

    ifup WWAN

    logger "LTE Modem init sequence finished"

This is far from being elegant, but **it works** reliably.

## preserve the config over upgrades

Unfortunately, your changes will be gone once you upgrade OpenWrt. In order to prevent this, add all files that you want to preserve over upgrades into the `/etc/sysupgrade.conf` file!

## more info

The Rooter project has a lot of know-how w/r to LTE modems. If you want to find scripts and init sequences for modems, then browse to <a href=https://github.com/ofmodemsandmen/RooterSource/tree/main/package/rooter>Their Github repo</a> in order to find some of the init scripts that they are using. Maybe you can recycle parts of it into your OpenWrt installation.