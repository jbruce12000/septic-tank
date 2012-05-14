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

this.baseurl = function() {
    return "http://"+this.host+":"+this.port+"/solr/"+this.core+"/select/" +
           "?wt=json&json.wrf=?&json.nl=map&";
    }

this.toString = function() {
    return this.sorlurl();
    }

this.solrurl = function() {
    return this.baseurl() + this.solr_params();
    }

// calculate fqs based on selected facets
this.query = function() {
    this.redirect();
    }

// get all facet selections from facets
this.get_facet_selections = function() {
    // create a map of facet name to list of values
    // like... { "server_ti" : [ "host1","host2" ], } 
    var f_map = {};
    $.each($(".ui-selected"),function(i,item){
        var ffn = item.getAttribute("facet-field-name");
        var ffv = item.getAttribute("facet-field-value");

        if(f_map.hasOwnProperty(ffn)) {
            f_map[ffn].push(ffv);
            }
        else {
            f_map[ffn] = [ ffv ];
            }
        });
    return f_map;
    }

// grab facet map selections from query string
this.get_facet_map_from_query_string = function() {
    var that = this;
    that.facet_map = {};
    $.each(that.facet_field,function(i,item) {
        var facet_vals = that.params["fm::"+item];
        if(!facet_vals) {
            return {};
            }
        var vals = facet_vals.split("::");
        that.facet_map[item] = vals;
        });
    return
    }

this.set_facet_map_on_page = function() {
    // set the selections for each facet
    if (!this.facet_map) {
        return;
        }
    $.each(this.facet_map,function(field,list) {
        $.each(list,function(j,val) {
            var selector1 = "'div[facet-field-name=\""+field+"\"]'";
            var selector2 = "'div[facet-field-value=\""+val+"\"]'";
            // FIX - cannot figure out how to get two selectors to work
            // selector2 is not guaranteed to be unique!
            $(selector2).addClass("ui-selected");
            });
        });
    }

this.flatten_fqs_solr = function() {
    this.get_facet_map_from_query_string();
    var fqs = [];
    var data = {};
    // fix need special handling for date_dt
    $.each(this.facet_map,function(key,list){
        data = {};
        data["fq"] = key+":"+"("+list.join(" OR ")+")";
        fqs.push($.param(data));
        });
    data = {};
    data["fq"] = this.date_fq;
    fqs.push($.param(data));
    return fqs.join("&");
    }

// this converts a data structure that looks like this...
// { key1 : [ val1, val2, val3 ], 
//   key2 : [ val4, val5 ] }
// into a string like this...
// fm::key1=val1::val2::val3&fm::key2=val4::val5
this.browser_facet_map_to_query_string = function() {
    var keystrings = [];
    $.each(this.facet_map,function(key,val){
        keystrings.push("fm::"+key+"="+val.join("::"));
        });
    return keystrings.join("&"); 
    }

// create query string 
// these are the same for both browser and ajax solr
this.easy_query_params = function() {
    var data = {};
    data["q"] = this.q;
    data["start"] = this.start;
    data["rows"] = this.rows;
    data["facet"] = this.facet;
    data["facet.range"] = this.facet_range;
    data["f.date_dt.facet.range.start"] = this.facet_date_range_start;
    data["f.date_dt.facet.range.end"] = this.facet_date_range_end;
    data["f.date_dt.facet.range.gap"] = this.facet_date_range_gap;
    return $.param(data);
    }

this.solr_params = function() {
    // browser params depend on this being set
    this.facet_map = this.get_facet_selections();
    var q = this.easy_query_params();
    var ff = this.flattenlist('facet.field',this.facet_field);
    if(ff) {
        q = q + "&" + ff;
        }
    var fqs = this.flatten_fqs_solr();
    if(fqs) {
        q = q + "&" + fqs;
        }
    return q;
    }

this.browser_params = function() {
    // browser params depend on this being set
    this.facet_map = this.get_facet_selections();
    var q = this.easy_query_params();
    var data = {};
    data["host"] = this.host;
    data["port"] = this.port;
    data["core"] = this.core;
    q = q + "&" + $.param(data);
    q = q + "&" + this.flattenlist('facet.field',this.facet_field);
    q = q + "&" + this.browser_facet_map_to_query_string();
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
    $.each(list,function(i,value) {
        var mydict = {};
        mydict[key] = value
        pieces.push($.param(mydict));
        });
    return pieces.join("&");
    }

var that = this;
this.ajax_success = function(data) {
    process_json(data);
    that.get_facet_map_from_query_string();
    that.set_facet_map_on_page();
    }

this.ajax = function() {
    $.ajax({ url : this.solrurl(),
         dataType: "json",
         success: this.ajax_success,
         error: function(xhr,err,text){ alert(err+" and "+text);},
         });
    }

this.redirect = function() {
    var url = window.location+"";
    // remove the query string
    url = url.split("?")[0];
    window.location = url + "?" + this.browser_params();
    }

// set defaults if needed
this.q = this.params["q"] || "*:*";
this.date_fq = this.params["date_fq"] || "date_dt:[NOW/HOUR-24HOURS TO NOW/HOUR+2HOURS]";
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
this.get_facet_map_from_query_string();
this.set_facet_map_on_page();

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
    ss.start=0;
    ss.query();
    });


}

//----------------------------------------------------------------------------
$(document).ready(function() {
initialize()

});

