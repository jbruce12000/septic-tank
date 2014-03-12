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
    # solr logs
    # 2012-02-15 02:24:00,320 INFO  [org.apache.solr.core.SolrCore] (http-0.0.0.0-8080-16) [ellington] webapp=/solr path=/update/ params={commit=false} status=0 QTime=1
    # 2012-02-15 03:00:14,307 WARNING [org.apache.solr.handler.ReplicationHandler] (http-0.0.0.0-8080-130) Unable to get index version : : java.io.FileNotFoundException: /services/solr/TEST/ellington/data_test1/index/_8dst.fnm (No such file or directory)\n']	at java.io.RandomAccessFile.open(Native Method)
    "level" : "(?P<level>(INFO|WARNING|ERROR|SEVERE|DEBUG))",
    "yyyy-mm-dd hh:mm:ss,ms" : "(?P<date>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)",
    "module" : "\[(?P<module>(\w|\.)+)\]",
    "ip" : "(?P<ip>\d+.\d+.\d+.\d+)",
    "port" : "(?P<port>\d+)",
    "child" : "(?P<child>\d+)",
    "address" : "\((?P<address>[A-Za-z0-9.-]+)\)",
    "core" : "\[(?P<core>\w+)\]",
    "solrlog" : "{{yyyy-mm-dd hh:mm:ss,ms}} {{level}}  {{module}} {{address}} {{core}} {{msg}}",
    "solraction" : "(?P<action>(add))",
    "solrobjecttype" : "(?P<objecttype>(\w|\.)+)",
    "solrobjectid" : "(?P<objectid>\d+)",
    "solractiongroup" : "\{{{solraction}}=\[{{solrobjecttype}}\.{{solrobjectid}}\]\}",
    "solr" : "{{yyyy-mm-dd hh:mm:ss,ms}} {{level}}\s+{{module}} {{address}}( {{core}}|) {{msg}}",

    # apache access logs
    # FIX - http version not always getting captured.
    "hostname" : "(?P<hostname>([A-Za-z0-9.]+)|(\d+\.\d+\.\d+\.\d+))",
    "client_ip" : "(?P<client_ip>\d+\.\d+\.\d+\.\d+)",
    "serve_time" : "(?P<serve_time>\d+)",
    #[29/Mar/2012:02:28:00 -0400]
    "apache_date" : "\[(?P<date>{{day_of_month}}/{{month_str}}/{{yyyy}}:{{hh:mm:ss}}) {{tz_offset}}\]",
    "day_of_month" : "\d+",
    "month_str" : "[a-zA-Z]+",
    "yyyy" : "\d{4}",
    "hh:mm:ss" : "\d{2}:\d{2}:\d{2}",
    "tz_offset" : "[+-]\d{4}",
    "apache_action" : "(?P<action>[A-Z]+)",
    "uri" : "(?P<uri>(/[A-Za-z0-9 $.+!*'(),~:#%_-]*)+)",
    "query_params" : "(?P<query_params>\?[A-Za-z0-9$.+!*'(),~#%&/=:;_-]*)?",
    "http_version" : "((HTTP|http)/(?P<http_version>[0-9.]+))",
    "http_status" : "(?P<http_status>\d+)",
    "bytes" : "(?P<bytes>(\d+|-))",
    "referer" : "(?P<referer>.*)",
    "useragent" : "(?P<useragent>.*)",
    "trash" : ".*",
    
    "apachelog" : "{{hostname}} {{client_ip}} {{serve_time}} {{apache_date}} \"{{apache_action}} {{uri}}{{query_params}}( |){{http_version}}\" {{http_status}} {{bytes}} \"{{referer}}\" \"{{useragent}}\"",
    "pagegen_apachelog" : "{{client_ip}} {{serve_time}} {{apache_date}} \"{{apache_action}} {{uri}}{{query_params}}( |){{http_version}}\" {{http_status}} {{bytes}} {{trash}}",

    # celery logs
    #[2012-04-09 23:02:08,948: INFO/PoolWorker-11] medley.videos.tasks.brightcove.UpdateBrightcoveVideos[bc9513e6-ae97-4172-8c97-0af7b3a4e369]:
    #[2012-04-09 23:02:08,951: WARNING/PoolWorker-11] Insufficient settings:www.prod.coxohiomedia.com:brightcove_account_id is missing, but required
    #[2012-04-09 23:01:35,042: ERROR/PoolWorker-11] Failed to import thumbnail
    #[2012-04-16 19:50:38,403: INFO/MainProcess] Got task from broker: medley.ellington_overrides.search.tasks.HaystackUpdateTask[c974aa00-edd5-427d-81f4-98bc6db7d673] eta:[2012-04-16 15:51:08.390622]
    "poolworker" : "(PoolWorker-(?P<poolworker>\d+)|MainProcess)",
    "celery_task" : "(?P<celery_task>[A-Za-z.]+)",
    "celery_hash" : "\[(?P<celery_hash>[a-f0-9-]+)\]\:",
    "celery_msg" : "(?P<celery_msg>.*)",
    "celerylog" : "\[{{yyyy-mm-dd hh:mm:ss,ms}}: {{level}}/{{poolworker}}\] ({{celery_task}}{{celery_hash}}|)\s*{{celery_msg}}",

    # pgbouncer logs
    # 2012-08-08 15:11:57.281 15674 LOG C-0x2aaaaad02000: ellington_app/django@::ffff:10.188.10.20:35816 login attempt: db=ellington_app user=django
    "yyyy-mm-dd hh:mm:ss.ms" : "(?P<date>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)",
    "pid" : "(?P<pid>\d+)",
    "dbconnection" : "(?P<dbconnection>..0x[0-9|a-f]+)",
    "database" : "(?P<database>(\w|_)+)",
    "pgbouncerlog" : "{{yyyy-mm-dd hh:mm:ss.ms}} {{pid}} LOG {{dbconnection}}: {{database}}/{{user}}@::ffff:{{ip}}:{{port}} {{msg}}",

    # medley debug logs for PID middleware
    #2012-11-13 22:56:45,072 - medley.util.middleware.LogPIDMiddleware - DEBUG - 32070|meminfo(rss=158584832, vms=581275648)|/|asdf=2&dasdfasdf=5
    "medleypidlog" : "{{yyyy-mm-dd hh:mm:ss,ms}} \- (?P<module>[A-Za-z0-9.]+) \- {{level}} \- {{pid}}\|meminfo\(rss\=(?P<resident>\d+), vms\=(?P<virtual>\d+)\)\|{{uri}}\|(?P<query_params>.*)"
    }


