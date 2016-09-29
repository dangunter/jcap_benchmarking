"""
Simple Flask REST API for JCAP database
"""
__author__ = 'Dan Gunter <dkgunter@lbl.gov>'
__date__ = '9/29/16'

import json
import datetime

import flask
import pymongo

app = flask.Flask(__name__)

iso_now = lambda: datetime.datetime.isoformat(datetime.datetime.now())

@app.route('/')
def home():
    return 'Hello from the JCAP demo'

@app.route('/jcap-benchmark/rest/v1/filter')
def jcap_filter():
    client = pymongo.MongoClient()
    coll = client.test.jcap
    query = {}
    for key, value in flask.request.args.items():
        query['{}.value.text'.format(key)] = value
    results = list(coll.find(query))
    json_results = json.dumps({
        'result': results,
        'parameters': flask.request.args,
        'timestamp': iso_now()
    })
    return json_results
