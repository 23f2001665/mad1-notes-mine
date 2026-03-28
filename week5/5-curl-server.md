# CONTROLLERS: Business Logic Layer
## Curl Commands

- HTTP is a **stateless protocol**: each client request is handled independently. The server does not remember previous requests. To maintain user state across multiple requests (e.g., shopping cart, login sessions), techniques such as:
    - HTTP cookies
    - Hidden form fields
    - Server-side sessions
    - JWT tokens

##### minimal HTTP server

```bash
 while true; do # Runs the loop forever so, server keeps listening after each request
    echo -e "HTTP/1/1 200 OK\n\n $(date)" | # inserts current date dynamically
    nc -l localhost 1500;
 done
```

`nc` = `netcat` (simple networking tool)
`-l` = listen mode  on port `1500`(acts like a server)

- When a client connects on port `1500` → sends current date as HTTP response from `echo` -> restarts and waits again

##### Python Built-in HTTP Server

```bash
python -m http.server
```

$http:// \underbrace{0.0.0.0}_\text{default IP address}: \underbrace{8000}_\text{default port}$ Serves files from the current working directory

HTTP 1.1 variant → large persistent connections and pipelining<br>

::: tip ✅ TODO: Try `curl wttr.in/{type city name}` on your wsl terminal like `curl wttr.in/chennai`
:::

:::code-group

```bash [Client Request]
GET / HTTP/1.1 # http method & version
Host: localhost:5000 or www.domain.com
User-Agent: curl/7.64.1 # version
Accept: */* #accepted file formats
```

```bash [Server Response]
HTTP/1.1 200 OK #status code
Server: SimpleHTTP/0.6 Python/3.x
Content-Type: text/html
Content-Length: <file-size> #10KB
```

:::

::: warning loopback addresses
 `127.0.0.1 (IPv4)` and `::1 (IPv6)` are **loopback** addresses. Packets sent to these addresses:
- Never leave the host machine & are looped through the network interface card only.
- This can be used for **diagnostic** purposes to verify that the internal path through the TCP/IP protocols is working.
:::

<CurlRestAPI />

| **Command**          | **Description**                                          |
|----------------------|----------------------------------------------------------|
| `curl <URL>`         | Basic GET request.                                       |
| `curl -v <URL> --verbose`      | detailed ℹ️info about the request & response, including headers    |
| `curl -L <URL>`      | Follow redirects.                                        |
| `curl -O <URL>`      | Download a file with its original name.                  |
| `curl -H  --header`  | add custom `"Header-Name: Header-Value"` to your HTTP request even multiple    |
| `curl -X POST`       | Send a POST request.                                     |
| `curl -X POST -d "k=v"`    | Send form data with a POST request.                      |
| `curl -X POST -H "Content-Type: application/json" -d '{}'` | Send JSON data.         |
| `curl <URL> -o <filename>` | Save output to a file.                             |
| `curl -i <URL> --include`      | include HTTP response headers      |
| `curl -F "file=@path"`            | Upload a file to a server.                               |
| `curl -w "<format>"`            | Display timing details of the request. (custom output format for information about the transfer, rather than the transferred data itself)                  |
| `curl -s -o /dev/null -w "%{http_code}\n" <URL>` | Get HTTP status code only.                          |

`curl` Output Symbols (`verbose` Mode)<br>
 `>` indicate request headers sent by the client (cURL)<br>
 `<` received from the server.<br>
 `*` indicate additional information like SSL/TLS handshake details and connection info.
