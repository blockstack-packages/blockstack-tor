# blockstack-tor

Blockstack/Tor integration.  To use, do the following:

1. Set a Tor password, if you haven't already.
```
$ tor --hash-password "hello world"
16:1DFAB8C36452BBFE60C21699968AB3B8E0B89DF7F53AAFB7C4E4C5ED5E
```

2. Add the password hash to your `torrc` file:
```
$ echo "HashControlPassword 16:1DFAB8C36452BBFE60C21699968AB3B8E0B89DF7F53AAFB7C4E4C5ED5E" >> /etc/tor/torrc
```

3. Start Tor
```
$ tor -f /etc/tor/torrc
```

4. Start `blockstack-tor` with your Tor password
```
$ blockstack-tor --password "hello world"
```

5. Try it out (work-in-progress; works in the test framework)
```
# make a zonefile for duckduckgo's onion address

$ cat /tmp/tordemo.zonefile
$ORIGIN tordemo.test
$TTL 3600
tor TXT "3g2upl4pq6kufc4m.onion"

# set up Blockstack to use the test framework (not shown),
# and register tordemo.test with the above zone file

$ blockstack register tordemo.test /tmp/tordemo.zonefile

# wait for it to register and confirm...

# try it out!
$ curl --socks5-hostname 127.0.0.1:9050 -D - tordemo.test
HTTP/1.1 301 Moved Permanently
Server: nginx
Date: Thu, 04 May 2017 20:15:23 GMT
Content-Type: text/html
Content-Length: 178
Connection: keep-alive
Location: https://duckduckgo.com/
Expires: Fri, 04 May 2018 20:15:23 GMT
Cache-Control: max-age=31536000
X-DuckDuckGo-Locale: en_US

<html>
<head><title>301 Moved Permanently</title></head>
<body bgcolor="white">
<center><h1>301 Moved Permanently</h1></center>
<hr><center>nginx</center>
</body>
</html>
```

# How to use

To use in production, add a `TXT` record to your name's zone file, formatted as
`tor "address.onion"`.  You can either manually edit your zone file, or use the
new zone file wizard in Blockstack 0.14.2 to add the `TXT` record interactively.
**There should be only one `tor` entry in your zone file**.

Example for DuckDuckGo:
```
$ORIGIN duckduckgo_tor.id
$TTL 3600
tor TXT "3g2upl4pq6kufc4m.onion"
```
