FROM python:3.7.10-slim-buster AS compile-image

ADD sources.list /etc/apt/

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc

ENV VIRTURL_ENV=/opt/venv
RUN python3 -m venv $VIRTURL_ENV
ENV PATH="$VIRTURL_ENV/bin:$PATH"

RUN pip install --upgrade pip && pip install pip-tools
COPY ./requirements.in .
RUN pip-compile requirements.in > requirements.txt && pip-sync
RUN pip install -r requirements.txt

FROM python:3.7.10-slim-buster AS runtime-image

MAINTAINER tengshan2008

EXPOSE 8000

RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat-openbsd

COPY --from=compile-image /opt/venv /opt/venv

WORKDIR /usr/src/app

RUN addgroup --system user && adduser --system --no-create-home --group user
RUN chown -R user:user /usr/src/app && chmod -R 755 /usr/src/app

COPY ./entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

USER user

COPY . /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/opt/venv/bin:$PATH"

CMD ["gunicorn", "wsgi:application", "-c", "gunicorn.conf.py"]
