__all__ = ['log', 'logging', 'ALL', 'VERBOSE', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'FATAL'] # what we get when importing *

import logging

# Configure logging levels to match GAUDI/ATHENA
logging.VERBOSE = logging.DEBUG - 1
logging.ALL     = logging.DEBUG - 2
logging.addLevelName(logging.VERBOSE, 'VERBOSE' )
logging.addLevelName(logging.ALL, 'ALL' )

# Add verbose/all methods
def all( self, msg, *args, **kwargs):
    if self.manager.disable >= logging.ALL:
        return
    if logging.ALL >= self.getEffectiveLevel():
        apply(self._log, (logging.ALL, msg, args), kwargs)

def verbose( self, msg, *args, **kwargs):
    if self.manager.disable >= logging.VERBOSE:
        return
    if logging.VERBOSE >= self.getEffectiveLevel():
        apply(self._log, (logging.VERBOSE, msg, args), kwargs)                

loggingClass = logging.getLoggerClass()
loggingClass.all = all
loggingClass.verbose = verbose

# Create looger and set level to INFO
log = logging.getLogger("OSLogging")
log.setLevel(logging.INFO)

# Create console handler and set level to INFO
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Set output format
format = logging.Formatter("%(module)-14s%(levelname)8s %(message)s")
ch.setFormatter(format)
log.addHandler(ch)

# Output levels
ALL     = logging.ALL
VERBOSE = logging.VERBOSE
DEBUG   = logging.DEBUG
INFO    = logging.INFO
WARNING = logging.WARNING
ERROR   = logging.ERROR
FATAL   = logging.FATAL
