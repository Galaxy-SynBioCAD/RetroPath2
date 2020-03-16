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

sys.path.insert(0, '/home/')
import rpTool

#def run_rp2(sourcefile, sinkfile, rulesfile, max_steps, topx=100, dmin=0, dmax=1000, mwmax_source=1000, mwmax_cof=1000, timeout=30, logger=None):

if __name__ == "__main__":
    #### WARNING: as it stands one can only have a single source molecule
    parser = argparse.ArgumentParser('Python wrapper for the KNIME workflow to run RetroPath2.0')
    parser.add_argument('-sinkfile', type=str)
    parser.add_argument('-sourcefile', type=str)
    parser.add_argument('-max_steps', type=int)
    parser.add_argument('-rulesfile', type=str)
    parser.add_argument('-rulesfile_format', type=str)
    parser.add_argument('-topx', type=int, default=100)
    parser.add_argument('-dmin', type=int, default=0)
    parser.add_argument('-dmax', type=int, default=100)
    parser.add_argument('-mwmax_source', type=int, default=1000)
    parser.add_argument('-mwmax_cof', type=int, default=1000)
    parser.add_argument('-scope_csv', type=str)
    parser.add_argument('-timeout', type=int, default=30)
    params = parser.parse_args()
    if params.max_steps<=0:
        logging.error('Maximal number of steps cannot be less or equal to 0')
        exit(1)
    with tempfile.TemporaryDirectory() as tmpInputFolder:
        if params.rulesfile_format=='csv':
            rulesfile = params.rulesfile
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
            logging.error('Cannot detect the rules_format: '+str(rulesfile_format))
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
                                params.timeout)
        if result[1]==b'timeout':
            logging.error('Timeout of RetroPath2.0')
        elif result[1]==b'memoryerror':
            logging.error('Memory allocation error')
        elif result[1]==b'oserror':
            logging.error('rp2paths has generated an OS error')
        elif result[1]==b'ramerror':
            logging.error.error('Could not setup a RAM limit')
        elif result[0]==b'':
            logging.error('Empty results')
        with open(params.scope_csv, 'wb') as scope_csv:
            scope_csv.write(result[0])
