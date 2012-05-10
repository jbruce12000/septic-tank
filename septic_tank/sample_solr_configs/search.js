//----------------------------------------------------------------------------
// size
// inputs 
//     dict
// outputs 
//     integer count of keys
//----------------------------------------------------------------------------
function size(obj) {
var c = 0, key;
for (key in obj) {
    if (obj.hasOwnProperty(key)) c++;
}
return c;
}

//----------------------------------------------------------------------------
// remove_from_array - removes the given value from an array if it exists
// inputs
//     list,value
// outputs
//     list
//----------------------------------------------------------------------------
function remove_from_array(list,val) {
if(typeof(list)=="object") {
    var idx = list.indexOf(val); // Find the index
    if(idx!=-1) list.splice(idx, 1); // Remove it
    return list;
    }
return list;
}

//----------------------------------------------------------------------------
// default_params - object to store default params
//----------------------------------------------------------------------------
function solrsearch() {

// grab query params from url
this.params = query_params()

// set defaults if needed
this.q = this.params["q"] || "*:*";
this.fq = this.params["fq"] || ["date_dt:[NOW/HOUR-24HOURS TO NOW/HOUR+2HOURS]"];
this.facet_range = this.params["facet.range"] || "date_dt";
this.facet = this.params["facet"] || "on";
this.host = this.params["host"] || "virtdev.cei.cox.com";
this.port = this.params["port"] || "8080";
this.core = this.params["core"] || "medley";
this.facet_date_range_start = this.params["f.date_dt.facet.range.start"] || "NOW/HOUR-24HOURS";
this.facet_date_range_end = this.params["f.date_dt.facet.range.end"] || "NOW/HOUR+2HOURS";
this.facet_date_range_gap = this.params["f.date_dt.facet.range.gap"] || "+1HOURS";
this.rows = this.params["rows"] || 20;
this.start = this.params["start"] || 0;
this.facet_field = this.params["facet.field"] || ["type_t","server_ti"];


this.baseurl = function() {
    return "http://"+this.host+":"+this.port+"/solr/"+this.core+"/select/" +
           "?wt=json&json.wrf=?&json.nl=map&";
    }

this.toString = function() {
    return this.fullurl();
    }

this.fullurl = function() {
    return this.baseurl() + this.whole_query();
    }

this.allparams = function() {
    var data = {};
    data["host"] = this.host;
    data["port"] = this.port;
    data["core"] = this.core;
    return $.param(data) + "&" + this.whole_query()
    }

// calculate fqs based on selected facets
this.query = function() {

    var fqs = [];

    // create a map of facet name to list of values
    // like... { "server_ti" : [ "host1","host2" ], } 
    var facet_map = {};
    $.each($(".ui-selected"),function(i,item){
        var ffn = item.getAttribute("facet-field-name");
        var ffv = item.getAttribute("facet-field-value");

        if(facet_map.hasOwnProperty(ffn)) {
            facet_map[ffn].push(ffv);
            }
        else {
            facet_map[ffn] = [ ffv ];
            }
        });

    // fix need special handling for date_dt
    $.each(facet_map,function(key,list){
        var myfq=key+":"+"("+list.join(" OR ")+")";
        fqs.push(myfq);
        });
    this.fq = fqs;
    this.redirect();
    }

this.browser_query_string = function() {
    var data = {};
    // fix, I need to separate browser query string processing from 
    // ajax solr query string.
    }

this.whole_query = function() {
    var data = {};
    data["q"] = this.q;
    data["start"] = this.start;
    data["rows"] = this.rows;
    data["facet"] = this.facet;
    data["facet.range"] = this.facet_range;
    data["f.date_dt.facet.range.start"] = this.facet_date_range_start;
    data["f.date_dt.facet.range.end"] = this.facet_date_range_end;
    data["f.date_dt.facet.range.gap"] = this.facet_date_range_gap;

    var q = $.param(data);
    q = q + "&" + this.flattenlist('facet.field',this.facet_field);
    q = q + "&" + this.flattenlist('fq',this.fq);
    return q;
    }

this.flattenlist = function(key,list) {

    // wtf... js seems to treat one element lists as strings
    if (typeof(list)=="string") {
        // hah, try using { key : list } and key is interpreted as a string!
        var temp = {};
        temp[key]=list;
        return $.param(temp);
        }

    var pieces = [];
    for each (value in list) {
        var mydict = {};
        mydict[key] = value
        pieces.push($.param(mydict));
        }
    return pieces.join("&");
    }

this.ajax = function() {
    console.log(this.fullurl());
    $.ajax({ url : this.fullurl(),
         dataType: "json",
         success: process_json,
         error: function(xhr,err,text){ alert(err+" and "+text);},
         });
    }

this.redirect = function() {
    var url = window.location+"";
    // remove the query string
    url = url.split("?")[0];
    window.location = url + "?" + this.allparams();
    }

// no query params means this is first access
if(size(this.params)==0) {
    this.redirect();
    }
else {
    this.ajax();
    }
}


