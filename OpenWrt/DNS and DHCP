### MX Record Configuration in Dnsmasq

If you want to add an mx record for a domain with dnsmasq, then just add these lines into the dnsmasq main configuration file (/etc/dnsmasq.conf)
```
mx-host=example.com,mail1.example.com,10
mx-host=example.com,mail2.example.com,20
```

The above config will add 2 MX records for the domain example.com with priority values 10 for mail1.example.com and 20 for mail2.example.com

### List of all DHCP Clients (for Zabbix sync)

```
# Sync OpenWrt dhcp to zabbix
sudo ubus call uci get '{"config": "dhcp", "type": "host"}'

