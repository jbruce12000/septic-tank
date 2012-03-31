from pipeline import Pipe
import logging
import re
import time
import hashlib

class Filter(Pipe):
    def __init__(self,fields=[]):
        super(Filter, self).__init__()
        self.fields = fields

class UniqFilter(Filter):
    '''
    Adds an id key to the record [which is a dict] passing through the pipeline.
    the value of the id key is an md5sum of the content of the record.

    NOTE: This does not prevent the record from passing through even if 
          previously seen.  This intended to be used with solr.  

    FUTURE: this could easily be made to have uniq output with limits on how 
            much gets stored.
    '''
    def execute(self,data):
        logging.debug('%s execute with data %s' % (type(self),data))
        if 'id' in data:
            del data['id']
        m = hashlib.md5()
        m.update(self.flatten_dict(data))
        data['id'] = m.hexdigest() 
        return data

    def flatten_dict(self,mydict):
        output = ''
        for key in sorted(mydict.iterkeys()):
            output = "%s%s%s" % (output, key, mydict[key])
        return output

class ZuluDateFilter(Filter):
    '''
    converts the datetime in the given field[s] from local to Zulu time
    Any format can be read for inoput, and any format can be produced for
    output.
  
    informat = strptime format string for reading your timestamp
    outformat = strptime format string you'd like output to be
    '''
    def __init__(self,fields=[],informat="%Y-%m-%d %H:%M:%S,%f",outformat="%Y-%m-%dT%H:%M:%SZ"):
        Filter.__init__(self,fields=fields)
        self.informat = informat
        self.outformat = outformat

    def execute(self,data):
        logging.debug('%s execute with data %s' % (type(self),data))
        if data is None:
            return data
        if self.fields:
            for key in self.fields:
                if key in data:
                    z = self.zulu(data[key])
                    data[key] = z
        return data

    def zulu(self,tstamp):
        return time.strftime(self.outformat,
              time.gmtime(time.mktime(time.strptime(tstamp, self.informat))))

class GrepFilter(Filter):
    def __init__(self,regex,fields=[]):
        Filter.__init__(self,fields=fields)
        self.regex = re.compile(regex)

    def execute(self,data):
        logging.debug('%s execute with data %s' % (type(self),data))
        if data is None:
            return data
        if self.fields:
            for key in self.fields:
                if key in data:
                    if self.regex.search(data[key]):
                        return data
            # if a non-existent field is given, we should return data
            for key in self.fields:
                if key not in data:
                    return data
        else:
            for key in data:
                if self.regex.search(data[key]):
                    return data
        return None

class RemoveFieldsFilter(Filter):
    def execute(self,data):
        logging.debug('%s execute with data %s' % (type(self),data))
        if data is None:
            return data
        if self.fields:
            for key in self.fields:
                if key in data:
                    del data[key]
        return data


class LCFilter(Filter):
    def execute(self,data):
        logging.debug('%s execute with data %s' % (type(self),data))
        if data is None:
            return data
        if self.fields:
            for key in self.fields:
                if key in data:
                    data[key] = data[key].lower()
        else:
            for key in data:
                if data[key] is not None:
                    data[key] = data[key].lower()
        return data