//----------------------------------------------------------------------------
// query_params
// inputs
//    window.location url
// outputs
//    dict of query params to values
//----------------------------------------------------------------------------
function query_params() {
var urlParams = {};
var e,
    a = /\+/g,  // Regex for replacing addition symbol with a space
    r = /([^&=]+)=?([^&]*)/g,
    d = function (s) { return decodeURIComponent(s.replace(a, " ")); },
    q = window.location.search.substring(1);

while (e = r.exec(q)) {
    key = d(e[1]);
    value = d(e[2]);

    // if the same key exists multiple times, add it to an array
    // solr has this with facet.field for instance
    if(urlParams.hasOwnProperty(key)) {
        if(typeof urlParams[key] == "object") {
            urlParams[key].push(value);
            }
        else {
            urlParams[key] = [ urlParams[key], value ];
            } 
        }
    else {
        urlParams[key] = value;
        }
    }
return urlParams;
}



//----------------------------------------------------------------------------
//----------------------------------------------------------------------------
function process_json(data) {
process_facets(data)
process_docs(data)
}

//----------------------------------------------------------------------------
// input
//     integer
// output
//     commified string
//----------------------------------------------------------------------------
function commify(num) {
        if(typeof(num) == "number") {
            nStr = num.toString();
            } 
        else {
            nStr = num
            }
	nStr += '';
	x = nStr.split('.');
	x1 = x[0];
	x2 = x.length > 1 ? '.' + x[1] : '';
	var rgx = /(\d+)(\d{3})/;
	while (rgx.test(x1)) {
		x1 = x1.replace(rgx, '$1' + ',' + '$2');
	}
	return x1 + x2;
}

//----------------------------------------------------------------------------
// input
//     integer
// output
//     zero padded string
function addZero(i) {
if (i<10) { i="0" + i; }
return i;
}

//----------------------------------------------------------------------------
// input
//    date 
// output
//    string yyyy-mm-dd hh:mm:ss in local time
function neat_time(d) {
return d.getFullYear()+"-"+addZero(d.getMonth()+1)+"-"+addZero(d.getDate())+" "+
       addZero(d.getHours())+":"+addZero(d.getMinutes())+":"+
       addZero(d.getSeconds())
}

//----------------------------------------------------------------------------
// inputs
//     dict
// outputs
//     list of sorted keys
function sortkeys(dict) {
var keys = [];
    for (var key in dict) {
      if (dict.hasOwnProperty(key)) {
        keys.push(key);
      }
    }
    keys.sort();
return keys
}

//----------------------------------------------------------------------------
// inputs
//     data - json object containing solr docs
// outputs
//     html - to the records div
function process_docs(data){
var docs=data.response.docs;
var begin=data.response.start;
var end=data.response.docs.length+begin;
begin=begin+1;
var total=data.response.numFound;

// paging...
if (typeof(ss.rows)=="string") {
    ss.rows = parseInt(ss.rows);
    }

var prev="<a href=\"#start="+(begin-ss.rows-1)+"\">prev</a>";
var next="<a href=\"#start="+(begin+ss.rows-1)+"\">next</a>";

// FIX - does not handle end
if (begin <= 1) {
    $("#records-header").html("Records "+begin+" - "+end+" of "+total+" "+next);
    }
else {
    $("#records-header").html(prev+" Records "+begin+" - "+end+" of "+total+" "+next);
    }
    
$("#records").empty();

$.each(docs,function(i,doc) {
    var cls="";
    if (i % 2 == 0) { cls="even"; }
    else { cls="odd"; }

    //sort fields alphabetically by name
    // FIX - each of the fields should be a link to facet on that link
    sorted = sortkeys(doc); 
    for (i in sorted) {
        var key=sorted[i];
        var value=doc[key];
        field=remove_field_type(key);
        $("#records").append("<div class=\"row "+cls+"\"><div class=\"column-field\"><a href=\"#"+key+"\">"+field+"</a></div><div class=\"column-value\">"+value+"</div></div>");
        }
    });

// this adds a new facet field
$(".column-field a").click(function() {
    // remove the leading # 
    var field=this.hash+"";
    field=field.split("#")[1];
    ss.facet_field.push(field);
    ss.redirect();
    });

// pager link for records header, prev or next
$(".records-header.pager a").click(function() {
    // remove the leading # 
    var field=this.hash+"";
    field=field.split("=")[1];
    ss.start=field;
    ss.redirect();
    });


}

//----------------------------------------------------------------------------
// inputs
//     field - solr field name like date_dt
// outputs
//     string with the final underscore and type removed
function remove_field_type(field) {
words=field.split("_");
if(words.length > 1){
    words=words.slice(0,words.length-1);
    }
return words.join("_")
}

