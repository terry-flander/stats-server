# server.py

from flask import Flask, jsonify, request
import argparse
import statistics_lib as sl
import json

app = Flask(__name__)

parser = argparse.ArgumentParser(description="Create Summary Catania Statistics")

parser.add_argument("--url", required=False, default="http://127.0.0.1:5000/stats/api/v1.0/test?offset=4")
parser.add_argument("--dataFolder", required=False, default="./test-data")
parser.add_argument("--saveFolder", required=False, default='summary-data')
parser.add_argument("--summaryStatList", required=False, default=f"./summary-stat-list.csv")
parser.add_argument("--maxInterval", required=False, default=10)
parser.add_argument("--logLevel", required=False, default=0, type=int)
args = parser.parse_args()

@app.route('/stats/api/v1.0/file', methods=['GET'])
def process_files():
    dataFolder = request.args.get('dataFolder', default=args.dataFolder, type=str)
    logLevel = request.args.get('logLevel', default=args.logLevel, type=int)
    result = sl.statisticsFromFiles(dataFolder, args.summaryStatList, args.saveFolder, logLevel)
    return jsonify(result)

@app.route('/stats/api/v1.0/url', methods=['GET'])
def process_url():
    url = request.args.get('url', default=args.url)
    dataFolder = request.args.get('dataFolder', default='', type=str)
    logLevel = request.args.get('logLevel', default=args.logLevel, type=int)
    if len(dataFolder) > 0:
        url += '&dataFolder=' + dataFolder
    result = sl.statisticsFromUrl(url, args.summaryStatList, args.saveFolder, args.maxInterval, logLevel)
    response = app.response_class(
        response=json.dumps(result, default=int),
        mimetype='application/json'
    )
    return response

@app.route('/stats/api/v1.0/test', methods=['GET'])
def get_test():
    offset = request.args.get('offset', default=0, type=int)    
    dataFolder = request.args.get('dataFolder', default=args.dataFolder, type=str)
    logLevel = request.args.get('logLevel', default=args.logLevel, type=int)
    return jsonify(sl.getTestStatistics(dataFolder, offset, logLevel))

if __name__ == '__main__':
    app.run(debug=True)
 