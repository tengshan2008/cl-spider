DB_IMAGE = biarms/mysql
DB_TAG = 5.7
DIR = /media/share/mysql

MYSQL_ROOT_PASSWORD = 123456
MYSQL_USER = user
MYSQL_PASSWORD = 803493
COMMAND = --character-set-server=utf8mb4 \
          --collation-server=utf8mb4_unicode_ci

WEB_IMAGE = tengshan/cl-spider
WEB_TAG = latest

.PHONY: build run mysql

build:
	docker build -t tengshan/cl-spider .

run:
	docker run -d \
	--publish 8888:8000 \
	--link mysql:mysql \
	--link minio:minio \
	${WEB_IMAGE}:${WEB_TAG}

mysql:
	docker run --name mysql \
	-p 3306:3306 \
	-v ${DIR}:/var/lib/mysql \
	-e MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD}" \
	-e MYSQL_USER="${MYSQL_USER}" \
	-e MYSQL_PASSWORD="${MYSQL_PASSWORD}" \
	-d ${DB_IMAGE}:${DB_TAG} ${COMMAND}
