ip route
ip addr
ip link
ip neigh
ip rule

See iproute2 cheat sheet https://cheatography.com/tme520/cheat-sheets/iproute2/

ip rules in OpenWrt:

If you want to bypass the VPN for all traffic from that host, you can do it with routing rules and a custom routing table. An example would look like this (in `/etc/config/network`):  

`config route`  
`option table '10'`  
`option target '0.0.0.0/0'`  
`option interface 'wan'`

`config rule`  
`option in 'lan'`  
`option src '192.168.10.254/32'`  
`option lookup '10'`
