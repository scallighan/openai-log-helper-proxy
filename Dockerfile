FROM python:3.12.0-bullseye
#FROM openresty/openresty:focal

RUN apt-get -y install --no-install-recommends wget gnupg ca-certificates gcc && \
    wget -O - https://openresty.org/package/pubkey.gpg | apt-key add - && \
    codename=`grep -Po 'VERSION="[0-9]+ \(\K[^)]+' /etc/os-release` && \
    echo "deb http://openresty.org/package/debian $codename openresty" \
    | tee /etc/apt/sources.list.d/openresty.list && \
    apt-get update && \
    apt-get -y install openresty && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /var/run/openresty && \
    ln -sf /dev/stdout /usr/local/openresty/nginx/logs/access.log && \
    ln -sf /dev/stderr /usr/local/openresty/nginx/logs/error.log

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y && apt-get install --reinstall libc6-dev -y
ENV PATH="/root/.cargo/bin:${PATH}"

RUN mkdir -p /opt/loghelper
COPY loghelper/requirements.txt /opt/loghelper
RUN cd /opt/loghelper && pip install -r requirements.txt   

RUN wget https://raw.githubusercontent.com/openresty/docker-openresty/master/nginx.conf && \
    mv nginx.conf /usr/local/openresty/nginx/conf
COPY default.conf /etc/nginx/conf.d/default.conf

 

COPY entry.sh /opt
COPY loghelper/ /opt/loghelper

RUN touch /var/log/nginx_access.log
RUN touch /var/log/loghelper_openai.log

ENTRYPOINT [ "bash", "/opt/entry.sh" ]