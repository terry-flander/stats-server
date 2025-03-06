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
- Required Python packages: requests, pandas, pyinstaller, Flask

You can install the required Python packages using pip:
```
pip install -r requirements.txt
```

## COMPILIATION

To compile the scripts into standalone executables, run the following commands in your terminal or command prompt:

For catania_stats.py:
```
pyinstaller --onefile catania_stats.py
```

For server.py:
```
pyinstaller --onefile server.py -F --add-data "./templates/*:templates" --add-data "./conf/*:./conf" --add-data "./data/test-data/*:./data/test-data"
```

For server_one.py:
```
pyinstaller --onefile server_one.py -F --add-data "./templates/*:templates" --add-data "./conf/*:./conf" --add-data "./data/test-data/*:./data/test-data"
```

Note the inclusion of --add-data to include templates and scripts directory. This provides access to the Update Statistics List HTML page (updateStatList.html) and secure request scripts (catania_stat.*)

After running these commands, you will find the compiled executables in the dist directory.

## USAGE

Using the **server** or **server_one** Executable

There are two versions of this program due to difference in behaviour of the pyinstall between Windows and RHEL. For Linux the relative imports do not work as expected. To remove the issue, there is only the single PY program including all the library routines. Behaviour is the same for either.

The server.py script provides a local webservice using Python Flask. By default it runs on *http://127.0.0.1:5000* and provides access to the *statistics_lib* which an use either a URL or a directory of local files as input to generate summary statistics.

In addition, there is an API which allows any saved local file to be fetched. This is used to test the URL api while the FILE api works with local-files only.

At startup, the following Command Line Arguments are available. Some can be overriden as API Parameters.

--``url``: if inputType == url then the source of JSON Catania Statistics (default=``production catania``). If this URL begins with 'https' then this will execute the script catania_stat.sh. This script is based on the script used by Zabbix to make a token based secure request to the Statistics API. 

--``dataFolder``: if inputType == file then a directory containing two or more captured Statistics JSON files. File names are not relevant however files are processed alphabetically, so newest file should always be last. (default=``test_data``)

--``saveFolder``: target for all saved output (default=``summary_data``)
  - urlData - each JSON fetched from URL is saved with file name generated from the time/date
  - change - each two compared JSON files produce a single change file with the name of the 2nd file
  - stats - each two compared JSON files produce a single summary statistics file with the name of the 2nd file

--``summaryStatList``: CSV file contining summary statistic name and regular expression pairs (default=``summary_stat_list.csv``)

-- ``maxInterval``: the maximum number of minutes between Statistics API requests to produce summaries. If the API requests are move than this delta, the resulting change will appear as an aboration and because the detailed statistcis are at such a low level, there is a good chance that many values will not have a previous match. To prevent this, set the value to no more than twice the normal request interval for the consuming service. (default=``10``)

--``logLevel``: set level of logging. (default=``0``)
  - 0 - Log errors only
  - 1 - Log errors and one messsage per request
  - 2 - Log errors and all messages
  - 3 - Log errors and messages; save calculated change: raw (CSV) and corrected (JSON); save summarised statistics (CSV and JSON)

### Update Summary Statistics List

Using the **server** Executable

Start the server with any of the above parameters (except --url / --file). A Flask endpoint will be enabled at:

--http://127.0.0.1:5000

Use any of the API endpoints to execute the indicated activities. Parameters are available to override the default values described above. Use the **logLevel** argument to control both local logging and temporary file retention. Both the **file** and **url** endpoints return only summary statistics as described by the **summaryStatList** CSV file. For **file** will be all sample times found in input **dataFolder**. For **url** will be only current period change unless the time since last sample greater than **maxInterval**. In that case the first **url** request returns nothing but is saved for the next request.

An HTML page is provided which allows access to the summary-stat-list.csv file for review and editing. This page is located at the standard Flask static endpoint:

-- http://127.0.0.1:5000/static/updateStatList.html

From this page, the current summary statistics list can be loaded, updated, and saved either with the original name (default), or a new name. To test or use a new file, use the ``summaryStatList`` argument with either the File or URL end-points. (see below)

The content of the file is a simple two column csv where the first column is the summary key to be generated, and the 2nd field contains a simple regular expression which is searched for in the generated index of each calculated change row.

## Automatic Statistics

In addition to the summary statistics described above, the application can automatically create new statistics from the contents of the data result.
Each entry in the ``summaryStatList`` which has **AUTO** as its first value will then be expaned by selecting unique Column Names as follows:

 - [0] - "AUTO"
 - [1] - Result data Column Name
 - [2] - Column Value contains this value. Leave blank for all unique Column Names

Used to select Pod totals, Buffered gauge values, and LEMF Sent totals

Examples:

```
AUTO,podReference,
AUTO,statisticName,"BUFFERED"
AUTO,statisticName,"SENT_PER_LEMF"
```

API Documentation is available at:

https://documenter.getpostman.com/view/1639425/2sAYdZtDSg

API:

GET /stats/api/v1.0/file
 - dataFolder - alternative dataFolder to use for processing. Defaults to ./data-folder
 - summaryStatList - CSV file contining summary statistic name and regular expression pairs
 - logLevel - set logging level: 0 = none, 1 = minimum > 1 all

GET /stats/api/v1.0/url
 - url - fully qualified URL souce for Catania Statistics API
 - dataFolder - alternative dataFolder to use for processing. Defaults to ./data-folder
 - summaryStatList - CSV file contining summary statistic name and regular expression pairs
 - logLevel - set logging level: 0 = none, 1 = minimum > 1 all

GET /stats/api/v1.0/test
 - offset - offset to entries in the data file list in dataFolder - 0 to total number of files - 1.
 - dataFolder - alternative dataFolder to use for processing. Defaults to ./data-folder
 - logLevel - set logging level: 0 = none, 1 = minimum > 1 all

GET, POST /stats/api/v1.0/statlist
 - offset - offset to entries in the data file list in dataFolder - 0 to total number of files - 1.
 - dataFolder - alternative dataFolder to use for processing. Defaults to ./data-folder
 - logLevel - set logging level: 0 = none, 1 = minimum > 1 all

### EXAMPLES

Process files in directory **test-data-5**, generate statistics described in **summary-stat-list-2.csv** with full loggin; save all intermediate data:

```http://127.0.0.1:5000/stats/api/v1.0/file?summaryStatList=./conf/summary-stat-list-2.csv&logLevel=3&dataFolder=./data/test-data-5```

Get the most recent changes to summary statics using all defaults:

```http://127.0.0.1:5000/stats/api/v1.0/url```

GET this URL to load Maintenance form. Load and Save buttons get selected CSV and save or save-as based on entered file name:

```http://127.0.0.1:5000/static/updateStatList.html```

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