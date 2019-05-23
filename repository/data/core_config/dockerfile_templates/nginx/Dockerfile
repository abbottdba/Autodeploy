FROM nginx
MAINTAINER om@sinonet.ph
RUN apt-get update \
        && apt-get -y install vim rsync procps nginx-module-perl\
        && mkdir /web \
        && mkdir -p /bak/bin