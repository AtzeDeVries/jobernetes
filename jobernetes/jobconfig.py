"""
Class creates a jobconfig from yaml
"""
import logging
import os.path
import yaml

class JobConfig:
    def __init__(self,path='jobermodel.yaml', source_type='file'):
        """
        Initialized Jobmodel (path=jobmodel,source_type='file')
        """
        self.log = logging.getLogger(__name__)
        self.log.debug('Initialized JobConfig')
        self.path = path 
        source_type = 'file' #shameless override (git/url should beimplemented)
        #if not type directory validate path
        if source_type == 'file':
            self.log.debug('Checking if path: "%s" exsists' % path)
            if not os.path.exists(path):
                self.log.error('Path does not exist or is not readable: "%s"' %
                               path)
                exit(1)

        #validate source type options
        source_type_options = ['file','git','url']
        if not source_type in source_type_options:
            self.log.error('ERROR: sourcetype should be one of %s' %
                            source_type_options)
            exit(1)

    def get_jobconfig(self):
        """
        Returns a config Object
        """
        with open(self.path, 'rt') as f:
            self.log.debug('Opening joberconfig "%s"' % self.path)
            overrides = yaml.safe_load(f.read())['jobernetes_config']

        config = self.__config_defaults()
        for key in overrides:
            config[key] = overrides[key]
        self.log.debug('Running with config: %s' % config)
        return config


    def __config_defaults(self):
        return {'cleanup': False,
                'kubernetes_namespace' : 'default',
                'ssl_insecure_warnings' : True,
                'refresh_time': 5
                }
