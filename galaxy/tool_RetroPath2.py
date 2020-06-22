#!/usr/bin/env python3
"""
Created on September 21 2019

@author: Melchior du Lac
@description: Galaxy script to query rpRetroPath2.0 REST service

"""
import sys
import argparse
import logging
import tempfile
import tarfile
import glob
import shutil

sys.path.insert(0, '/home/')
import rpTool

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
)

logging.disable(logging.INFO)
#logging.disable(logging.WARNING)


if __name__ == "__main__":
    #### used to pass the logger to the 
    logger = logging.getLogger(__name__)
    #### WARNING: as it stands one can only have a single source molecule
    parser = argparse.ArgumentParser('Python wrapper for the KNIME workflow to run RetroPath2.0')
    parser.add_argument('-sinkfile', type=str)
    parser.add_argument('-sourcefile', type=str)
    parser.add_argument('-max_steps', type=int)
    parser.add_argument('-rulesfile', type=str)
    parser.add_argument('-rulesfile_format', type=str)
    parser.add_argument('-scope_csv', type=str)
    parser.add_argument('-topx', type=int, default=100)
    parser.add_argument('-dmin', type=int, default=0)
    parser.add_argument('-dmax', type=int, default=100)
    parser.add_argument('-mwmax_source', type=int, default=1000)
    parser.add_argument('-mwmax_cof', type=int, default=1000)
    parser.add_argument('-timeout', type=int, default=90)
    parser.add_argument('-partial_retro', type=str, default='False')
    params = parser.parse_args()
    if params.max_steps<=0:
        logging.error('Maximal number of steps cannot be less or equal to 0')
        exit(1)
    if params.topx<0:
        logging.error('Cannot have a topx value that is <0: '+str(params.topx))
        exit(1)
    if params.dmin<0:
        logging.error('Cannot have a dmin value that is <0: '+str(params.dmin))
        exit(1)
    if params.dmax<0:
        logging.error('Cannot have a dmax value that is <0: '+str(params.dmax))
        exit(1)
    if params.dmax>1000:
        logging.error('Cannot have a dmax valie that is >1000: '+str(params.dmax))
        exit(1)
    if params.dmax<params.dmin:
        logging.error('Cannot have dmin>dmax : dmin: '+str(params.dmin)+', dmax: '+str(params.dmax))
        exit(1)
    if params.partial_retro=='False' or params.partial_retro=='false' or params.partial_retro=='F':
        partial_retro = False
    elif params.partial_retro=='True' or params.partial_retro=='true' or params.partial_retro=='T':
        partial_retro = True
    else:
        logging.error('Cannot interpret partial_retro: '+str(params.partial_retro))
        exit(1)
    with tempfile.TemporaryDirectory() as tmpInputFolder:
        if params.rulesfile_format=='csv':
            logging.info('Rules file: '+str(params.rulesfile))
            rulesfile = tmpInputFolder+'/rules.csv'
            shutil.copy(params.rulesfile, rulesfile)
            logging.info('Rules file: '+str(rulesfile))
        elif params.rulesfile_format=='tar':
            with tarfile.open(params.rulesfile) as rf:
                rf.extractall(tmpInputFolder)
            out_file = glob.glob(tmpInputFolder+'/*.csv')
            if len(out_file)>1:
                logging.error('Cannot detect file: '+str(glob.glob(tmpInputFolder+'/*.csv')))
                exit(1)
            elif len(out_file)==0:
                logging.error('The rules tar input is empty')
                exit(1)
            rulesfile = out_file[0]
        else:
            logging.error('Cannot detect the rules_format: '+str(params.rulesfile_format))
            exit(1)
        result = rpTool.run_rp2(params.sourcefile,
                                params.sinkfile,
                                rulesfile,
                                params.max_steps,
                                params.topx,
                                params.dmin,
                                params.dmax,
                                params.mwmax_source,
                                params.mwmax_cof,
                                params.timeout,
                                partial_retro)
        if result[1]==b'timeouterror':
            logging.error('Timeout of RetroPath2.0')
            exit(1)
        elif result[1]==b'memoryerror':
            logging.error('Memory allocation error')
            exit(1)
        elif result[1]==b'oserror':
            logging.error('rp2paths has generated an OS error')
            exit(1)
        elif result[1]==b'ramerror':
            logging.error('Could not setup a RAM limit')
            exit(1)
        elif result[1]==b'timeoutwarning' or result[1]==b'memwarning' or result[1]==b'noresultwarning' or result[1]==b'oswarning' or result[1]==b'ramwarning':
            logging.warning(result[2])
            logging.warning('Returning partial results')
        if result[0]==b'':
            logging.error('Empty results')
            exit(1)
        with open(params.scope_csv, 'wb') as scope_csv:
            scope_csv.write(result[0])
