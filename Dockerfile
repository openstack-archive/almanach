FROM python:2.7

RUN mkdir -p /opt/almanach/src
ADD almanach /opt/almanach/src/almanach
ADD setup.* /opt/almanach/src/
ADD README.md /opt/almanach/src/
ADD requirements.txt /opt/almanach/src/
ADD LICENSE /opt/almanach/src/
ADD almanach/resources/config/almanach.cfg /etc/almanach.cfg
COPY docker-entrypoint.sh /opt/almanach/entrypoint.sh

RUN cd /opt/almanach/src && \
    pip install -r requirements.txt && \
    PBR_VERSION=2.0.dev0 python setup.py install && \
    chmod +x /opt/almanach/entrypoint.sh

VOLUME /opt/almanach

USER nobody

ENTRYPOINT ["/opt/almanach/entrypoint.sh"]
