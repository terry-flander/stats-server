# server.py

from flask import Flask, jsonify, request, render_template
import argparse
import json

import os
from os import listdir
from os.path import isfile, join
import csv
import requests
import pandas as pd
import traceback
import subprocess

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
        result = statisticsFromFiles(dataFolder, summaryStatList, args.saveFolder, logLevel)
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
    result = statisticsFromUrl(url, summaryStatList, args.saveFolder, args.maxInterval, logLevel)
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
    return jsonify(getTestStatistics(dataFolder, offset, logLevel))

@app.route('/stats/api/v1.0/statlist', methods=['GET','POST'])
def update_stat_list():
    logLevel = request.args.get('logLevel', default=args.logLevel, type=int)
    summaryStatListUrl = request.args.get('summaryStatListUrl', default=args.summaryStatList, type=str)
    if request.method == 'POST':
        summaryStatList = request.args.get('summaryStatList', type=str)
        saveStatList(summaryStatListUrl, summaryStatList, logLevel)
    return (getStatList(summaryStatListUrl, logLevel))

def prepareDataFrame(df, logLevel):
   
    result = df

    try:
        # converting json dataset from dictionary to dataframe
        result['timestamp'] = pd.to_datetime(result['timestamp'])
        result['newIndex'] = result['serviceName'] + result['statisticName'] + result['podReference']
        result = result.set_index(result['newIndex'])

    except Exception:
        print(traceback.format_exc())

    return result

def calculateChange(time_1, time_2, lastTimestamp, saveFolder, save_file, logLevel):

    result = []
    try:
        result = time_2.copy()
        change_raw = time_2.copy()

        # Simple subtraction. Could product negative differences
        value_change = time_2['value'] - time_1['value'].where(time_1['statisticsType'] == 'Counter')
        time_change =  time_2['timestamp'] - time_1['timestamp']

        # Convert any case where time_1.value > time_2.value to time_2.value or if statistic of type 'Gauge'
        result['value'] = value_change.where(value_change >= 0, time_2['value'])
        change_raw['value'] = value_change
        change_raw['timeDelta'] = time_change.astype(str)

        new_index = change_raw.query("timeDelta == 'NaT'")
        reset_index = change_raw.query("value < 0")

        if logLevel > 0:
            print(f'Checking {len(result.index)} changes since {str(lastTimestamp)}')
        
        os.makedirs(os.path.join(os.getcwd(), saveFolder + '/change/'), exist_ok=True)
        save_change = f'{os.getcwd()}/{saveFolder}/change/{save_file}'
        
        if result is not None and logLevel > 2:
            result.to_json(save_change, orient="records")
            print(f"Change saved to {save_change}")

            os.makedirs(os.path.join(os.getcwd(), saveFolder + '/raw/'), exist_ok=True)
            save_raw = f'{os.getcwd()}/{saveFolder}/raw/{save_file.replace(".json",".csv")}'
            change_raw.to_csv(save_raw, index=False)

    except Exception:
        print(traceback.format_exc())

    return result, new_index, reset_index

def createSummaryStatistics(summary_list, timestamp, c, saveFolder, save_file, logLevel):

    result = []
    change = c[0]
    new_index = c[1]
    reset_index = c[2]

    try:

        date_type = str(timestamp)
        for st in summary_list:
            if st[0] != "AUTO":
                stat = change[change['newIndex'].str.contains(st[1])]
                count = len(change[change['newIndex'].str.contains(st[1])])
                value = stat["value"].astype(int).sum()
                if count > 0:
                    result += [{ "statisticName": st[0], "value": value, "count": count, "date_time": date_type }]

        # ADD NEW COUNT OF INDEX CHANGES
        result += [{ "statisticName": "NEW_INDEX_COUNT", "value": new_index.shape[0], "count": 0, "date_time": date_type }]
        result += [{ "statisticName": "RESET_INDEX_COUNT", "value": reset_index.shape[0], "count": 0, "date_time": date_type }]


        if len(result) > 0:
            os.makedirs(os.path.join(os.getcwd(), saveFolder + '/stats/json/'), exist_ok=True)
            save_stats = f'{os.getcwd()}/{saveFolder}/stats/json/{save_file}'
            with open(save_stats,"w+") as f:
                f.write(json.dumps(result, default=str))
            if logLevel > 1:
                print(f"Summary statistics saved to {save_stats}")

            if logLevel > 2:
                os.makedirs(os.path.join(os.getcwd(), saveFolder + '/stats/csv/'), exist_ok=True)
                save_file = save_file.replace('.json','.csv')
                save_stats = f'{os.getcwd()}/{saveFolder}/stats/csv/{save_file}'
                df = pd.DataFrame(result)
                df.to_csv(save_stats, index=False)
                print(f"Summary statistics saved to {save_stats}")
        
    except Exception:
        print(traceback.format_exc())

    return result

