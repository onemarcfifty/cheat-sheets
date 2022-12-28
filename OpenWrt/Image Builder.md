# Image Builder

The <a href=https://openwrt.org/docs/guide-user/additional-software/imagebuilder>OpenWrt Image Builder</a> can be used to create a custom firmware image without the need to compile from source.

## Obtaining the Image Builder from the OpenWrt web site

The OpenWrt CI (Continuous Integration) process puts a version of the image builder alongside every single firmware version on the OpenWrt download server. In order to obtain the Image builder, do a `wget` or `curl` from the respective address, e.g.:

    wget https://downloads.openwrt.org/releases/22.03.2/targets/x86/64/openwrt-imagebuilder-22.03.2-x86-64.Linux-x86_64.tar.xz

in order to obtain the release 22.03.2 version for x86. Then unpack the file and cd into the directory with the files:

    tar -xJf openwrt-imagebuilder-22.03.2-x86-64.Linux-x86_64.tar.xz
    cd openwrt-imagebuilder-22.03.2-x86-64.Linux-x86_64

## Using the image builder

The image builder comes with a Makefile that has the following rules implemented:

- help
- info
- clean
- image

typing `make info` will show the target architecture that it wants to build. If you want to build your image, then type `make image` . The target image will be located under the bin directory (e.g. `bin/targets/x86/64`) This image can now be uploaded to the LuCI "Flash Firmware" page of your router.

## Adapting the config for x86

The scripts/binaries are essentially the same for every architecture, the main difference is the `.config` file that contains information on how large the partitions have to be, which default packages to include etc. On x86 the default image size is set to 104 MB. If you have a lot of software packages on your x86 router, then that may be too small. The line that you need to change in the .config file is the following:

    CONFIG_TARGET_ROOTFS_PARTSIZE=104

If you want to change the partition to let's say 512 MB, then just type:

    sed -i s/CONFIG_TARGET_ROOTFS_PARTSIZE=104/CONFIG_TARGET_ROOTFS_PARTSIZE=512/ .config

## Building your custom Image


You can add multiple parameters to the make process (essentially all parameters that are defined in the .config file). One very useful parameter is the `PACKAGES` keyword which tells the image builder to pack specific software packages to the image. For example if you wanted to have the zabbix agent on the image then you could do something like 

    make image PACKAGES="base-files busybox dnsmasq dropbear firewall fstools ip6tables iptables iwinfo kernel kmod-ath9k kmod-gpio-button-hotplug kmod-ipt-offload kmod-usb-core kmod-usb-ledtrig-usbport kmod-usb-ohci kmod-usb2 libc libgcc logd mtd netifd odhcp6c odhcpd-ipv6only opkg ppp ppp-mod-pppoe swconfig uboot-envtools uci uclient-fetch urandom-seed urngd wpad-basic zabbix-agentd git zabbix-extra-mac80211 zabbix-extra-network zabbix-extra-wifi dropbearconvert"

## getting a list of packages on a running system

In order to get a copy-paste ready list of the installed packages from your router, you can use the opkg command (on the router). ssh into the router and type

    opkg --strip-abi list-installed | awk '{printf "%s ", $1}'

That will list all installed packages with the version numbers removed (`--strip-abi`) and the line breaks removed. The output can be copy-pasted into the `PACKAGES` argument of make.

## problems on older image builders (Version 19 and older)

If you are running the image builder for older versions, then you might get an error complaining about `SOURCE_DATE_EPOCH` at the end. A possible workaround is to simply add the parameter to the build process:

    make image PACKAGES="(whatever)" SOURCE_DATE_EPOCH=`date +'%s'`

That should build the image with no complains