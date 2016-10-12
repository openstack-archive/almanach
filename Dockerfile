FROM python:3.5

ADD . /usr/local/src/
RUN cd /usr/local/src && \
    pip install -r requirements.txt && \
    python setup.py install && \
    mkdir -p /etc/almanach && \
    cp /usr/local/src/etc/almanach/almanach.docker.conf /etc/almanach/almanach.conf

USER nobody
