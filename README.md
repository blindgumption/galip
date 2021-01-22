# GALIP -- Geolocate Access Logs using IP addresses

GALIP is a project to extract IP addresses from web server access logs and use third party APIs to determine the geographic location the query came from.  Yes, it's a contrived acronym, but it's pronounceable.

The initial focus is using Nginx access logs formatted in JSON using the following directives in the http section of nginx.conf.  Because Nginx does not provide msecs on the ISO8601 timestamp, I use a map directive to create a new variable from the ISO8601 and unix timestamps.

```text

        map "$time_iso8601:$msec" $time_iso8601_msec {
            ~^(\d+-\d+-\d+T\d+:\d+:\d+)([+|-]\d+:\d+):\d+(\.\d+)$ $1$3$2;}

        log_format  json_combined escape=json '{'
            '"time_iso8601_msec":"$time_iso8601_msec", '
            '"time_iso8601":"$time_iso8601", '
            '"time_ms":"$msec", '
            '"remote_addr":"$remote_addr", '
            '"remote_user":"$remote_user", '
            '"request":"$request", '
            '"status": "$status", '
            '"body_bytes_sent":"$body_bytes_sent", '
            '"request_time":"$request_time", '
            '"http_user_agent":"$http_user_agent" ' '}';

        access_log  /var/log/nginx/access.log json_combined;
        ## access_log /var/log/nginx/access.log;

```

## The Two Main Areas of GALIP

The initial motivation for GALIP was me (BlindGumption) wanting to know where queries were coming from.  And I wanted/needed that data presented in an accessible way.

As I thought about it, I realized the code for getting the data and providing it to a web app should be separate from presenting it (MVC anyone?).  So ...
GALIP has two main reasons to exist,

1. Create the data -- getting the IP addresses from the logs, querying the APIs for the location, storing that info in a database
1. Serving up that data in a variety of ways

### First, Get the Data

There is (well, will be) a Python script that can run as a systemd service.  If this project really takes off, there might be an actual install script or maybe even apt/yum integration.  Until then, there will be manual steps to configure the galipd service.

The galipd service will read from the specified access logs (defaults to '/var/log/nxing/access.log').  The log will need to be formatted as described above by the Nginx directives.  

galipd will extract the remote IP address from the log statement and query third party services (more on these later) to get the geographic location data.  it will store that location data in a database (defaults to MongoDB).  It will also store the access log in the database in its JSON format.

### Second, Serve the Data

The GALIP Python modules wil provide a variety of ways to get the geolocation data from the database.  They will also provide access to the access logs.

These interfaces will evolve as blindgumption.com evolves.

## The Giolocation APIs

GALIP will initially use
[IPStack](https://ipstack.com) and
[IPLocate](https://www.iplocate.io) free tier services for  proof of concept.  If GALIP really takes off, maybe there will be some integration with MaxMind and it will be up to the users of GALIP if they want to pay for any of the geolocation lookup services.  

I got this idea from a
[blog regarding how to look up geolocation data](https://medium.com/@rossbulat/node-js-client-ip-location-with-geoip-lite-fallback-c25833c94a76).
