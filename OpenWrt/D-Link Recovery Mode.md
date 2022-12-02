**Revert to Flash with D-Link Recovery console**

The D-Link modems have a built in recovery page. More details <a href=https://openwrt.org/docs/guide-user/installation/recovery_methods/d-link_recovery_gui>can be found here in the OpenWrt docs</a>

1. Download Firmware Version 1.00 from US D-Link site https://support.dlink.com/resource/PRODUCTS/DIR-3060-US/REVA/FIRMWARE/DIR-3060_REVA_FIRMWARE_v1.00B12.zip
2. decrypt Firmware file with https://github.com/0xricksanchez/dlink-decrypt
3. Using FireFox portable 3.5.6 (with wine) browse to 192.168.0.1, select decrypted firmware, do NOT click upload but leave window open. 
4. Restart Router in Recovery mode, NOW click on Upload 