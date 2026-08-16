server {
    listen 80;
    listen [::]:80;
    server_name delfin.kyiv.ua www.delfin.kyiv.ua;
    root /home/www/delfin.kyiv.ua/html;
    index idx.htm;

    location / {
        try_files $uri $uri/ =404;
    }
}
