from inputs import Input
import logging
import re
import time
import os
from stat import S_ISREG

class FileWatcher(object):
    '''
    represents a watched file on the filesystem.  Used by the DirWatcher.

    inputs

        folder = string, required, folder where the file is located

        name = string, required, name of the file

        seek_end = boolean, True by default.  if you do not want to seek 
            to the end of the file set this to False.  All content in the 
            file will be returned by readfile
            if this is set to False.
     
        last_lines = integer, 0 by default.  grab the last N lines from
            from a file when first opening it. 
    '''
    def __init__(self,folder,name,seek_end=True,last_lines=0):
        self.name = name
        self.folder = folder
        self.absname = os.path.realpath(os.path.join(self.folder, self.name))
        self.file = None
        if not self.regular_file():
            raise
        self.file = open(self.absname, "r")
        if seek_end:
            self.file.seek(0,os.SEEK_END)
        self.file_id = self.get_file_id()
        logging.debug('watching file %s' % self.absname)
        self.line_terminators = ('\n')
        self.last_lines = last_lines
        if self.last_lines:
            self.go_back_n_lines(lines=self.last_lines)

    def reopen(self):
        self.file.close()
        self.file = open(self.absname, "r")
        self.file_id = self.get_file_id()
        self.last_lines = 0

    def valid(self):
        return self.regular_file()

    def regular_file(self):
        st = os.stat(self.absname)
        if S_ISREG(st.st_mode):
            return True
        return False

    def readfile(self):
        lines = self.file.readlines()
        output = []
        for line in lines:
            entry = {}
            entry['msg'] = line
            entry['file'] = self.absname
            output.append(entry)
        if self.rotated():
            logging.debug('file rotated %s' % self.absname)
            self.reopen()
        if self.truncated():
            logging.debug('file truncated %s' % self.absname)
            self.reopen() 
        return output

    def get_file_id(self):
        st = os.stat(self.absname)
        return "%xg%x" % (st.st_dev, st.st_ino)

    def rotated(self):
        id = self.get_file_id()
        if id != self.file_id:
            return True
        return False

    def truncated(self):
        st = os.stat(self.absname)
        if st.st_size < self.file.tell():
            return True
        return False

    def __del__(self):
        if self.file:
            self.file.close()
        logging.debug('file closed %s' % self.absname)

    def go_back_n_lines(self,lines=0):
        '''
        seeks the file back N lines or the beginning of the file if there
        are not enough lines.  this seeks to the end of the file first.
        '''
        logging.debug('rewinding file back %d lines %s' % (lines,self.absname))
        #import pdb; pdb.set_trace()
        self.file.seek(0,os.SEEK_END)
        pos = self.file.tell()
        n = lines + 2
        while n > 0:
            c = self.file.read(1)
            #logging.debug('char = %s' % c)
            if c in self.line_terminators:
                n -= 1
            pos -= 1
            if pos > 0:
                self.file.seek(pos)
            else:
                self.file.seek(0)
                break
        pos +=2
        self.file.seek(pos)
        #import pdb; pdb.set_trace()
        return 

class DirWatcher(Input):
    '''
    watches a directory on the filesystem and keeps track of files matching
    a regular expression.  keeps changed lines of watched files in a cache.
    properly handles deleted and truncated files.
  
    inputs

        folder = string, required, folder to watch
 
        regex = string, required, regular expression defining files to 
            watch

        sleepfor = integer, default 5, seconds to sleep between scans of 
            of the watched directory for changes

        last_lines = integer, default 0.  when initialized, all files opened
            seek back n lines and will read from there on.  this is useful
            if the process is stopped and you want to get old log data through
            the pipeline.

    outputs
    
       dict like { 'msg' : 'line of data from file', 
                   'file' : '/path/to/file' }
    '''
    def __init__(self, folder, regex='.*\.log', sleepfor=5,last_lines=0):
        '''
        '''
        super(DirWatcher, self).__init__()
        self.sleep_between_checks = sleepfor
        self.files_map = {}
        self.folder = os.path.realpath(folder)
        self.regex = re.compile(regex)
        assert os.path.isdir(self.folder), "%s does not exist" \
                                            % self.folder
        self.last_lines = last_lines
        self.init_files()
        self.cache = []
      

    def __del__(self):
        self.files_map.clear()

    def __iter__(self):
        return self

    def output(self):
        if not self.cache:
            self.update_cache()
        if self.cache:
            return self.cache.pop(0)
        return None

    def listdir(self):
        '''List of files in directory filtered by regex'''
        ls = os.listdir(self.folder)
        return [x for x in ls if self.regex.search(x)]

    def init_files(self):
        for name in self.listdir():
            absname = os.path.realpath(os.path.join(self.folder, name))
            try:
                # add a watcher for each file and seek to the end
                self.files_map[absname] = FileWatcher(folder=self.folder,\
                    name=name,seek_end=True,last_lines=self.last_lines)
            except Exception, err:
                pass 

    def update_cache(self):
        ls = []
        for name in self.listdir():
            absname = os.path.realpath(os.path.join(self.folder, name))
            # file is already in the map
            if absname in self.files_map:
                try:
                    lines = self.files_map[absname].readfile()
                    #import pdb; pdb.set_trace()
                    if lines:
                        for line in lines:
                            self.cache.append(line) 
                except Exception, err:
                    logging.error('file stat error: file=%s error=%s' % \
                         (absname,str(err)))
                    del self.files_map[absname]
            # file is not in the map 
            else:
                try:
                    self.files_map[absname] = FileWatcher(folder=self.folder,\
                        name=name,seek_end=False)
                except Exception, err:
                    pass

        # files in map that should not be
        badfiles = []
        for name in self.files_map:
            try:
                self.files_map[name].valid()
            except Exception, err:
                logging.debug('file bad %s %s' % (name,str(err)))
                badfiles.append(name)
        for key in badfiles:
            logging.debug('unwatching file %s' % key)
            del self.files_map[key]
 
        time.sleep(self.sleep_between_checks)
