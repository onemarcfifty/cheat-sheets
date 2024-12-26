
http://translate.google.com/translate?sl=auto&tl=en&u=https://sitetobetranslated.com/

​## NGINX config

```
​location / {
    ​if ($http_host ~* "(?<prefix>.*)(?<suffix>[^.]*)\.(?<tld>[^.]+)$") {
        set $translated_url "http://translate.google.com/translate?sl=auto&tl=en&u=http://$suffix.$tld$request_uri";
        ​if ($suffix.$tld != "translate.google.com") {
            rewrite ^/(.*)$ $translated_url break;
            proxy_pass $translated_url;
        }
    }
    proxy_pass http://$http_host;
}
```
