.PHONY: mysql

mysql:
	docker run --name mysql \
	-p 3306:3306 \
	-v /media/share/mysql:/var/lib/mysql \
	-e MYSQL_ROOT_PASSWORD="123456" \
	-e MYSQL_USER="user" \
	-e MYSQL_PASSWORD="803493" \
	-d biarms/mysql:5.7 \
	--character-set-server=utf8mb4 \
	--collation-server=utf8mb4_unicode_ci