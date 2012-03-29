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
    }
