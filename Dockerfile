FROM python:3.7-slim-stretch

RUN set -ex \
    \
    && apt-get -y upgrade \
    && apt-get -y update \
    && apt-get -y install git \
    && apt-get clean

RUN apt-get update && apt-get install -y tzdata && rm /etc/localtime && \
ln -snf /usr/share/zoneinfo/Europe/Istanbul /etc/localtime && \
dpkg-reconfigure -f noninteractive tzdata && apt-get clean

WORKDIR /version-update

COPY /version-update.py .

CMD ["python", "/version-update.py"]
