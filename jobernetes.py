#!/usr/bin/env python

import logging

import jobernetes

from jobernetes.jobmodel import JobModel


jobernetes.setup_logging()
logger = logging.getLogger(__name__)

logger.info('Starting Jobernetes')

jobmodel = JobModel(path='test-dir/simple')
jobmodel.get_phases()
