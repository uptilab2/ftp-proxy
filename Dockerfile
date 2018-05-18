
FROM python:3.6-alpine

MAINTAINER Emile Caron


RUN pip install gunicorn ftp-proxy

EXPOSE 2121

ENTRYPOINT ["gunicorn", "ftp_proxy:app"]
CMD ["--bind", "0.0.0.0:2121", "--worker-class", "aiohttp.GunicornWebWorker"]
