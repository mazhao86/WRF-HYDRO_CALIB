import shutil
import os 
import time 
import sys 
import datetime 
import logging
import yaml 

libPathList = ['./lib/Python', './util']
for libPath in libPathList:
	sys.path.insert(0,libPath)
from adjustParameters import *
from adjustForcings import adjustForcings
from sanityPreCheck import RunPreCheck, RunCalibCheck, RunPreSubmitTest


# setup the log file --- this will get passed to all of the imported modules!!!
suffix = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
logfile= 'logfile_{}.log'.format(suffix)

file_handler = logging.FileHandler(filename=logfile)
stdout_handler = logging.StreamHandler(sys.stdout)
logging.basicConfig(level=logging.INFO, 
		    format='%(asctime)s %(name)15s %(levelname)-8s %(message)s',
		    datefmt='%a, %d %b %Y %H:%M:%S',
		    handlers=[file_handler, stdout_handler]
		    )
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# -----  main ------ 
setupfile = 'setup.yaml'
calibrationfile = 'calib_params.tbl' 

# start the logging with some handy info
logger.info('starting {}. using {} setup parameters and {}' .format(__name__, setupfile, calibrationfile))
logger.info('Logging to file: {}/{}'.format(os.getcwd(), logfile))

# ---- run 'sanity checks' -----  
#if not RunPreCheck(setupfile).run_all(): sys.exit()
#if not RunCalibCheck(setupfile).run_all(): sys.exit()

# create the setup instance 
setup = SetMeUp(setupfile)
#setup()   # gather forcing files, create directories, etc.
#
## check that setup() was successful 
#if not RunPreSubmitTest(setupfile).run_all(): sys.exit()
calib = CalibrationMaster(setupfile)
#calib.ForwardModel() # run once, no updating parameters 

param_cmd = "SELECT * FROM PARAMETERS"
param = pd.read_sql(sql = param_cmd, con="sqlite:///{}/CALIBRATION.db".format(setup.clbdirc))
lastState = param.loc[param.Iteration == param.Iteration.iloc[-1]]
lastState.set_index('parameter', inplace=True)
calib.df.update(lastState)
calib.df.nextValue = calib.df.currentValue 
# update the iteration 
calib.iters = int(lastState.Iteration.iloc[0])+1
calib()

# now run the calibration 

## clean up 
logger.info('----- Calibration Complete -----')
logger.info('moving logfile {} to directory {}'.format(logfile, clbdirc))
shutil.move(logfile, setup.clbdirc+'/'+logfile)  # move the log file to the directory 
# make some plots or something ....
#
