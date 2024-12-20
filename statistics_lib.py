import os
from os import listdir
from os.path import isfile, join
import csv
import json
import requests
import pandas as pd
import traceback

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
        value_change = time_2['value'] - time_1['value']

        # Convert any case where time_1.value > time_2.value to time_2.value
        result['value'] = value_change.where(value_change >= 0, time_2['value'])
        change_raw['value'] = value_change

        if logLevel > 0:
            print(f'Checking {len(result.index)} changes since {str(lastTimestamp)}')
        
        os.makedirs(os.path.join(os.getcwd(), saveFolder + '/change/'), exist_ok=True)
        save_change = f'{os.getcwd()}/{saveFolder}/change/{save_file}'
        
        if result is not None:
            result.to_json(save_change, orient="records")
            if logLevel > 1:
                print(f"Change saved to {save_change}")

        if logLevel > 2:
            os.makedirs(os.path.join(os.getcwd(), saveFolder + '/raw/'), exist_ok=True)
            save_raw = f'{os.getcwd()}/{saveFolder}/raw/{save_file}'
            change_raw.to_json(save_raw, orient="records")

    except Exception:
        print(traceback.format_exc())

    return result

def createSummaryStatistics(summaryStatList, timestamp, change, saveFolder, save_file, logLevel):

    result = []
    try:
        with open(summaryStatList, newline='') as f:
            reader = csv.reader(f)
            summary_list = list(reader)

        date_type = str(timestamp)
        for st in summary_list:
            stat = change[change['newIndex'].str.contains(st[1])]
            count = len(change[change['newIndex'].str.contains(st[1])])
            result += [{ "statisticName": st[0], "value": stat["value"].sum(), "count": count, "date_time": date_type }]

        if len(result) > 0:
            os.makedirs(os.path.join(os.getcwd(), saveFolder + '/stats/'), exist_ok=True)
            save_stats = f'{os.getcwd()}/{saveFolder}/stats/{save_file}'
            with open(save_stats,"w+") as f:
                f.write(json.dumps(result, default=str))
            if logLevel > 1:
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

            with open(os.path.join(dataFolder, rawStatsFiles[count + 1])) as train_file:
                dict_train = json.load(train_file)
            time_2 = prepareDataFrame(pd.DataFrame.from_dict(dict_train), logLevel)
            thisTimestamp = time_2['timestamp'].max()
            
            save_file = rawStatsFiles[count + 1]
            change = calculateChange(time_1, time_2, lastTimestamp, saveFolder, save_file, logLevel)

            py_date = thisTimestamp.to_pydatetime()
            timestamp = py_date.strftime("%Y-%m-%dT%H:%M:%S")
            data = createSummaryStatistics(summaryStatList, timestamp, change, saveFolder, save_file, logLevel)
            result += data
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
    
def statisticsFromUrl(url, summaryStatList, saveFolder, maxInterval, logLevel):

    result = []
    try:
        response = requests.get(url).json()
        time_2 = prepareDataFrame(pd.json_normalize(response), logLevel)
        thisTimestamp = time_2['timestamp'].max()
        
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
                data = createSummaryStatistics(summaryStatList, thisTimestamp, change, saveFolder, save_file_name, logLevel)
                result += data
            elif logLevel > 0:
                print(f'Last statistics {interval} minutes ago. No statistics generated. (maxInterval={maxInterval})')

            # Only keep most recently received statistics JSON
            for count in range(0, len(rawStatsFiles) - 1):
                os.remove(os.path.join(save_dir + rawStatsFiles[count]),)


    except Exception:
        print(traceback.format_exc())

    return result
