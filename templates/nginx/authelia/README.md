# NGINX Authelia template

This template is meant to go on the Authelia server itself. It is assumed that the server name is `auth.yourdomain.com` (actually the config files youse `auth.*` so it should work with any domain).

In order to use them:

1. Stop NGINX `systemctl stop nginx`
2. remove the default web site of NGINX `rm /etc/nginx/sites-enabled/default`
3. copy the files to the right location:

    -  `proxy-snippet` => `/etc/nginx/snippets/proxy.conf`
    - `siteconf` => `/etc/nginx/sites-available/authelia.conf`
    - `ssl-snippet` => `/etc/nginx/snippets/ssl.conf`

(it is assumed that authelia listens on localhost port 9091)

(it is further assumed that the SSL certificates are in `/etc/authelia/certs/server.crt` and `/etc/authelia/certs/server.key`)

4. link authelia.conf to be the enabled web service `ln -s /etc/nginx/sites-available/authelia.conf /etc/nginx/sites-enabled/authelia.conf`
5. start NGINX `systemctl start nginx`

Authelia should now be available on port 443 of the server `auth.yourdomain.com`
