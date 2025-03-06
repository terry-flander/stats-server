import argparse
import statistics_lib as sl
   
def main(args):

    # Primarily for testing although could be used for batch processing of saved snapshots.
    # Use the files in the dataFolder
    if args.inputType == 'file':
        sl.statisticsFromFiles(args.dataFolder, args.summaryStatList, args.saveFolder, args.logLevel)
    else:
        sl.statisticsFromUrl(args.url, args.summaryStatList, args.saveFolder, args.logLevel)
            
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Create Summary Catania Statistics")

    parser.add_argument("--inputType", required=False, default='url')
    # inputType == url (default)
    parser.add_argument("--url", required=False, default="https://api.gtm.ostraa.corp.telstra.com/t/catania.api/statistics-service/drop12/v1/statistics-service/stats")

    # inputType == file
    parser.add_argument("--dataFolder", required=False, default="./data/test-data")

    # common arguments
    parser.add_argument("--saveFolder", required=False, default='./data/summary-data')
    parser.add_argument("--summaryStatList", required=False, default=f"./conf/summary-stat-list.csv")
    parser.add_argument("--logLevel", required=False, default=0, type=int)
    args, unknown = parser.parse__known_args()

    main(args)
