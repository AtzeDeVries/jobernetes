"""
Class creates a job model from a directory structure.
"""
import logging
import os.path
import yaml
import json

class JobModel:
    def __init__(self,path='jobermodel.yaml', source_type='file'):
        """
        Initialized Jobmodel (path=jobmodel,source_type='file')
        """
        self.log = logging.getLogger(__name__)
        self.log.debug('Initialized JobModel')
        self.path = path 
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

    def get_jobmodel(self):
        """
        Returns a phases Object
        """
        with open(self.path, 'rt') as f:
            self.log.debug('Opening jobermodel "%s"' % self.path)
            phases = yaml.safe_load(f.read())['jobernetes']
        self.__validate_jobmodel(phases)
        for phase in phases:
            self.__explode_directory(phase)
        self.__extend_jobmodel(phases)
        self.log.info('Imported jobermodel from "%s"' % self.path)
        return phases

    def __extend_jobmodel(self,phases):
        count = 0
        for phase in phases:
            for job in phase['jobs']:
                job['kube_job_definition'] = self.__get_kube_job_definition(job['job_path'])
                job['kube_job_definition']['metadata']['labels']['jobernetes_job_name'] = job['name']
                job['kube_job_definition']['metadata']['labels']['jobernetes_phase'] = str(count)
                job['kube_job_definition']['metadata']['labels']['jobernetes_exploded'] = str('type' in job and job['type']=='exploded')
            count += 1

    def __explode_directory(self,phase):
        new_job_array = []
        for job in phase['jobs']:
            if self.__is_job_type_directory(job):
                count = 0
                for f in self.__directory_filelist(job):
                    #name = '%s-exploded-job-%s' % (job['name'],self.__generate_number_sequence(count))
                    appender = {'name': job['name'], 'job_path': f, 'type': 'exploded'}
                    if 'depends_on' in job:
                        appender['depends_on'] = job['depends_on']
                    count += 0
                    new_job_array.append(appender)
            else:
                new_job_array.append(job)
        phase['jobs'] = new_job_array
        return phase

    def __generate_number_sequence(self,count,lenght=8):
        string = ""
        for i in range(lenght - len(str(count))):
            string = string + "0"
        return string + str(count)

    def __validate_jobmodel(self,phases,dry_run=False):
        """
        Validates the Jobmodel
        * checks if job path exist
        * checks if job path is correct
        * checks if dependencies exists
        * Should check if job names are unique (to be implemented)
        * should check names on spaces (not allowed)
        """
        ok=True
        for phase in phases:
            self.log.debug('Checking phase: "%s"' % phase['phase_name'])
            for job in phase['jobs']:
                #validate paths
                self.log.debug('Check if path "%s" exists' % job['job_path'])
                if not os.path.exists(job['job_path']):
                    ok=False
                    self.log.warn('Path does not exist or is not readable: "%s"' %
                               job['job_path'])
                else:
                    self.log.debug('Check if path "%s" is dir or file' %
                                   job['job_path'] )
                    if 'type' in job and job['type'] == 'directory':
                        if os.path.isfile(job['job_path']):
                            ok=False
                            self.log.warn('Job is a directory but path is a '
                                          'file "%s"'% job['job_path'])
                    else:
                        if os.path.isdir(job['job_path']):
                            ok=False
                            self.log.warn('Job is a file but path is a '
                                          'directory "%s"'% job['job_path'])
                #validate dependencies
                if 'depends_on' in job:
                    for dep in job['depends_on']:
                        self.log.debug('Check if dependencies "%s" from job '
                                       '"%s" exists' % (dep,job['name']))
                        if not self.__validate_dependency(phase,dep):
                            ok=False
                            self.log.warn('Dependency "%s" of job "%s" does '
                                          'not exist' % (dep,job['name']))

        if not dry_run and not ok:
            self.log.error('Validation of jobermodel failed, exiting.')
            exit(1)



    def __validate_dependency(self,current_phase,dependency):
        """
        Validates a depenency, returns True/False
        Requires 'current_phase' and 'depenceny'
        """
        for job in current_phase['jobs']:
            if job['name'] == dependency:
                return True
        return False

    def __is_job_type_directory(self,job):
        return 'type' in job and job['type'] == 'directory'

    def __directory_filelist(self,job):
        """
        Only use if jobtype is directory.
        :param: job (dict type: directory)
        :returns: array of files in job directory
        """
        filelist = []
        for _, _, files in os.walk(job['job_path']):
            for job_file in files:
               self.log.debug('Checking file %s' % job_file)
               if job_file.split('.')[-1] in ['yml','yaml','json']:
                   filelist.append(os.path.join(job['job_path'],job_file))
        return filelist

    def __get_kube_job_definition(self,job_path):
        if job_path.split('.')[-1] in ['yml','yaml']:
            with open(job_path) as f:
                self.log.debug('Opening kubejob "%s"' % job_path)
                return yaml.safe_load(f.read())
        elif job_path.split('.')[-1] in ['json']:
            with open(job_path) as f:
                self.log.debug('Opening kubejob "%s"' % job_path)
                return json.safe_load(f.read())
        else:
            self.log.error('Fail, jobpath: "%s" should be yml,yaml or json')
            exit(1)



