FROM arm32v7/python:3.7.10-slim-buster

# COPY sources.list /etc/apt/sources.list

COPY . /usr/src/app

RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/opt/venv/bin:$PATH"

CMD ["gunicorn", "wsgi:application", "-c", "gunicorn.conf.py"]