//----------------------------------------------------------------------------
// inputs
//     data - json object containing solr date facet counts
// outputs
//
function process_facets(data){
process_date_facets(data);
process_facet_fields(data);
// FIX - this filter requires that you hold down the ctrl key
// across different statsblocks.  bummer.
$(".statsblocks").selectable({filter: $(".block-text")});
}

//----------------------------------------------------------------------------
// inputs
//     data - solr json object 
// outputs
//
//----------------------------------------------------------------------------
function process_facet_fields(data){
$("#facets").empty();
var fields=data.facet_counts.facet_fields;
for (field in fields) {

    // add a div for this facet
    // FIX - the wrapper for these facets is a problem and jumps down
    // once it fills the screen.
    // these needs to be a clickable X in the corner to close a facet
    // FIX - remove closer X from date, type, and server

    var html = "<div class=\"facet-wrap\">"+
        "<div id=\""+field+"-header\" class=\"records-header\">"+remove_field_type(field) +
        "<div class=\"closer\"><a href=\"#close="+field+"-header\">X</a></div>" +
        "</div><div id=\""+field+"\" class=\"statsblocks\"></div></div>";

    $("#facets").append(html);

    var selector = "#"+field;
    var thefield = eval("data.facet_counts.facet_fields" + "." + field);
    var max = max_dict(thefield);
    $.each(thefield,function(key,value) {
        var percent = Math.floor(value/max*100)
        var overlay = commify(value)
        var attrs = { "facet-field-name" : field,
                      "facet-field-value" : key };
        $(selector).append(block(percent,overlay,key,attrs));
        });
    }

// this removes a facet field
$(".closer a").click(function() {
   // get everything after =
    var field=this.hash+"";
    field=field.split("=")[1];
    $("#"+field).parent().fadeOut('slow', function() {
        var ff=field.replace("-header","");
        ss.facet_field = remove_from_array(ss.facet_field,ff);
        });
    });


}

//----------------------------------------------------------------------------
// inputs
//     data - json object containing solr date facet counts
// outputs
//
//----------------------------------------------------------------------------
function process_date_facets(data){
var dates = data.facet_counts.facet_ranges.date_dt.counts;
var max = max_dict(dates);
$('#dateblocks').empty()
$.each(dates,function(key, value) {
    var attrs={ "facet-field-name" : "date_dt",
                "facet-field-value" : key };
    percent = Math.floor(value/max*100);
    var dt = new Date(key);
    overlay = commify(value);
    $("#dateblocks").append(block(percent,overlay,neat_time(dt),attrs));
    });
}

//----------------------------------------------------------------------------
// max_dict - reads keys and returns the largest value
// inputs
//     dict - keys don't matter, values must be integers
// outputs
//     largest value
//----------------------------------------------------------------------------
function max_dict(dict){
var max=0
$.each(dict,function(key,value) {
    if(value>max) { max=value; }
    });
return max;
}

//----------------------------------------------------------------------------
// flatten_attrs
// input
//    dict
// output
//    string "key1=val1 key2=val2..."
//----------------------------------------------------------------------------
function flatten_attrs(attrs){
if(!attrs) { return ""; }
var kvps=[];
$.each(attrs,function(key,value) {
    kvps.push(key+"="+"\""+value+"\"");
    });
return kvps.join(" ");
}

//----------------------------------------------------------------------------
// block
// inputs
//     percent, integer 0-100
//     overylaytext char - will overlay block
//     text char - will be to the right of block
//     attrs - dict of keys/values to be added to the block-text div
// outputs
//     html representation of a block
//----------------------------------------------------------------------------
function block(percent,overlaytext,text,attrs) {

var kvps=flatten_attrs(attrs);

var html="<div class=\"block-wrap\">\n" +
    "<div class=\"block\">\n" +
    "<div class=\"block-overlay-text\">"+overlaytext+"</div>\n" +
    "<div class=\"block-left\" style=\"width:" +
    (100-percent) + "%\"></div>\n" +
    "<div class=\"block-right\" style=\"width:" +
    percent + "%\"></div>\n" +
    "</div><!--end block-->\n" +
    "<div "+kvps+" class=\"block-text\">" +
    text + "</div>\n" +
    "</div><!--end block-wrap-->\n";
return html
} // end block

//----------------------------------------------------------------------------
// initialize - initialize query parameters, handle start-up tasks for page
// inputs
//     none
// outputs
//     none 
//----------------------------------------------------------------------------
function initialize() {
// global, on purpose.
ss = new solrsearch();

//fix - need a clear button
$("#submit").click(function() {
    ss.query();
    });


}

//----------------------------------------------------------------------------
$(document).ready(function() {
initialize()

});

