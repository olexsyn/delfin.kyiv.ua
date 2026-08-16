server {
    listen 80;
    listen [::]:80;
    server_name delfin.kyiv.ua www.delfin.kyiv.ua;
    return 301 https://delfin.kyiv.ua$request_uri;
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name delfin.kyiv.ua;

    root /home/www/delfin.kyiv.ua/html;
    index idx.htm;

    ssi on;
    # ssi_types за замовчуванням уже text/html, окремо вказувати не треба

    # _parts/* — включення для SSI, а не самостійні сторінки.
    # internal, а не deny/404: deny блокує і внутрішні SSI-subrequest-и,
    # тобто зламав би самі #include virtual="/_parts/..."
    location ^~ /_parts/ {
        internal;
    }

    location / {
        limit_req zone=general burst=15 nodelay;
        try_files $uri $uri/ =404;
    }

    # статика без SSI-обробки — кешування на стороні клієнта
    location ~* \.(?:css|js|jpg|jpeg|png|gif|ico|ttf|woff2?)$ {
        expires 30d;
        access_log off;
    }

    ssl_certificate /etc/letsencrypt/live/delfin.kyiv.ua/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/delfin.kyiv.ua/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name www.delfin.kyiv.ua;
    return 301 https://delfin.kyiv.ua$request_uri;

    ssl_certificate /etc/letsencrypt/live/delfin.kyiv.ua/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/delfin.kyiv.ua/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}
