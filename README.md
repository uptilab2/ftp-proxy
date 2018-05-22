# ftp-proxy ![travis](https://travis-ci.com/uptilab2/ftp-proxy.svg?branch=master)
Http proxy to interact with FTP servers

## Install
`pip install ftp-proxy`

## Deployment
Use the provided [docker image](https://hub.docker.com/r/emilecaron/ftp-proxy)

## Usage
### Using the python client
See [client repository](https://github.com/uptilab2/ftp-proxy-client)

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
["/file1.txt", "/other.py", "/folder", "/folder/nested.txt", "/folder/subfolder"]
```

##### Download (/ftp/download)
Download a file from the ftp server
Mandatory parameters:
- path (string): path to file to download

##### SFTP support
SFTP support API is roughly the same as ftp, and can be achieved by switching the url prefixes from ftp to sftp
The following features are not yet available for SFTP:
- recursive listing
- extension filtering

#### Errors
If an error occured on the proxy or the FTP server, the request will return a HTTP 400 json response with the following format
```javascript
{
    "error": "<DESCRIPTION>"
}
```

## Development
### Setup
```sh
git clone git@github.com:uptilab2/ftp-proxy.git
cd ftp-proxy

# Project uses pipenv for dependency management
# so it should be installed first
pipenv install --dev

# Run the tests:
pipenv run py.test

# Run the development server:
pipenv run python -m aiohttp.web -H 0.0.0.0 -P 5000 ftp_proxy:init_func
```
