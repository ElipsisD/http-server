# HTTP-server

it is simple http-server build by socket package from python

### `/echo/{str}` - return `str` (support gzip encoding)

### `/filename` - work with **POST** and **GET** methods:
 - **POST** - create file with `filename` with data from response body
 - **GET** - return data from file in response body
### `/user-agent` - return data from User-Agent header in response body