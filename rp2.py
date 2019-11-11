#!/usr/bin/env python3
"""
Created on March 5 2019

@author: Melchior du Lac
@description: REST+RQ version of RetroPath2.0

"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import subprocess
import logging
import resource
from datetime import datetime
from flask import Flask, request, jsonify, send_file, abort
from flask_restful import Resource, Api
import io
import os
import tempfile
import glob

#Linux
#KPATH = '/home/src/knime_3.6.2/knime'
KPATH = '/home/mdulac/src/knime_3.6.2/knime'
#Mac OSX
#KPATH = '/Applications/KNIME\ 3.6.1.app/Contents/MacOS/Knime'
#Linux
#RP_WORK_PATH = '/home/mdulac/Downloads/RetroPath2.0_docker_test/RetroPath2.0/RetroPath2.0.knwf'
#Mac OSX
RP_WORK_PATH = '/home/mdulac/src/RetroPath2.0.knwf'
#MAX_VIRTUAL_MEMORY = 10 * 1024 * 1024 # 10 MB
MAX_VIRTUAL_MEMORY = 15000 * 1024 * 1024 # 15 GB -- define what is the best


def limit_virtual_memory():
    resource.setrlimit(resource.RLIMIT_AS, (MAX_VIRTUAL_MEMORY, resource.RLIM_INFINITY))


def run_userTMP(sinkfile_bytes, sourcefile_bytes, maxSteps, rulesfile_bytes, topx=100, dmin=0, dmax=1000, mwmax_source=1000, mwmax_cof=1000):
    rp2_pathways = b''
    #with tempfile.TemporaryDirectory() as tmpfolder:
    tmpfolder = os.getcwd()+'/rp2_test'
    print('using tmp folder: '+str(tmpfolder))
    #write the input to file
    sourcefile = tmpfolder+'/source.csv'
    with open(sourcefile, 'wb') as sourcefi:
        sourcefi.write(sourcefile_bytes)
    sinkfile = tmpfolder+'/sink.csv'
    with open(sinkfile, 'wb') as sinkfi:
        sinkfi.write(sinkfile_bytes)
    if rulesfile_bytes==b'':
        #Mac OSX
        #rulesfile = 'Users/melchior/Documents/retrorules_rr02_rp2_hs/retrorules_rr02_rp2_flat_forward.csv'
        rulesfile = '/home/mdulac/src/retrorules_rr02_rp2_flat_retro.csv'
        #Linux
        print('Using stored rules: '+str(rulesfile))
    else:
        rulesfile = tmpfolder+'/rules.csv'
        with open(rulesfile, 'wb') as rulesfi:
            rulesfi.write(rulesfile_bytes)
        print('Using tmp writing: '+str(rulesfile))
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
                '-workflow.variable=output.dir,"'+str(tmpfolder)+'/",String',
                '-workflow.variable=output.solutionfile,"results.csv",String',
                '-workflow.variable=output.sourceinsinkfile,"source-in-sink.csv",String']
        print('#################')
        print(knime_command)
        print('#################')
        print('#################')
        commandObj = subprocess.Popen(knime_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, preexec_fn=limit_virtual_memory)
        commandObj.wait()
        (result, error) = commandObj.communicate()
        result = result.decode('utf-8')
        error = error.decode('utf-8')
        print('#################')
        print(result)
        print('#################')
        print('#################')
        print(error)
        print('#################')
        print(glob.glob(tmpfolder+'/*'))
        if 'There is insufficient memory for the Java Runtime Environment to continue' in result:
            logging.error('RetroPath2.0 does not have sufficient memory to continue')
        else:
            try:
                csvScope = glob.glob(tmpfolder+'/*_scope.csv')
                with open(csvScope[0], mode='rb') as scopeFile:
                    rp2_pathways = scopeFile.read()
            except IndexError:
                logging.warning('ERROR: RetroPath2.0 has not found any results')
    except OSError as e:
        logging.error('Running the RetroPath2.0 Knime program produced an OSError')
        logging.error(e)
    except ValueError as e:
        logging.error('Cannot set the RAM usage limit')
        logging.error(e)
    return rp2_pathways

def run(sinkfile_bytes, sourcefile_bytes, maxSteps, rulesfile_bytes, topx=100, dmin=0, dmax=1000, mwmax_source=1000, mwmax_cof=1000):
    rp2_pathways = b''
    with tempfile.TemporaryDirectory() as tmpfolder:
        print('using tmp folder: '+str(tmpfolder))
        #write the input to file
        sourcefile = tmpfolder+'/source.csv'
        with open(sourcefile, 'wb') as sourcefi:
            sourcefi.write(sourcefile_bytes)
        sinkfile = tmpfolder+'/sink.csv'
        with open(sinkfile, 'wb') as sinkfi:
            sinkfi.write(sinkfile_bytes)
        if rulesfile_bytes==b'':
            #Mac OSX
            #rulesfile = 'Users/melchior/Documents/retrorules_rr02_rp2_hs/retrorules_rr02_rp2_flat_forward.csv'
            rulesfile = '/home/mdulac/src/retrorules_rr02_rp2_flat_retro.csv'
            #Linux
            print('Using stored rules: '+str(rulesfile))
        else:
            rulesfile = tmpfolder+'/rules.csv'
            with open(rulesfile, 'wb') as rulesfi:
                rulesfi.write(rulesfile_bytes)
            print('Using tmp writing: '+str(rulesfile))
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
                    '-workflow.variable=output.dir,"'+str(tmpfolder)+'/",String',
                    '-workflow.variable=output.solutionfile,"results.csv",String',
                    '-workflow.variable=output.sourceinsinkfile,"source-in-sink.csv",String']
            print('#################')
            print(knime_command)
            print('#################')
            print('#################')
            commandObj = subprocess.Popen(knime_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, preexec_fn=limit_virtual_memory)
            commandObj.wait()
            (result, error) = commandObj.communicate()
            result = result.decode('utf-8')
            error = error.decode('utf-8')
            print('#################')
            print(result)
            print('#################')
            print('#################')
            print(error)
            print('#################')
            print(glob.glob(tmpfolder+'/*'))
            if 'There is insufficient memory for the Java Runtime Environment to continue' in result:
                logging.error('RetroPath2.0 does not have sufficient memory to continue')
            else:
                try:
                    csvScope = glob.glob(tmpfolder+'/*_scope.csv')
                    with open(csvScope[0], mode='rb') as scopeFile:
                        rp2_pathways = scopeFile.read()
                except IndexError:
                    logging.warning('ERROR: RetroPath2.0 has not found any results')
        except OSError as e:
            logging.error('Running the RetroPath2.0 Knime program produced an OSError')
            logging.error(e)
        except ValueError as e:
            logging.error('Cannot set the RAM usage limit')
            logging.error(e)
    return rp2_pathways
