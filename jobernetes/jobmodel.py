"""
Class creates a job model from a directory structure.
"""
import logging
import os.path

class JobModel:
    def __init__(self,path='workdir', source_type='directory'):
        self.log = logging.getLogger(__name__)
        self.log.debug('Initialized JobModel')
        self.path = path 
        #if not type directory validate path
        if source_type == 'directory':
            self.log.debug('Checking if path: "%s" exsists' % path)
            if not os.path.exists(path):
                self.log.error('Path does not exist or is not readable: "%s"' %
                               path)
                exit(1)
        
        #validate source type options
        source_type_options = ['directory','git']
        if not source_type in source_type_options:
            self.log.error('ERROR: sourcetype should be one of %s' %
                            source_type_options)
            exit(1)

    def get_phases(self):
        self.phases = []
        for item in os.listdir(self.path):
            if not os.path.isdir(os.path.join(self.path ,item)):
                self.log.debug('Skiping "%s" since it is not a directory' % item)
                continue
            if not item[0].isdigit():
                self.log.debug('Skipping "%s" since it does not start with a'
                               ' digit' % item)
                continue
            self.phases.append(item)
            #end 
        self.phases.sort()
        print(self.phases)
        