def statisticsFromFiles(dataFolder, summaryStatList, saveFolder, logLevel):

    result = []
    try:

        items = os.listdir(dataFolder)
        rawStatsFiles = sorted(items)
        for count in range(0, len(rawStatsFiles) - 1):
            with open(os.path.join(dataFolder, rawStatsFiles[count])) as train_file:
                dict_train = json.load(train_file)
            time_1 = prepareDataFrame(pd.DataFrame.from_dict(dict_train), logLevel)
            lastTimestamp = time_1['timestamp'].max()
            summary_list = getStatisticList(summaryStatList, time_1)


            with open(os.path.join(dataFolder, rawStatsFiles[count + 1])) as train_file:
                dict_train = json.load(train_file)
            time_2 = prepareDataFrame(pd.DataFrame.from_dict(dict_train), logLevel)
            thisTimestamp = time_2['timestamp'].max()
            
            save_file = rawStatsFiles[count + 1]
            change = calculateChange(time_1, time_2, lastTimestamp, saveFolder, save_file, logLevel)

            py_date = thisTimestamp.to_pydatetime()
            timestamp = py_date.strftime("%Y-%m-%dT%H:%M:%S")
            data = createSummaryStatistics(summary_list, timestamp, change, saveFolder, save_file, logLevel)
            result += data

        if logLevel > 2:
            os.makedirs(os.path.join(os.getcwd(), saveFolder + '/stats/csv/'), exist_ok=True)
            save_file = save_file.replace('.json','-all.csv')
            save_stats = f'{os.getcwd()}/{saveFolder}/stats/csv/{save_file}'
            df = pd.DataFrame(result)
            df.to_csv(save_stats, index=False)
            print(f"Summary statistics saved to {save_stats}")


    except Exception:
        print(traceback.format_exc())

    return result

def getTestStatistics(dataFolder, offset, logLevel):

    result = []
    try:
        items = os.listdir(dataFolder)
        rawStatsFiles = sorted(items)
        if offset < 0 or offset >= len(items):
            print(f'Offset out of range: 0 to {len(items) - 1}')
        else:
            load_file = os.path.join(dataFolder, rawStatsFiles[offset])
            if logLevel > 1:
                print(f'Load from: {load_file}')
            with open(load_file) as json_file:
                result = json.load(json_file)
    except Exception:
        print(traceback.format_exc())

    return result
    
def getStatList(summaryStatList, logLevel):

    result = ''
    try:
        with open(summaryStatList, 'r') as file:
            result = file.read()
        if logLevel > 1:
            print (f'Loaded summaryStatList from {summaryStatList}')
        if logLevel > 2:
            print (result)
            
    except Exception:
        print(traceback.format_exc())

    return result

def saveStatList(summaryStatListUrl, summaryStatList, logLevel):

    try:
        with open(summaryStatListUrl, 'w') as file:
            file.write(summaryStatList)
        if logLevel > 1:
            print (f'Saved summaryStatList to {summaryStatListUrl}')
            
    except Exception:
        print(traceback.format_exc())

    return summaryStatList

def statisticsFromUrl(url, summaryStatList, saveFolder, maxInterval, logLevel):

    result = []
    try:
        response = getStatisticsAPI(url)

        time_2 = prepareDataFrame(pd.json_normalize(response), logLevel)
        thisTimestamp = time_2['timestamp'].max()
        summary_list = getStatisticList(summaryStatList, time_2)

        # Save URL Contents for next time
        os.makedirs(os.path.join(os.getcwd(), saveFolder + '/urlData/'), exist_ok=True)
        save_file_name = f'stats{thisTimestamp.strftime("%Y%m%d_%H%M%S")}.json'
        save_dir = f'{os.getcwd()}/{saveFolder}/urlData/'
        save_file = f'{save_dir}/{save_file_name}'

        # time_2.to_json(save_file, orient="records")
        with open(save_file, "w") as f:
            json.dump(response, f)
        items = [f for f in os.listdir(save_dir) if os.path.isfile(os.path.join(save_dir, f)) ]

        if len(items) > 1:
            rawStatsFiles = sorted(items)

            # Get last saved data
            with open(os.path.join(save_dir, rawStatsFiles[-2])) as train_file:
                dict_train = json.load(train_file)

            time_1 = prepareDataFrame(pd.DataFrame.from_dict(dict_train), logLevel)

            # if this request is older than set maximum interval, do not calculate change
            diff = time_2['timestamp'].max() - time_1['timestamp'].max()
            interval = int(diff.total_seconds() / 60)

            if interval <= maxInterval:
                lastTimestamp = time_1['timestamp'].max()
                change = calculateChange(time_1, time_2, lastTimestamp, saveFolder, save_file_name, logLevel)
                data = createSummaryStatistics(summary_list, thisTimestamp, change, saveFolder, save_file_name, logLevel)
                result += data
            elif logLevel > 0:
                print(f'Last statistics {interval} minutes ago. No statistics generated. (maxInterval={maxInterval})')

            # Only keep most recently received statistics JSON
            for count in range(0, len(rawStatsFiles) - 1):
                os.remove(os.path.join(save_dir + rawStatsFiles[count]),)


    except Exception:
        print(traceback.format_exc())

    return result

def getStatisticsAPI(url):
    
    result = []

    try:
        if not url.startswith('http'):
            proc = subprocess.Popen([url], stdout=subprocess.PIPE, shell=True, text=False)
            (out, err) = proc.communicate()
            with open('temp.json') as train_file:
                result = json.load(train_file)
        else:
            result = requests.get(url, verify=False).json()
    except Exception:
        print(traceback.format_exc())

    return result

def getStatisticList(summaryStatList, pd):
    with open(summaryStatList, newline='') as f:
        reader = csv.reader(f)
        summary_list = list(reader)
    auto = [word for word in summary_list if word[0] == "AUTO"]
    result =  [word for word in summary_list if not word[0] == "AUTO"]

    for a in auto:
        result += getUniqueValues(pd, a[1], a[2], a[3])

    return result
    
def getUniqueValues(pd, index, prefix, matching):

    u = pd[index].unique()
    result = []
    for e in u:
        if matching is None or matching in e:
            if prefix is None or prefix == "":
                result += [[e, e]]
            else:
                pre = prefix.split(";")
                for p in pre:
                    result += [[p + ":" + e, p + ".*?" + e]]
    return result

if __name__ == '__main__':
    app.run(debug=True)
 