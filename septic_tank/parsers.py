from pipeline import Pipe
from regexes import regs
from collections import defaultdict
import logging
import re

class Parser(Pipe):

    def __init__(self):
        super(Parser, self).__init__()

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
    def __init__(self,regs=regs,use=[]):
        super(RegexParser, self).__init__()
        self.expanded = RegexExpander(regs=regs)
        if not use:
           raise Exception, 'use must be a list, and cannot be empty'
        self.use = use
        self.compiled = {}
        self.matches = defaultdict(int)
        self.compile()

    def compile(self):
        for key in self.use:
            if key not in self.expanded.regs:
                raise Exception, 'key %s given in use is not supplied in regs' % key
            self.compiled[key] = re.compile(self.expanded.regs[key])

    def execute(self,line):
        '''
        search using each regex in use until we get a match
        use is processed in order
        '''
        for key in self.use:
            result = self.compiled[key].search(line)
            if result:
                self.matches[key] += 1
                logging.debug('%s MATCHED %s' % (key,line))
                matches = result.groupdict()
                matches['type'] = key
                return matches

        logging.debug('NO MATCH FOUND %s' % line)
        return None
