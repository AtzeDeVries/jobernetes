#!/usr/bin/env python

import logging

import jobernetes

from jobernetes.jobmodel import JobModel
from jobernetes.jobexecutor import JobExecutor
from jobernetes.jobconfig import JobConfig

jobernetes.setup_logging()
logger = logging.getLogger(__name__)

logger.info('Starting Jobernetes')

### Get the Jobmodel
job_model = JobModel()
### Get the config
job_config = JobConfig()

cfg = job_config.get_jobconfig()

job_executor = JobExecutor(job_model.get_jobmodel(),
                           namespace=cfg['kubernetes_namespace'],
                           ssl_insecure_warnings=cfg['ssl_insecure_warnings'],
                           cleanup=cfg['cleanup'],
                           refresh_time=cfg['refresh_time'],
                           incluster=cfg['incluster'])

job_executor.start()

