#FROM python:3-alpine
FROM python:3-slim-buster

LABEL org.opencontainers.image.source https://github.com/SENERGY-Platform/device-management-service

#RUN apk --no-cache add git
RUN apt-get update && apt-get install -y git

WORKDIR /usr/src/app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD ["gunicorn", "-b", "0.0.0.0:80", "--workers", "1", "--threads", "4", "--worker-class", "gthread", "--log-level", "error", "app:app"]
