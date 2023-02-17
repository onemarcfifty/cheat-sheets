## Multiple Services on one Docker host

Accessing multiple services on the same docker host can be cumbersome. Let's say you have 

- Portainer on port 9443
- Homer on port 8080
- Authelia on port 444

running on the same Docker Host. How would you access them ? You would need to browse to e.g.

  https://YOURDOCKERHOST:8080

for Homer etc. - not very nice. 

### Use DNS names

The first step is to set up Host names in your DNS for the services and have them point to your docker server, e.g.

- portainer.yourdomain.com
- auth.yourdomain.com
- homer.yourdomain.com

Now - how would we get rid of the port numbers ? The trick is to install an NGINX reverse proxy on your Docker host and have it point to the right backends with different `Server_Name` directives:

### Define various Servers with NGINX

The configuration files for the enabled Sites that NGINX serves are located in `/etc/nginx/sites-enabled` and typically are symlinks to config files in `/etc/nginx/sites-available`. Here's an example:


```
# ##############################################################
# NGINX Proxy setup
# use with authelia
# ##############################################################

# DNS Resolver setting
# I am using systemd-resolved on the host so that I can
# also resolve entries in the /etc/hosts file,
# but you can specify any DNS Server in your LAN

resolver                  127.0.0.53 ipv6=off;

# SSL certificate settings

ssl_certificate /etc/letsencrypt/live/YOURDOMAIN.COM/cert.pem;
ssl_certificate_key /etc/letsencrypt/live/YOURDOMAIN.COM/privkey.pem;
ssl_session_timeout 5m;


# #############################
# HOMER
# this is the default site - any
# hostname other than the following 
# will go to this site
# #############################

server
{
  listen  443 ssl;
  listen [::]:443 ssl;

  server_name homer.YOURDOMAIN.COM;

  location /
  {
    limit_except GET 
    {
      deny  all;
    }
    include /etc/nginx/snippets/proxy.conf;
    proxy_pass  http://localhost:8080/;
  }

}


# #############################
# docker host => portainer
# protected with authelia
# #############################

server 
{
  listen  443 ssl;
  listen [::]:443 ssl;
  
  server_name docker-host.YOURDOMAIN.COM;

  set $protectedhost https://127.0.0.1:9443;
  include /etc/nginx/snippets/authelia-location.conf;

  location / 
  {
    include /etc/nginx/snippets/proxy.conf;
    include /etc/nginx/snippets/authrequest.conf;
    proxy_pass  $protectedhost;
  }
}

# #############################
# authelia
# #############################

server
{
  listen  443 ssl;
  listen [::]:443 ssl;

  server_name auth.YOURDOMAIN.COM;

  location /
  {
    include /etc/nginx/snippets/proxy.conf;
    proxy_pass  https://localhost:444/;
  }

}
```

### Advantages of this solution

- All Services are available on the same port, but on different (virtual/DNS) hosts
- no need for IPVLAN or MACVLAN
- Non-SSL apps can be served over TLS if you provide NGINX with the right certificates
- you can enhance security by adding a default site as the first one (e.g. with a fake certificate to avoid sniffing etc.)
