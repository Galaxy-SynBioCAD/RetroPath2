#!/usr/bin/env python3
"""
Created on March 5 2019

@author: Melchior du Lac
@description: REST+RQ version of RetroPath2.0

"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from datetime import datetime
from flask import Flask, request, jsonify, send_file, abort
from flask_restful import Resource, Api
import io
import json
import time
from rq import Connection, Queue

from retropath2 import runRetroPath2

#######################################################
############## REST ###################################
#######################################################


app = Flask(__name__)
api = Api(app)


## Stamp of rpCofactors
#
#
def stamp(data, status=1):
    appinfo = {'app': 'RetroPath2.0', 'version': '8.0',
               'author': 'Melchior du Lac',
               'organization': 'BRS',
               'time': datetime.now().isoformat(),
               'status': status}
    out = appinfo.copy()
    out['data'] = data
    return out


## REST App.
#
#
class RestApp(Resource):
    def post(self):
        return jsonify(stamp(None))
    def get(self):
        return jsonify(stamp(None))


## REST Query
#
# REST interface that generates the Design.
# Avoid returning numpy or pandas object in
# order to keep the client lighter.
class RestQuery(Resource):
    def post(self):
        with Connection():
            q = Queue()
            sourcefile = request.files['sourcefile'].read()
            sinkfile = request.files['sinkfile'].read()
            rulesfile = request.files['rulesfile'].read()
            params = json.load(request.files['data'])
            #pass the cache parameters to the rpCofactors object
            scopeCSV = io.BytesIO()
            async_results = q.enqueue(runRetroPath2,
                                      sinkfile,
                                      sourcefile,
                                      params['maxSteps'],
                                      rulesfile,
                                      params['topx'],
                                      params['dmin'],
                                      params['dmax'],
                                      params['mwmax_source'],
                                      params['mwmax_cof'])
            result = None
            while result is None:
                result = async_results.return_value
                time.sleep(2.0)
            scopeCSV.write(result)
            ###### IMPORTANT ######
            scopeCSV.seek(0)
            #######################
            return send_file(scopeCSV, as_attachment=True, attachment_filename='scope.csv', mimetype='text/csv')


api.add_resource(RestApp, '/REST')
api.add_resource(RestQuery, '/REST/Query')


if __name__== "__main__":
    app.run(host="0.0.0.0", port=8991, debug=True, threaded=True)
