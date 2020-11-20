from google.api_core.datetime_helpers import DatetimeWithNanoseconds
from utils import FirestoreHandler, BigQueryHandler
from datetime import datetime
import sys
import json

date = datetime.today().strftime('%Y-%m-%d')

def main (request):
    config = None

    config = json.loads(open("config_local.json").read()) if "-local" in sys.argv else json.loads(open("config.json").read())

    FH = FirestoreHandler()
    docs = FH.get_documents(
        collection='sensors_data'
    )

    doc_ids_separated_by_date = {}
    data_separated_by_date = {}
    schema = []
    
    table_date = None
    
    for doc in docs:
        
        doc_dict = doc.to_dict()
        
        # extracts date in format YYYY-MM-DD
        if isinstance(doc_dict["date"], DatetimeWithNanoseconds):
            table_date = str(doc_dict["date"].year) +"-"+ str(doc_dict["date"].month) +"-"+ str(doc_dict["date"].day) 
        else: 
            table_date = doc_dict["date"]

        # create a date on the data list
        if table_date not in data_separated_by_date:
            data_separated_by_date[table_date] = []
            doc_ids_separated_by_date[table_date] = []

        doc_ids_separated_by_date[table_date].append(doc.id)

        # inserts in the Big Query Schema order
        data_separated_by_date[table_date].append({
            "date": table_date,
            "timestamp_ms": doc_dict["timestamp_ms"],
            "collector_node_id": doc_dict["collector_node_id"],
            "central_node_id": doc_dict["central_node_id"],
            "water_level": doc_dict["water_level"],
            "lat_long": doc_dict["lat_long"],
            "location_id": doc_dict["location_id"]
        })

    # Checks if it's empty
    if not bool(data_separated_by_date):
        print("No data to upload into bq")
        return
    
    # Starts BQ Handler, insert data and checks if data is upload successfuly
    BQ = BigQueryHandler(config)
    for date in data_separated_by_date:
        success = BQ.insert_data(data=data_separated_by_date[date], table_type="sensors_data_fs",table_date=date)

        if success == True:
            # Update fs_state to sent to bq for all docs
            FH.delete_documents(collection='sensors_data', doc_ids=doc_ids_separated_by_date[date])
            print(f"Done. Data from date {date} was sent to Big Query")
        else:
            print(f"Failed. Data from date {date} wasn't sent to Big Query")
    
    
if "-local" in sys.argv:
    main(None)