# Catania Statistics Pre-processing

The Catania statistics API returns very low-level counters for each of many internal processes. These in themselves only represent a snap-shot at a point of time for these processes. In order to be useful for monitoring application behaviour, these counters need to be converted to delta change values between consecutive snap-shots. 

These delta values can be summarised to provide higher level delta values based on the Statistic type using a unique concatination of statistic attributes.

## OVERVIEW

Python scripts to compare two Catania Statistics JSON files, calculate the difference between the newer and older and then create summary statistics using a CSV file 
containg a list of statistics name regular expressions to total these differences for selected rows.

In the case where the new value is less than the old value, the new value is taken to be the difference. This can occur when any of the counters is reset to 0. This may happend due 
to a restart of the system (all restart at 0)

## PREREQUISITES

Before you can run or compile the script, you need to have the following installed:

- Python 3.6 or higher
- Required Python packages: requests, pandas, pyinstaller

You can install the required Python packages using pip:
```
pip install requests pandas pyinstaller
```

## COMPILIATION

To compile the scripts into standalone executables, run the following commands in your terminal or command prompt:

For catania_stats.py:
```
pyinstaller --onefile catania_stats.py
```

For server.py:
```
pyinstaller --onefile server.py
```
After running these commands, you will find the compiled executables in the dist directory.

## USAGE

Using the **server**.py Executable

The server.py script provides a local webservice using Python Flask. By default it runs on *http://127.0.0.1:5000* and provides access to the *statistics_lib* which an use either a URL or a directory of local files as input to generate summary statistics.

In addition, there is an API which allows any saved local file to be fetched. This is used to test the URL api while the FILE api works with local-files only.

At startup, the following Command Line Arguments are available. Some can be overriden as API Parameters.

--``url``: if inputType == url then the source of JSON Catania Statistics (default=``production catania``)

--``dataFolder``: if inputType == file then a directory containing two or more captured Statistics JSON files. File names are not relevant however files are processed alphabetically, so newest file should always be last. (default=``test_data``)

--``saveFolder``: target for all saved output (default=``summary_data``)
  - urlData - each JSON fetched from URL is saved with file name generated from the time/date
  - change - each two compared JSON files produce a single change file with the name of the 2nd file
  - stats - each two compared JSON files produce a single summary statistics file with the name of the 2nd file

--``summaryStatList``: CSV file contining summary statistic name and regular expression pairs (default=``summary_stat_list.csv``)

-- ``maxInterval``: the maximum number of minutes between Statistics API requests to produce summaries. If the API requests are move than this delta, the resulting change will appear as an aboration and because the detailed statistcis are at such a low level, there is a good chance that many values will not have a previous match. To prevent this, set the value to no more than twice the normal request interval for the consuming service. (default=``10``)

--``logLevel``: set level of logging. (default=``0``)
  - 0 - Log errors only
  - 1 - Log errors and one messsage per requestt
  - 2 - Log errors and all messages

API:

GET /stats/api/v1.0/file
 - dataFolder - alternative dataFolder to use for processing. Defaults to ./data-folder
 - logLevel - set logging level: 0 = none, 1 = minimum > 1 all

GET /stats/api/v1.0/url
 - url - fully qualified URL souce for Catania Statistics API
 - dataFolder - alternative dataFolder to use for processing. Defaults to ./data-folder
 - logLevel - set logging level: 0 = none, 1 = minimum > 1 all

GET /stats/api/v1.0/test
 - offset - offset to entries in the data file list in dataFolder - 0 to total number of files - 1.
 - dataFolder - alternative dataFolder to use for processing. Defaults to ./data-folder
 - logLevel - set logging level: 0 = none, 1 = minimum > 1 all



Using the **catania_stats**.py Executable

The catania_stats.py script uses either a URL or a directory of local files as input to generate summary statistics.

Command Line Arguments:

--``inputType``: type of processing: url or file. Depending on selection, different arguments are required (default=``url``)

--``url``: if inputType == url then the source of JSON Catania Statistics (default=``production catania``)

--``dataFolder``: if inputType == file then a directory containing two or more captured Statistics JSON files. File names are not relevant however files are processed alphabetically, so newest file should always be last. (default=``test_data``)

--``saveFolder``: target for all saved output (default=``summary_data``)
  - urlData - each JSON fetched from URL is saved with file name generated from the time/date
  - change - each two compared JSON files produce a single change file with the name of the 2nd file
  - stats - each two compared JSON files produce a single summary statistics file with the name of the 2nd file

--``summaryStatList``: CSV file contining summary statistic name and regular expression pairs (default=``summary_stat_list.csv``)

--``logLevel``: set level of logging. (default=``0``)
  - 0 - Log errors only
  - 1 - Log errors and one messsage per requestt
  - 2 - Log errors and all messages

## EXAMPLES

```
catania_stats.exe --inputType url --url http://localhost:8010/static/stats20241210_1113.json
```

```
catania_stats.exe --inputType file
```