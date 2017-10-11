#!/usr/bin/env python

import logging

import jobernetes

from jobernetes.jobmodel import JobModel
from jobernetes.jobexecutor import JobExecutor

jobernetes.setup_logging()
logger = logging.getLogger(__name__)

logger.info('Starting Jobernetes')

job_model = JobModel()
job_executor = JobExecutor(job_model.get_jobmodel(),
                           namespace='default',
                           ssl_insecure_warnings=False,
                           cleanup=True)

job_executor.start()

