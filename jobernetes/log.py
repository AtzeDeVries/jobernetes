
import logging

class Log:
    def __init__(self, log_level='INFO', log_file='jobernetes.log',
                 log_to_console=True, log_to_journal=False, log_to_file=False):

        level =logging.getLevelName(log_level)  
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s\t- %(module)s::%(funcName)s - %(message)s')
        
        if log_to_journal:
            from systemd.journal import JournalHandler
            self.logger.setLevel(level)
            logger.addHandler(JournalHandler())
        
        if log_to_file:
            fh = logging.FileHandler(log_file)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)
        
        if log_to_console:
            sh = logging.StreamHandler()
            sh.setFormatter(formatter)
            self.logger.addHandler(sh)
