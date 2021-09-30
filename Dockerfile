FROM centos:7

MAINTAINER Rudolf Stasilovich <rudiandradi@gmail.com>

ENV TZ=Europe/Moscow

CMD pip3 install -r requirements.txt
CMD run.py