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
// input
//     integer
// output
//     zero padded string
function addZero(i) {
if (i<10) { i="0" + i; }
return i;
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
//----------------------------------------------------------------------------
function solrsearch() {

// get needed parameters from url or set sane defaults
this.set_defaults = function() {
    this.date_fq = this.params["date_fq"] || "[NOW/HOUR-24HOURS TO NOW/HOUR+2HOURS]";
    this.facet_range = this.params["facet.range"] || "date_dt";
    this.facet = this.params["facet"] || "on";
    this.facet_mincount = this.params["facet.mincount"] || 1;
    this.host = this.params["host"] || "virtdev.cei.cox.com";
    this.port = this.params["port"] || "8080";
    this.core = this.params["core"] || "medley";
    this.facet_date_range_start = this.params["f.date_dt.facet.range.start"] || "NOW/HOUR-24HOURS";
    this.facet_date_range_end = this.params["f.date_dt.facet.range.end"] || "NOW/HOUR+2HOURS";
    this.facet_date_range_gap_secs = parseInt(this.params["f.date_dt.facet.range.gap.secs"],10) || 3600;
    this.rows = this.params["rows"] || 20;
    this.start = this.params["start"] || 0;
    this.facet_field = this.params["facet.field"] || ["type_t","server_ti"];
    this.search_for = this.params["search-for"];
    this.search_field = this.params["search-field"];
    this.get_facet_map_from_query_string();
    this.set_facet_map_on_page();
    }

// grab query params from url
this.params = query_params()

//----------------------------------------------------------------------------
// convert a local time string to a zulu time string
// input
//     string "2012-05-23 15:43:26"
// output
//     string "2012-05-23T19:43:26Z"
//----------------------------------------------------------------------------
this.local_to_zulu = function(d) {
    d = d.replace(" ","T");
    dt = new Date(d);
    return dt.toISOString();
    }

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

this.prepare_date_params = function() {
    var start = $("#start").attr("zulu");
    var end = $("#end").attr("zulu");
    if(start && end) {
        // this is here so that if someone uses the back button, the last gap
        // is still calculated properly
        oldgap = parseInt(this.params["f.date_dt.facet.range.gap.secs"],10);
        this.facet_date_range_gap_secs = this.facet_gap_size(31,start,end);
        this.facet_date_range_start = start;
        var endgap = parseInt(oldgap,10) + parseInt(this.facet_date_range_gap_secs,10);
        this.facet_date_range_end = end+"+"+endgap+"SECONDS";
        this.date_fq = "["+start+" TO "+end+"+"+oldgap+"SECONDS]";
        }
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
    $.each(this.facet_map,function(key,list){
        data = {};
        data["fq"] = key+":"+"("+list.join(" OR ")+")";
        fqs.push($.param(data));
        });
    data = {};
    data["fq"] = "date_dt:" + this.date_fq;
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
    this.facet_map = this.get_facet_selections();
    this.prepare_date_params();
    var data = {};
    data["start"] = this.start;
    data["rows"] = this.rows;
    data["facet"] = this.facet;
    data["facet.mincount"] = this.facet_mincount;
    data["f.date_dt.facet.mincount"] = 0;
    data["facet.range"] = this.facet_range;
    data["f.date_dt.facet.range.start"] = this.facet_date_range_start;
    data["f.date_dt.facet.range.end"] = this.facet_date_range_end;
    return $.param(data);
    }

this.solr_params = function() {
    var q = this.easy_query_params();
    var ff = this.flattenlist('facet.field',this.facet_field);
    if(ff) {
        q = q + "&" + ff;
        }
    var fqs = this.flatten_fqs_solr();
    if(fqs) {
        q = q + "&" + fqs;
        }
    var data={};
    data["q"] = "*:*";
    if (this.search_field && this.search_for) {
        data["q"] = this.search_field + ":" + this.search_for;
        }
    data["f.date_dt.facet.range.gap"] = "+" + this.facet_date_range_gap_secs+"SECONDS";
    q = q + "&" + $.param(data);
    return q;
    }

this.browser_params = function() {
    var q = this.easy_query_params();
    var data = {};
    data["host"] = $("#host").val();
    data["port"] = $("#port").val();
    data["core"] = $("#core").val();
    data["date_fq"] = this.date_fq;
    if ($("#search-field").val()) {
        data["search-field"] = $("#search-field").val();
        }
    if ($("#search-for").val()) {
        data["search-for"] = $("#search-for").val();
        }
    data["f.date_dt.facet.range.gap.secs"] = this.facet_date_range_gap_secs;
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


//----------------------------------------------------------------------------
// inputs
//     date string in zulu time like "2012-05-23T00:03:27Z"
// outputs
//     unix seconds since 1/1/1970
//----------------------------------------------------------------------------
this.unixsecs = function(d) {
    var dt = new Date(d);
    if(dt) {
        return dt.getTime()/1000;
        }
    return 0;
    }

//----------------------------------------------------------------------------
// ss.facet_gap_size(25,start,end);
// facet_gap_size
// inputs 
//     num_blocks
//     start date like "2012-05-23T00:03:27Z"
//     end date like above
// outputs 
//     gap size in seconds
//----------------------------------------------------------------------------
this.facet_gap_size = function(blocks,start_date,end_date) {
    var map_o_secs = [1,10,30,60,300,600,900,1800,3600,7200,14400,28800,86400,604800];

    var start_s = this.unixsecs(start_date);
    var end_s = 0;
    if (end_date) {
        end_s = this.unixsecs(end_date) + this.facet_date_range_gap_secs;
        }
    else {
        end_s = this.unixsecs(start_date) + this.facet_date_range_gap_secs;
        } 
    var diff_secs = end_s - start_s;
    var block_secs = diff_secs/blocks;
    for(var i=0;i<map_o_secs.length;i++) {
        if(map_o_secs[i] >= block_secs) {
            return map_o_secs[i];
            }
        }
    return map_o_secs[map_o_secs.length-1];
    }


//----------------------------------------------------------------------------
var that = this;
this.ajax_success = function(data) {
    process_json(data);
    that.get_facet_map_from_query_string();
    that.set_facet_map_on_page();
    }

//----------------------------------------------------------------------------
this.ajax = function() {
    console.log(this.solrurl());
    $.ajax({ url : this.solrurl(),
         dataType: "json",
         success: this.ajax_success,
         error: function(xhr,err,text){ alert(err+" and "+text);},
         });
    }

//----------------------------------------------------------------------------
this.redirect = function() {
    var url = window.location+"";
    // remove the query string
    url = url.split("?")[0];
    window.location = url + "?" + this.browser_params();
    }

this.set_defaults();
if(size(this.params)==0) {
    this.redirect();
    }
else {
    this.ajax();
    }
}


//----------------------------------------------------------------------------
//----------------------------------------------------------------------------
function process_json(data) {
process_facets(data)
process_docs(data)
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

var pager_html = "Records "+begin+" - "+end+" of "+total;
if (begin > 1) {
    pager_html = prev + " " + pager_html;
    }
if (end < total) {
    pager_html = pager_html + " " + next;
    }
$("#records-header").html(pager_html);
$("#records").empty();

var fields = {};
$.each(docs,function(i,doc) {

    var cls="";
    if (i % 2 == 0) { cls="even"; }
    else { cls="odd"; }

    //sort fields alphabetically by name
    var sorted = sortkeys(doc); 
    for (i in sorted) {
        var key=sorted[i];
        var value=doc[key];
        field=remove_field_type(key);
        fields[field] = key;
        $("#records").append("<div class=\"row "+cls+"\"><div class=\"column-field\"><a href=\"#"+key+"\">"+field+"</a></div><div class=\"column-value\">"+value+"</div></div>");
        }
    });

// add all fields to the fields dropdown in the form
$('#search-field option').remove();
var sorted = sortkeys(fields);
for (i in sorted) {
    var key=sorted[i];
    var value=fields[key];
    $('#search-field').append($("<option/>", {
        value: value,
        text: key 
        }));
    }

if (ss.search_field) {
    $("#search-field").val(ss.search_field);
    }
if (ss.search_for) {
    $("#search-for").val(ss.search_for);
    }

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
$(".statsblocks").selectable({filter: $(".block-text"),
    selected: function(event, ui) {
        // this updates the start and end input boxes to times selected
        // in the date facet
        // FIX hardcoded ss
        var fmap = ss.get_facet_selections();
        dates = fmap['date_dt'];
        if(dates) {
            var start_dt=new Date(dates[0]);
            var end_dt=new Date(dates[dates.length-1]);
            $("#start").val(neat_time(start_dt));
            $("#start").attr("zulu",dates[0]);
            $("#end").val(neat_time(end_dt));
            $("#end").attr("zulu",dates[dates.length-1]);
            }
        }
    });
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

$("#start").datetimepicker({
    showSecond: true,
    timeFormat: 'hh:mm:ss',
    dateFormat: 'yy-mm-dd',
    });

$("#end").datetimepicker({
    showSecond: true,
    timeFormat: 'hh:mm:ss',
    dateFormat: 'yy-mm-dd',
    });

$("#start").change(function() {
    $("#start").attr("zulu",ss.local_to_zulu($("#start").val()));
    });

$("#end").change(function() {
    $("#end").attr("zulu",ss.local_to_zulu($("#end").val()));
    });

// set values for inputs
$("#host").val(ss.host);
$("#port").val(ss.port);
$("#core").val(ss.core);


}

//----------------------------------------------------------------------------
$(document).ready(function() {
initialize()

});

