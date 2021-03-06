from pipeline import Pipe
from regexes import regs
from collections import defaultdict
import csv
import logging
import re

class Parser(Pipe):

    def __init__(self):
        super(Parser, self).__init__()

class CSVParser(Parser):
    '''
    csv parser
 
    inputs

        fieldnames - array, required, names of fields in csv file
        record_type - string, required, added as the value for the 'type'
            key for every call to parse.
        parse_field - string, default 'msg' - if execute is passed a dict,
            this is the key in that dict to parse
        kwargs - keyword arguments that get passed directly to csv.DictReader

    notes
    
        1. all quotes are removed from data  
    '''
    def __init__(self,record_type,fieldnames=[],parse_field='msg',**kwargs):
        super(CSVParser, self).__init__()
        # fix - add kwargs here to be passed to csvreader
        self.fieldnames = fieldnames
        self.parse_field = parse_field
        self.kwargs = kwargs
        self.record_type = record_type

    def execute(self,data):
        '''
        parse a single line of csv data

        inputs

            data - either a string or a dict - if a string, parse it - if a
                dict, parse the field based on self.parse_field.
        
        outputs

            a dict mapping self.fieldnames to values parsed from data or None
                if parsing fails.
       

        '''
        if isinstance(data,str) or isinstance(data,unicode):
            return self.parse(data)
        if isinstance(data,dict):
            if self.parse_field in data:
                captured = self.parse(data[self.parse_field])
                if captured:
                    data.update(captured)
                    return data
        return None

                    
    def parse(self,data):
        '''
        parse a csv string

        input

            data = single line string containing csv 

        output

            dict = map of self.fieldnames to parsed fields
        '''
        try:
            # FIX - creating and destroying objects is slow, limits
            # this parser to 1000 recs/s.  self.reader.reader is 400ms
            # faster on 18k recs.  not enough to be worth it
            reader = csv.DictReader([data],fieldnames=self.fieldnames,
                **self.kwargs)
            output = reader.next()
            if isinstance(output,dict):
                output['type'] = self.record_type
                # csv module appends shit it does not have fieldnames for to
                # None. lets remove those.
                if None in output:
                    del output[None]
                return output
            return None
        except Exception, e:
            # excepting just csv.Error is not enough because of unicode errors
            logging.error('csv parse error: %s',str(e))
        return None
        


class RegexExpander(object):
    '''
    this takes a dict of names mapped to regular expressions possibly
    containing references wrapped in {{ }}.  the references are expanded
    recursively until no references remain.
    '''

    def __init__(self,regs=regs):
        self.regs = regs
        # {{ anything but braces followed by }}
        self.delim_regex = re.compile("{{([^{|^}]+)}}")
        self.expand_regs()

    def expand_regs(self):
        '''replace {{anything}} with a substitue regular expression in the
        regs dict.
        '''
        for key in self.regs:
            value = self.regs[key]
            self.regs[key] = self.recursive_replace(value)

    def recursive_replace(self,value):
        if len(value) > 5000:
            raise Exception, "circular reference"

        result = self.delim_regex.search(value)
        if result:
            newvalue = re.sub('{{%s}}' % result.group(1), self.regs[result.group(1)], value)
            return self.recursive_replace(newvalue)
        return value

class RegexParser(Parser):
    '''
    a regular expression parser that executes a regular expression search
    on a line using potentially a group of regular expressions.  the first
    matching regular expression wins.
    '''
    def __init__(self,regs=regs,use=[],parse_field='msg'):
        super(RegexParser, self).__init__()
        self.expanded = RegexExpander(regs=regs)
        if not use:
           raise Exception, 'use must be a list, and cannot be empty'
        self.use = use
        self.parse_field = parse_field
        self.compiled = {}
        self.matches = defaultdict(int)
        self.compile()

    def compile(self):
        for key in self.use:
            if key not in self.expanded.regs:
                raise Exception, 'key %s given in use is not supplied in regs' % key
            logging.debug('compiling regex %s = %s' % (key,self.expanded.regs[key]))
            # need re.DOTALL to match \n for multiline
            self.compiled[key] = re.compile(self.expanded.regs[key],re.DOTALL)

    def execute(self,data):
        '''
        This parses the given data using potentially many regexes.

        data could be either a string or a dict.
        if it is a string, we try to parse the string
        if it is a dict, we use self.parse_field to determine what field
            to parse
        '''
        # fix - remove this string shit, should always be a dict
        if isinstance(data,str) or isinstance(data,unicode):
            return self.search_line(data)
        if isinstance(data,dict):
            if self.parse_field in data:
                captured = self.search_line(data[self.parse_field])
                if captured:
                    data.update(captured)
                    return data
                return None
        
    def search_line(self,line):
        '''
        search a single line using each regex in self.use until we get a match
        self.use is processed in order
        '''
        for key in self.use:
            result = self.compiled[key].search(line)
            if result:
                self.matches[key] += 1
                logging.debug('%s MATCHED %s' % (key,line))
                matches = result.groupdict()
                matches['type'] = key
                return matches

        logging.info('NO MATCH FOUND %s' % line)
        return None
