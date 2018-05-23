
FROM python:3.6

MAINTAINER Emile Caron

ARG VERSION

RUN pip install --no-cache gunicorn ftp-proxy==$VERSION

EXPOSE 2121

ENTRYPOINT ["gunicorn", "ftp_proxy:app"]
CMD ["--bind", "0.0.0.0:2121", "--worker-class", "aiohttp.GunicornWebWorker"]
