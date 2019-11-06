#!/usr/bin/env python3
"""
Created on March 5 2019

@author: Melchior du Lac
@description: REST+RQ version of RetroPath2.0

"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import random
import string
import subprocess
import logging
import shutil
import resource
from datetime import datetime
from flask import Flask, request, jsonify, send_file, abort
from flask_restful import Resource, Api
import io
import os

#Linux
#KPATH = '/home/mdulac/knime_3.6.1/knime'
#Mac OSX
#KPATH = '/Applications/KNIME\ 3.6.1.app/Contents/MacOS/Knime'
KPATH = '"/Applications/KNIME\ 3.6.1.app/Contents/MacOS/Knime"'
#Linux
#RP_WORK_PATH = '/home/mdulac/Downloads/RetroPath2.0_docker_test/RetroPath2.0/RetroPath2.0.knwf'
#Mac OSX
RP_WORK_PATH = '/Users/melchior/Downloads/RetroPath2.0/RetroPath2.0.knwf'
#MAX_VIRTUAL_MEMORY = 10 * 1024 * 1024 # 10 MB
MAX_VIRTUAL_MEMORY = 15000 * 1024 * 1024 # 15 GB -- define what is the best


def limit_virtual_memory():
    resource.setrlimit(resource.RLIMIT_AS, (MAX_VIRTUAL_MEMORY, resource.RLIM_INFINITY))


def runRetroPath2(sinkfile, sourcefile, maxSteps, rulesfile=None, topx=100, dmin=0, dmax=1000, mwmax_source=1000, mwmax_cof=1000):
    if not os.path.exists(os.getcwd()+'/tmp'):
        os.mkdir(os.getcwd()+'/tmp')
    tmpOutputFolder = os.getcwd()+'/tmp/'+''.join(random.choice(string.ascii_lowercase) for i in range(15))
    os.mkdir(tmpOutputFolder)
    if rulesfile==None:
        #Mac OSX
        rulesfile = 'Users/melchior/Documents/retrorules_rr02_rp2_hs/retrorules_rr02_rp2_flat_forward.csv'
        #Linux
    try:
        knime_command = [KPATH,
                '-nosplash',
                '-nosave',
                '-reset',
                '--launcher.suppressErrors',
                '-application',
                'org.knime.product.KNIME_BATCH_APPLICATION',
                '-workflowFile='+RP_WORK_PATH,
                '-workflow.variable=input.dmin,"'+str(dmin)+'",int',
                '-workflow.variable=input.dmax,"'+str(dmax)+'",int',
                '-workflow.variable=input.max-steps,"'+str(maxSteps)+'",int',
                '-workflow.variable=input.sourcefile,"'+str(sourcefile)+'",String',
                '-workflow.variable=input.sinkfile,"'+str(sinkfile)+'",String',
                '-workflow.variable=input.rulesfile,"'+str(rulesfile)+'",String',
                '-workflow.variable=output.topx,"'+str(topx)+'",int',
                '-workflow.variable=output.mwmax-source,"'+str(mwmax_source)+'",int',
                '-workflow.variable=output.mwmax-cof,"'+str(mwmax_cof)+'",int',
                '-workflow.variable=output.dir,"'+str(tmpOutputFolder)+'/",String',
                '-workflow.variable=output.solutionfile,"results.csv",String',
                '-workflow.variable=output.sourceinsinkfile,"source-in-sink.csv",String']
        #commandObj = subprocess.Popen(knime_command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=False, preexec_fn=limit_virtual_memory)
        commandObj = subprocess.Popen(knime_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, preexec_fn=limit_virtual_memory)
        #exit_code = subprocess.run(knime_command)
        commandObj.wait()
        (result, error) = commandObj.communicate()
        result = result.decode('utf-8')
        error = error.decode('utf-8')
        #print('exit_code: '+str(exit_code))
        """
        print('####################### result ###########################')
        print(result)
        print('####################### error ############################')
        print(error)
        """
        if 'There is insufficient memory for the Java Runtime Environment to continue' in result:
            logging.error('RetroPath2.0 does not have sufficient memory to continue')
            shutil.rmtree(tmpOutputFolder)
            return b''
    except OSError as e:
        logging.error('Running the RetroPath2.0 Knime program produced an OSError')
        logging.error(e)
        shutil.rmtree(tmpOutputFolder)
        return b''
    except ValueError as e:
        logging.error('Cannot set the RAM usage limit')
        logging.error(e)
        shutil.rmtree(tmpOutputFolder)
        return b''
    try:
        csvScope = glob.glob(tmpOutputFolder+'/*_scope.csv')
        with open(csvScope[0], mode='rb') as scopeFile:
            fileContent = scopeFile.read()
        shutil.rmtree(tmpOutputFolder)
        return fileContent
    except IndexError:
        logging.warning('ERROR: RetroPath2.0 has not found any results')
        shutil.rmtree(tmpOutputFolder)
        return b''
    shutil.rmtree(tmpOutputFolder)
    return b''
