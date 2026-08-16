server {
	listen 80;
	listen [::]:80;
	server_name www.delfin.kyiv.ua;
	return 301 http://delfin.kyiv.ua$request_uri;
}

server {
	listen 80;
	listen [::]:80;
	server_name delfin.kyiv.ua;
	root /home/www/html/delfin.kyiv.ua;
	index idx.htm;

	# .htm вже мапиться на text/html стандартним /etc/nginx/mime.types,
	# окремий types{} тут не потрібен (і небезпечний: types{} в server-контексті
	# повністю замінює таблицю MIME-типів, а не доповнює її — без include
	# mime.types у http{} це зламало б Content-Type для css/js/картинок)
	ssi on;
	# ssi_types за замовчуванням уже text/html, окремо вказувати не треба

	# _parts/* — включення для SSI, а не самостійні сторінки.
	# internal, а не deny/404: deny блокує і внутрішні SSI-subrequest-и,
	# тобто зламав би самі #include virtual="/_parts/..."
	location ^~ /_parts/ {
		internal;
	}

	location / {
		try_files $uri $uri/ =404;
	}

	# статика без SSI-обробки — кешування на стороні клієнта
	location ~* \.(?:css|js|jpg|jpeg|png|gif|ico|ttf|woff2?)$ {
		expires 30d;
		access_log off;
	}

	error_log /var/log/nginx/delfin.kyiv.ua_error.log;
	access_log /var/log/nginx/delfin.kyiv.ua_access.log;
}
