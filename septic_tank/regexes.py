'''
A place to store regular expressions for the regular expression parser
'''
regs = {
    "yyyy-mm-dd hh:mm" : "(?P<date>\d{4}-\d{2}-\d{2} \d{2}:\d{2})",
    "user" : "(?P<user>(@| |)(\w|-i|\||)+)",
    "team" : "(?P<team>\w+)",
    "msg" : "(?P<msg>.*)",
    "action" : "(?P<action>.*)",
    "irclog" : "{{team}}\|{{yyyy-mm-dd hh:mm}} \<{{user}}\> {{msg}}",
    "ircsys" : "{{team}}\|{{yyyy-mm-dd hh:mm}} \-\!\- {{msg}}",
    "ircaction" : "{{team}}\|{{yyyy-mm-dd hh:mm}}\s+\*(\s+|){{user}} {{action}}",

    "level" : "(?P<level>(INFO|ERROR|SEVERE|DEBUG))",
    "yyyy-mm-dd hh:mm:ss,ms" : "(?P<date>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)",
    "module" : "\[(?P<module>(\w|\.)+)\]",
    "ip" : "(?P<ip>\d+.\d+.\d+.\d+)",
    "port" : "(?P<port>\d+)",
    "child" : "(?P<child>\d+)",
    "address" : "\(http-{{ip}}-{{port}}-{{child}}\)",
    "core" : "\[(?P<core>\w+)\]",
    "solrlog" : "{{yyyy-mm-dd hh:mm:ss,ms}} {{level}}  {{module}} {{address}} {{core}} {{msg}}",
    "solraction" : "(?P<action>(add))",
    "solrobjecttype" : "(?P<objecttype>(\w|\.)+)",
    "solrobjectid" : "(?P<objectid>\d+)",
    "solractiongroup" : "\{{{solraction}}=\[{{solrobjecttype}}\.{{solrobjectid}}\]\}",
    "solradd" : "{{yyyy-mm-dd hh:mm:ss,ms}} {{level}}  {{module}} {{address}} {{solractiongroup}} {{msg}}",

    "hostname" : "(?P<hostname>[A-Za-z0-9.]+)",
    "client_ip" : "(?P<client_ip>\d+\.\d+\.\d+\.\d+)",
    "serve_time" : "(?P<serve_time>\d+)",
    #[29/Mar/2012:02:28:00 -0400]
    "apache_date" : "\[(?P<apache_date>{{day_of_month}}/{{month_str}}/{{yyyy}}:{{hh:mm:ss}}) {{tz_offset}}\]",
    "day_of_month" : "\d+",
    "month_str" : "[a-zA-Z]+",
    "yyyy" : "\d{4}",
    "hh:mm:ss" : "\d{2}:\d{2}:\d{2}",
    "tz_offset" : "[+-]\d{4}",
    "apache_action" : "(?P<action>[A-Z]+)",
    "uri" : "(?P<uri>(/[A-Za-z0-9$.+!*'(),~:#%_-]*)+)",
    "query_params" : "(?P<query_params>\?[A-Za-z0-9$.+!*'(),~#%&/=:;_-]*)?",
    "http_version" : "HTTP/(?P<http_version>[0-9.]+)",
    "http_status" : "(?P<http_status>\d+)",
    "bytes" : "(?P<bytes>(\d+|-))",
    "trash" : ".*",
    "apachelog" : "{{hostname}} {{client_ip}} {{serve_time}} {{apache_date}} \"{{apache_action}} {{uri}}{{query_params}} {{http_version}}\" {{http_status}} {{bytes}} {{trash}}",
    }


#COMBINEDAPACHELOG %{IPORHOST:clientip} %{USER:ident} %{USER:auth} \[%{HTTPDATE:timestamp}\] "%{WORD:verb} %{URIPATHPARAM:request} HTTP/%{NUMBER:httpversion}" %{NUMBER:response} (?:%{NUMBER:bytes}|-) "(?:%{URI:referrer}|-)" %{QS:agent}
#IPORHOST (?:%{HOSTNAME}|%{IP})
#USERNAME [a-zA-Z0-9_-]+
#USER %{USERNAME}
#HTTPDATE %{MONTHDAY}/%{MONTH}/%{YEAR}:%{TIME} %{INT:ZONE}
#MONTHDAY (?:(?:0[1-9])|(?:[12][0-9])|(?:3[01])|[1-9])
#YEAR [0-9]+
#TIME (?!<[0-9])%{HOUR}:%{MINUTE}(?::%{SECOND})(?![0-9])
#HOUR (?:2[0123]|[01][0-9])
#MINUTE (?:[0-5][0-9])
## '60' is a leap second in most time standards and thus is valid.
#SECOND (?:(?:[0-5][0-9]|60)(?:[.,][0-9]+)?)
#INT (?:[+-]?(?:[0-9]+))
#WORD \b\w+\b
#URIPATHPARAM %{URIPATH}(?:%{URIPARAM})?
#URIPATH (?:/[A-Za-z0-9$.+!*'(),~:#%_-]*)+
#URIPARAM \?[A-Za-z0-9$.+!*'(),~#%&/=:;_-]*
#NUMBER (?:%{BASE10NUM})
#BASE10NUM (?<![0-9.+-])(?>[+-]?(?:(?:[0-9]+(?:\.[0-9]+)?)|(?:\.[0-9]+)))
#URI %{URIPROTO}://(?:%{USER}(?::[^@]*)?@)?(?:%{URIHOST})?(?:%{URIPATHPARAM})?
#URIPROTO [A-Za-z]+(\+[A-Za-z+]+)?
#URIHOST %{IPORHOST}(?::%{POSINT:port})?
#QS %{QUOTEDSTRING}
#QUOTEDSTRING (?:(?<!\\)(?:"(?:\\.|[^\\"]+)*"|(?:'(?:\\.|[^\\']+)*')|(?:`(?:\\.|[^\\`]+)*`)))
