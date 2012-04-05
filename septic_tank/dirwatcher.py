from inputs import Input
import logging
import re
import time
import os
from stat import S_ISREG

class FileWatcher(object):
    '''
    represents a watched file on the filesystem

    folder = folder where the file is located
    name = file name
    seek_end = if you do not want to seek to the end of the file set this
        to False.  All content in the file will be returned by readfile
        if this is set to False.
    '''
    def __init__(self,folder,name,seek_end=True):
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

    def reopen(self):
        self.file.close()
        self.file = open(self.absname, "r")
        self.file_id = self.get_file_id()

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


class DirWatcher(Input):
    '''
    '''
    def __init__(self, folder, regex='.*\.log', sleepfor=5):
        '''
        '''
        super(DirWatcher, self).__init__()
        self.sleep_between_checks = sleepfor
        self.files_map = {}
        self.folder = os.path.realpath(folder)
        self.regex = re.compile(regex)
        assert os.path.isdir(self.folder), "%s does not exist" \
                                            % self.folder
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
                    name=name,seek_end=True)
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
