FROM arm32v7/python:3.7.10-slim-buster AS compile-image

ADD sources.list /etc/apt/

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ \
    libxml2 libxml2-dev python3-libxml2 libxslt1-dev python-libxslt1 zlib1g-dev libffi-dev

ENV VIRTURL_ENV=/opt/venv
RUN python3 -m venv $VIRTURL_ENV
ENV PATH="$VIRTURL_ENV/bin:$PATH"

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com

FROM arm32v7/python:3.7.10-slim-buster AS runtime-image

MAINTAINER tengshan2008

EXPOSE 8000

RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat-openbsd

RUN /bin/cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo 'Asia/Shanghai' > /etc/timezone

COPY --from=compile-image /opt/venv /opt/venv

WORKDIR /usr/src/app

RUN addgroup --system user && adduser --system --no-create-home --group user
RUN chown -R user:user /usr/src/app && chmod -R 755 /usr/src/app

USER user

COPY . /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/opt/venv/bin:$PATH"

ENTRYPOINT ["./startup.sh"]
