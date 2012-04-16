from pipeline import Pipe
import json
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
        m.update(json.dumps(data,sort_keys=True))
        data['id'] = m.hexdigest() 
        return data

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
    '''
    checks if the given input - either a string or dict matches a regular
    expression.  
    '''
    def __init__(self,regex,fields=[],reverse=False):
        Filter.__init__(self,fields=fields)
        self.regex = re.compile(regex)
        self.reverse = reverse

    def execute(self,data):
        logging.debug('%s execute with data %s' % (type(self),data))
        if data is None:
            return data
        if isinstance(data,dict):
            if self.reverse:
                return self.execute_reverse_dict(data)
            return self.execute_dict(data)
        elif isinstance(data,str) or isinstance(data,unicode):
            if self.reverse:
                return self.execute_reverse_str(data)
            return self.execute_str(data)
        else:
            return None

    def execute_reverse_str(self,data):
        'like grep -v'
        if self.regex.search(data):
            return None
        return data

    def execute_str(self,data):
        if self.regex.search(data):
            return data
        return None

    def execute_reverse_dict(self,data):
        '''
        note that this only operates if fields are given
        returns None if no fields are given
        '''
        if self.fields: 
            for key in self.fields:
                if key in data:
                    if self.regex.search(data[key]):
                        return None
            return data
        return None 

    def execute_dict(self,data):

        if self.fields:
            for key in self.fields:
                if key in data:
                    if self.regex.search(data[key]):
                        return data
                else:
                    # if a non-existent field is given, we should return data
                    return data
        else:
            for key in data:
                if self.regex.search(data[key]):
                    return data
        return None

class AddFieldsFilter(Filter):
    '''
    Add a dictionary of keys and values to each record passing through
    the pipeline.  Useful for adding out-of-band data like server (hostname)
    to each record.
    
    inputs
        fields = dict, required

    outputs
        updates every record in pipeline with the contents of the dict
    '''
    def __init__(self, fields={}):
        # parent defineds fields=[], this must override
        Filter.__init__(self,fields=fields)

    def execute(self,data):
        logging.debug('%s execute with data %s' % (type(self),data))
        if data is None:
            return data

        if self.fields:
           if isinstance(self.fields,dict):
               data.update(self.fields)
               return data

        # we cannot add fields unless it is a dict, so we just pass on 
        # what we got.
        return data


class RemoveFieldsFilter(Filter):
    '''
    Remove fields from records passing through a pipeline.

    inputs
        fields = list, required
    '''
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
    '''
    lowercase all fields, or specific fields of records passing through 
    a pipeline.
 
    inputs
        fields = list, optional
    '''
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

