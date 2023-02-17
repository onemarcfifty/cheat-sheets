## Some gotchas with NGINX

I always stumble over the same things when I set up NGINX. This is just to remind me to check:

- The resolver
- TLS version
- default site
- if is evil

### The resolver

NGINX does not use the system resolver (DNS) by default. You have to specify a line (example)

    resolver   127.0.0.53 ipv6=off;

This entry points to the resolver on the local host, but you could point it to any other server. I use the local resolver with `systemd-resolved` because it also resolves mDNS and `/etc/hosts` entries

### TLS Version

I strive to use TLSv1.3 only, however, if the last host in the forward chain is http only this doesn't work. Enabling TLSv1.2 seems to be a requirement:

    ssl_protocols TLSv1.2 TLSv1.3;

(can be specified on a per-site / per-Server level)

### Default Site / Sub directories

If you want to avoid people scanning your Web Server, then move your services into sub directories (e.g. `https://yourdomain.com/directory`) In order to make requests to the root fail, add a default server entry AS THE FIRST ENTRY in the enabled site config:

```
  server
  {
    listen  443 ssl;
    listen [::]:443 ssl;
    return(404);
  }
```

All following lines refer to the sub directory:

```
  location /yourdir
  {
    limit_except GET POST
    {
      deny  all;
    }
    include /etc/nginx/snippets/proxy.conf;
    proxy_pass  http://localhost:8080/;
  }
```


### "Certificate Sniffing" on the default site

Do not define one certificate for all enabled sites. Do it per service. Because if someone browsed to `https://yourIpAddress` (rather than the DNS Name) they would get an "unsafe" warning but could still see the certificate! (and hence browse to the correct server name)

Remediation: Reject TLS handshake on the default root and define Server names for all services:


```
# ##############################################################
# default server
# ##############################################################

server
{
    listen  443 ssl;
    listen [::]:443 ssl;
    return(404);

# in NGINX 1.19 and above we can specify to reject ssl handshake:

    ssl_reject_handshake on;

# in Versions below we just link to a (fake) self signed Cert that has no info about the real server name

ssl_certificate /etc/FAKEcert.pem;
ssl_certificate_key /etc/FAKEprivkey.pem;

}

# ##############################################################
# Real Server, only reachable with real address
# ##############################################################


server
{
  listen  443 ssl;
  listen [::]:443 ssl;

  server_name realserver.yourdomain.com;

  ssl_certificate /etc/letsencrypt/live/realserver.yourdomain.com/cert.pem;
  ssl_certificate_key /etc/letsencrypt/live/realserver.yourdomain.com/privkey.pem;

  location /RandomSubDirName
  {
    limit_except GET POST # or whatever (MKCOL, PROPERTIES, etc.)
    {
      deny  all;
    }
    include /etc/nginx/snippets/proxy.conf;
    proxy_pass  http://localhost:8080/;
  }
}

```

see also [this article on serverfault.com](https://serverfault.com/questions/373929/nginx-how-do-i-reject-request-to-unlisted-ssl-virtual-server)