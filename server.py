# server.py

from flask import Flask, jsonify, request, render_template
import argparse
import statistics_lib as sl
import json
import traceback

app = Flask(__name__, static_folder='static')

parser = argparse.ArgumentParser(description="Create Summary Catania Statistics")

parser.add_argument("--url", required=False, default="http://127.0.0.1:5000/stats/api/v1.0/test?offset=4")
parser.add_argument("--dataFolder", required=False, default="./data/test-data")
parser.add_argument("--saveFolder", required=False, default='./data/summary-data')
parser.add_argument("--summaryStatList", required=False, default=f"./conf/summary-stat-list.csv")
parser.add_argument("--maxInterval", required=False, default=10)
parser.add_argument("--logLevel", required=False, default=0, type=int)
args, unknown = parser.parse_known_args()

@app.route('/stats/editConfig/v1.0')
def get_edit_form():
    return render_template('updateStatList.html')

@app.route('/stats/api/v1.0/file', methods=['GET'])
def process_files():
    result = []
    try:
        dataFolder = request.args.get('dataFolder', default=args.dataFolder, type=str)
        logLevel = request.args.get('logLevel', default=args.logLevel, type=int)
        summaryStatList = request.args.get('summaryStatList', default=args.summaryStatList, type=str)
        result = sl.statisticsFromFiles(dataFolder, summaryStatList, args.saveFolder, logLevel)
        return jsonify(result)
    
    except Exception:
        return json.dumps(result, indent=2, default=int)
    
@app.route('/stats/api/v1.0/url', methods=['GET'])
def process_url():
    url = request.args.get('url', default=args.url)
    dataFolder = request.args.get('dataFolder', default='', type=str)
    logLevel = request.args.get('logLevel', default=args.logLevel, type=int)
    summaryStatList = request.args.get('summaryStatList', default=args.summaryStatList, type=str)
    if len(dataFolder) > 0:
        url += '&dataFolder=' + dataFolder
    result = sl.statisticsFromUrl(url, summaryStatList, args.saveFolder, args.maxInterval, logLevel)
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

@app.route('/stats/api/v1.0/statlist', methods=['GET','POST'])
def update_stat_list():
    logLevel = request.args.get('logLevel', default=args.logLevel, type=int)
    summaryStatListUrl = request.args.get('summaryStatListUrl', default=args.summaryStatList, type=str)
    if request.method == 'POST':
        summaryStatList = request.args.get('summaryStatList', type=str)
        sl.saveStatList(summaryStatListUrl, summaryStatList, logLevel)
    return (sl.getStatList(summaryStatListUrl, logLevel))

@app.route('/stats/api/v1.0/getData', methods=['GET'])
def get_data():
    result = sl.getTableData()
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
 