#!/usr/bin/env python3
"""
Created on September 21 2019

@author: Melchior du Lac
@description: Extract the sink from an SBML into RP2 friendly format

"""
import argparse
import tempfile
import os
import logging
import shutil
import docker


##
#
#
def main(sinkfile,
         sourcefile,
         max_steps,
         rulesfile,
         rulesfile_format,
         scope_csv,
         topx=100,
         dmin=0,
         dmax=1000,
         mwmax_source=1000,
         mwmax_cof=1000,
         timeout=90):
    docker_client = docker.from_env()
    image_str = 'brsynth/retropath2-standalone:dev'
    try:
        image = docker_client.images.get(image_str)
    except docker.errors.ImageNotFound:
        logging.warning('Could not find the image, trying to pull it')
        try:
            docker_client.images.pull(image_str)
            image = docker_client.images.get(image_str)
        except docker.errors.ImageNotFound:
            logging.error('Cannot pull image: '+str(image_str))
            exit(1)
    with tempfile.TemporaryDirectory() as tmpOutputFolder:
        shutil.copy(sinkfile, tmpOutputFolder+'/sink.csv')
        shutil.copy(sourcefile, tmpOutputFolder+'/source.csv')
        shutil.copy(rulesfile, tmpOutputFolder+'/rules.dat')
        command = ['/home/tool_RetroPath2.py',
                   '-sinkfile',
                   '/home/tmp_output/sink.csv',
                   '-sourcefile',
                   '/home/tmp_output/source.csv',
                   '-max_steps',
                   str(max_steps),
                   '-rulesfile',
                   '/home/tmp_output/rules.dat',
                   '-rulesfile_format',
                   str(rulesfile_format),
                   '-topx',
                   str(topx),
                   '-dmin',
                   str(dmin),
                   '-dmax',
                   str(dmax),
                   '-mwmax_source',
                   str(mwmax_source),
                   '-mwmax_cof',
                   str(mwmax_cof),
                   '-scope_csv',
                   '/home/tmp_output/output.dat',
                   '-timeout',
                   str(timeout)]
        container = docker_client.containers.run(image_str,
                                                 command,
                                                 detach=True,
                                                 stderr=True,
                                                 volumes={tmpOutputFolder+'/': {'bind': '/home/tmp_output', 'mode': 'rw'}})
        container.wait()
        err = container.logs(stdout=False, stderr=True)
        err_str = err.decode("utf-8")
        print(err_str)
        if not 'ERROR' in err_str:
            shutil.copy(tmpOutputFolder+'/output.dat', scope_csv)
        container.remove()


##
#
#
if __name__ == "__main__":
    parser = argparse.ArgumentParser('Python wrapper to run RetroPath2.0')
    parser.add_argument('-sinkfile', type=str)
    parser.add_argument('-sourcefile', type=str)
    parser.add_argument('-max_steps', type=int)
    parser.add_argument('-rulesfile', type=str)
    parser.add_argument('-rulesfile_format', type=str)
    parser.add_argument('-topx', type=int, default=100)
    parser.add_argument('-dmin', type=int, default=0)
    parser.add_argument('-dmax', type=int, default=1000)
    parser.add_argument('-mwmax_source', type=int, default=1000)
    parser.add_argument('-mwmax_cof', type=int, default=1000)
    parser.add_argument('-scope_csv', type=str)
    parser.add_argument('-timeout', type=int, default=90)
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
    main(params.sinkfile,
         params.sourcefile,
         params.max_steps,
         params.rulesfile,
         params.rulesfile_format,
         params.scope_csv,
         params.topx,
         params.dmin,
         params.dmax,
         params.mwmax_source,
         params.mwmax_cof,
         params.timeout)
