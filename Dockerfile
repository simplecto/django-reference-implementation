FROM python:3.12-slim

COPY requirements.txt /
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r /requirements.txt
RUN mkdir /app
COPY src/ app/

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY gunicorn_settings.py /gunicorn_settings.py

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

CMD ["gunicorn", "-c", "/gunicorn_settings.py", "wsgi:application"]
