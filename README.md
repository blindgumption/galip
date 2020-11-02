# GALIP -- Geolocate Access Logs using IP addresses 

GALIP is a project to extract IP addresses from web server access logs and use third party APIs to determine the geographic location the query came from.  Yes, it's a contrived acronym, but it's pronounceable. 

The initial focus is using Nginx access logs formatted in JSON using the following directives in the http section of nginx.conf.  Because Nginx does not provide msecs on the ISO8601 timestamp, I use a map directive to create a new variable from the ISO8601 and unix timestamps.

`
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
        `