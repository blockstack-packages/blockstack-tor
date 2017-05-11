# blockstack-tor

Blockstack/Tor integration.

# Getting Started

To get started, do the following.

1. Install [Blockstack](https://github.com/blockstack/blockstack-core).

2. Set a Tor password, if you haven't already.
```
$ tor --hash-password "hello world"
16:1DFAB8C36452BBFE60C21699968AB3B8E0B89DF7F53AAFB7C4E4C5ED5E
```

3. Add the password hash to your `torrc` file:
```
$ echo "HashControlPassword 16:1DFAB8C36452BBFE60C21699968AB3B8E0B89DF7F53AAFB7C4E4C5ED5E" >> /etc/tor/torrc
```

4. Start Tor
```
$ tor -f /etc/tor/torrc
```

5. Start `blockstack-tor` with your Tor password
```
$ blockstack-tor --password "hello world"
```

6. Try it out

Test it out with `duckduckgo_tor.id`, which points to DuckDuckGo's hidden service.
```
$ curl -L --socks5-hostname 127.0.0.1:9050 -D - duckduckgo_tor.id
HTTP/1.1 301 Moved Permanently
Server: nginx
Date: Mon, 08 May 2017 19:33:52 GMT
Content-Type: text/html
Content-Length: 178
Connection: keep-alive
Location: https://duckduckgo.com/
Expires: Tue, 08 May 2018 19:33:52 GMT
Cache-Control: max-age=31536000
X-DuckDuckGo-Locale: en_US

HTTP/1.1 200 OK
Server: nginx
Date: Mon, 08 May 2017 19:33:54 GMT
Content-Type: text/html; charset=UTF-8
Content-Length: 5229
Connection: keep-alive
ETag: "59109693-146d"
Expires: Mon, 08 May 2017 19:33:53 GMT
Cache-Control: no-cache
Strict-Transport-Security: max-age=31536000
Accept-Ranges: bytes

<!DOCTYPE html>
<!--[if IEMobile 7 ]> <html lang="en_US" class="no-js iem7"> <![endif]-->
<!--[if lt IE 7]> <html class="ie6 lt-ie10 lt-ie9 lt-ie8 lt-ie7 no-js" lang="en_US"> <![endif]-->
<!--[if IE 7]>    <html class="ie7 lt-ie10 lt-ie9 lt-ie8 no-js" lang="en_US"> <![endif]-->
<!--[if IE 8]>    <html class="ie8 lt-ie10 lt-ie9 no-js" lang="en_US"> <![endif]-->
<!--[if IE 9]>    <html class="ie9 lt-ie10 no-js" lang="en_US"> <![endif]-->
<!--[if (gte IE 9)|(gt IEMobile 7)|!(IEMobile)|!(IE)]><!--><html class="no-js" lang="en_US"><!--<![endif]-->

...
```

# How to Link a .onion Address to a Blockchain ID

To register your .onion address, add a `TXT` record to your name's zone file, formatted as
`tor "address.onion"`.  You can either manually edit your zone file, or use the
new zone file wizard in Blockstack 0.14.2+ to add the `TXT` record interactively.
**There should be only one `tor` entry in your zone file**.

Example for DuckDuckGo:
```
$ORIGIN duckduckgo_tor.id
$TTL 3600
tor TXT "3g2upl4pq6kufc4m.onion"
```

The steps to register a name for your .onion address are as follows:

1. Make a zone file with your .onion address

```
$ cat /tmp/tordemo.zonefile
$ORIGIN tordemo.id
$TTL 3600
tor TXT "3g2upl4pq6kufc4m.onion"
```

2. Register your Blockchain ID with the zone file
```
$ blockstack register tordemo.id /tmp/tordemo.zonefile
```

3.  Wait for the registration to confirm
```
$ blockstack get_name_zonefile tordemo.id
{
    "zonefile": "$ORIGIN tordemi.id\n$TTL 3600\ntor TXT \"3g2upl4pq6kufc4m.onion\"\n"
}
```

4.  Enjoy!

# Miscellaneous

* **I don't have Blockstack installed.  Can I still try this out?**

Yes, you can!  Run `blockstack-tor` with the `--blockstack-node=node.blockstack.org:6264` flag to use a public node.

* **Will you add support for [Prop279](https://github.com/torproject/torspec/blob/master/proposals/279-naming-layer-api.txt)?**

Yes, that's the plan.

* **How do I try out adding .onion addresses to Blockstack names without registering them first?**

You can use the [Blockstack Integration Test
Framework](https://github.com/blockstack/blockstack-core/tree/master/integration_tests)
to register arbitrary Blockstack names and namespaces, and give them arbitrary
zone files with which to experiment with this tool.
