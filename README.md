# ftp-proxy
Http proxy to interact with FTP servers

## Install
`git clone git@github.com:uptilab2/ftp-proxy.git`

## Usage
### Using the python client
See client repository `https://github.com/uptilab2/ftp-proxy-client`

### Using an http client
ftp-proxy can be used with any http client

#### Authentication headers
All api routes expect the same authentication headers

| Header | Content | Default |
|--------|---------|---------|
| `X-ftpproxy-host` | server host | No default, mandatory header |
| `X-ftpproxy-port` | server port | 21 |
| `X-ftpproxy-user` | login | anonymous |
| `X-ftpproxy-password` | password | |

#### Available routes

##### Ping (/ftp/ping)
Test connection to the remote FTP server
Returns HTTP 200 on success

##### LS (ftp/ls)
List the files on the ftp server
Optional parameters:
- path (string): path to list content. Defaults to "/"
- recursive (true/false): recurse down subdirectories. Defaults to "false"
- extension (string): list only files with matching extension if provided (example: ".py")

Response:
```javascript
{
    "files": ["file1.txt", "other.py", "folder/nested.txt"],
    "directories": ["folder", "folder/subfolder"]
}
```

##### Download (/ftp/download)
Download a file from the ftp server
Mandatory parameters:
- path (string): path to file to download


#### Errors
If an error occured on the proxy or the FTP server, the request will return a HTTP 400 json response with the following format
```javascript
{
    "error": "<DESCRIPTION>"
}
```

## Development
### Setup
- Clone this repository
- Install pipenv
- Run dev server: `pipenv run python -m aiohttp.web -H 0.0.0.0 -P 5000 ftp_proxy:init_func`

### Test
Public anonymous server
`curl -H "X-ftpproxy-host: speedtest.tele2.net" localhost:5000/ftp/ping`

Run local ftp server for testing
`twistd -n ftp --userAnonymous=yolo --root=/tmp`

Connect to it
`curl -H "X-ftpproxy-port: 2121" -H "X-ftpproxy-user: yolo" -H "X-ftpproxy-host: localhost" localhost:5000/ftp/ping`

### Upload to Pypi
```bash
pipenv run python setup.py sdist
pipenv run python setup.py bdist_wheel
```
