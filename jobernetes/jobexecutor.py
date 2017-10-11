"""
Class JobExecutor
"""

import yaml, os, time, datetime, urllib3
from datetime import timedelta
import kubernetes
from kubernetes import client, config
from kubernetes.client import configuration

import logging

class JobExecutor:
    def __init__(self,jobmodel,
                 namespace='default',
                 ssl_insecure_warnings=True,
                 cleanup=True):
        """
        Initialized JobExecutor(jobmodel)
        """
        self.log = logging.getLogger(__name__)
        self.log.debug('Initialized JobExecutor')
        self.jobmodel = jobmodel
        self.__initialize_client()
        self.namespace = namespace
        self.cleanup = cleanup
        if not ssl_insecure_warnings:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    
    def start(self,refresh_time=5):
        the_end = False
        while not the_end:
            state = self.__get_phase()
            self.log.debug('Current phase is %i' % state)
            if state == -1:
                self.log.info('Creating first phase')
                self.__create_phase(0)
            else:
                if self.__is_phase_finished(state):
                    if state == len(self.jobmodel)-1:
                        self.log.info('Finished!')
                        self.__report()
                        if self.cleanup:
                            self.__cleanup_jobs()
                        the_end = True
                        continue
                    else:
                        #if not self.__is_phase_running(state+1):
                        self.log.info('Creating phase %s' % str(state+1))
                        self.__create_phase(state+1)
                else:
                    self.log.info('phase %s is running' % str(state))
                    self.log.info('Checking if depended jobs can be started')
                    self.__update_phase(state)
            self.log.info("Waiting for %i seconds for status update" % refresh_time)
            time.sleep(refresh_time)

    def __report(self):
        totaltime = timedelta(0)
        #totaltime = time.timedelta(0)
        start_times = []
        end_times = []
        for job in self.__get_current_jobs().items:
            start_times.append(job.status.start_time)
            end_times.append(job.status.completion_time)
            time_taken = job.status.completion_time - job.status.start_time
            self.log.info('Job %s took %s' % (job.metadata.name,time_taken))
            totaltime += time_taken
        user_time = sorted(end_times)[-1] - sorted(start_times)[0]
        self.log.info('Total computer runtime is %s' % totaltime)
        self.log.info('Total user time is %s' % user_time)

    def __get_phase(self):
        """
        Gets current phase. It will go trough phases.
        :returns: int current phase (0 is not started)
        """
        job_list = self.__get_current_jobs().items
        current_phase = -1
        if len(job_list) == 0:
            return current_phase
        for i in range(len(self.jobmodel)):
            if len(self.__get_current_jobs(label_selector='jobernetes_phase='+str(i)).items) > 0:
                current_phase += 1
                self.log.debug('Found jobs in phase: %i' % i)
        return current_phase



    def __update_phase(self,phase_num):
        jobs_to_be_created = []
        """
        checks if some jobs are finished so depended jobs can be started
        """
        for job in self.jobmodel[phase_num]['jobs']:
            if 'depends_on' in job and len(job['depends_on']) > 0:
                self.log.debug('Checking dependencies of job: "%s"' % job['kube_job_definition']['metadata']['name'])
                if self.__are_dependencies_finished(job['depends_on']):
                    if not self.__is_job_created(job,phase_num):
                        jobs_to_be_created.append(job)
                        self.log.info('dependencies of job: "%s" are done '
                                      'Creating new job.' % job['kube_job_definition']['metadata']['name'])
        for job in jobs_to_be_created:
            self.kube_client.create_namespaced_job(body=job['kube_job_definition'],
                                                   namespace=self.namespace)
            self.log.info('Created job: "%s"' % job['kube_job_definition']['metadata']['name'])



    def __is_phase_running(self,phase_num):
        """
        Should check if some of the jobs are created and active.  It should check
        """
        checklist = self.__get_current_jobs(label_selector="jobernetes_phase="+str(phase_num)).items
        if len(checklist) > 0:
            return True
        return False

    
    
    def __is_job_created(self,job,phase_num):
        for j in self.__get_current_jobs(label_selector="jobernetes_phase="+str(phase_num)).items:
            if job['kube_job_definition']['metadata']['name'] == j.metadata.name:
                return True
        return False
 

    
    def __is_job_finished(self,job):
        for j in self.__get_current_jobs().items:
            if job == j.metadata.name:
                self.log.debug('Found job %s, checking if finished' % job)
                return not bool(j.status.active)
        return False



    def __is_phase_finished(self,phase_num):
        for job in self.jobmodel[phase_num]['jobs']:
            if not self.__is_job_finished(job['kube_job_definition']['metadata']['name']):
                return False
        return True



    def __are_dependencies_finished(self,dep_array):
        is_finished = True
        for dep in dep_array:
            jobs = self.__get_current_jobs(label_selector="jobernetes_job_name="+dep).items
            if len(jobs) == 0:
                self.log.debug('No jobs are online that have jobernetes name: "%s"' % dep)
                is_finished = False
                continue
            for job in jobs:
                if bool(job.status.active):
                    self.log.debug('Job "%s" is not yet finished' % job.metadata.name)
                    is_finished = False
        return is_finished


    def __create_phase(self,phase_num,timeout=60):
        """
        Creates a phase.
        """
        for job in self.jobmodel[phase_num]['jobs']:
            if not 'depends_on' in job or len(job['depends_on']) == 0:
                self.kube_client.create_namespaced_job(body=job['kube_job_definition'],
                                                       namespace=self.namespace)


    def __initialize_client(self):
        """
        Current requires correct .kube/config and kubectl
        """
        #c = configuration.verify_ssl = False
        config.load_kube_config()
        self.kube_client = client.BatchV1Api()



    def __get_current_jobs(self,label_selector=''):
        """
        Get listing of current jobs
        """
        return self.kube_client.list_namespaced_job(self.namespace,
                                                    _request_timeout=60,label_selector=label_selector)


    def __cleanup_jobs(self):
        phase_num = 0
        for phase in self.jobmodel:
            for job in phase['jobs']:
                if self.__is_job_created(job,phase_num):
                    self.kube_client.delete_namespaced_job(name=job['kube_job_definition']['metadata']['name'],
                                                            body={},
                                                            namespace=self.namespace)
                    self.log.info('Cleaning up job: "%s"' % job['kube_job_definition']['metadata']['name'])
            phase_num += 1




    def job_debug(self,label_selector=''):
        job_list = self.__get_current_jobs(label_selector)
        for job in job_list.items:
            print("%-40s%-15s%-40s%-30s%-25s" % (job.metadata.name,
                               bool(job.status.active),
                               job.spec.template.spec.containers[0].image,
                               job.status.start_time,
                               job.metadata.labels))



#    def __validate_phase(self,phase_num):
#        """
#        Phase should have all jobs are none.
#        :param: int phase_num
#        :returns: bool
#        """
#        current_job_names = self.__list_current_job_names(label_selector="jobernetes_phase="+str(phase_num))
#        for kube_job_name in self.jobmodel[phase_num]['jobs']:
#            if not kube_job_name['kube_job_definition']['metadata']['name'] in current_job_names:
#                return False
#        return True

#    def __list_current_job_names(self,label_selector=''):
#        name_list = []
#        for job in self.__get_current_jobs(label_selector).items:
#            name_list.append(job.metadata.name)
#        return name_list

#    def __is_job_created(self,job_name):
#        """
#        Checks if job is created
#        :param: str job_name required
#        :returns: Bool
#        """
#        for job in self.__get_current_jobs().items:
#            if job.metadata.name == job_name:
#                return True
#        return False
#
