# ftp-proxy

## Development
`pipenv run python -m aiohttp.web -H 0.0.0.0 -P 5000 ftp_proxy:init_func`

## Test
Public anonymous server
`curl -H "X-ftpproxy-host: speedtest.tele2.net" localhost:5000/ftp/ping`

Run local ftp server for testing
`twistd -n ftp --userAnonymous=yolo --root=/tmp`

Connect to it
`curl -H "X-ftpproxy-port: 2121" -H "X-ftpproxy-user: yolo" -H "X-ftpproxy-host: localhost" localhost:5000/ftp/ping`
