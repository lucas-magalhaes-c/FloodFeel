from google.api_core.datetime_helpers import DatetimeWithNanoseconds
from utils import FirestoreHandler, data_generator
from datetime import datetime, timedelta
import sys
import json

# date = datetime.today().strftime('%Y-%m-%d')

start_time = datetime.strptime('20/11/20 18:35:00', '%d/%m/%y %H:%M:%S') - timedelta(hours=3) #BRT=GMT-3
end_time = datetime.strptime('20/11/20 18:36:00', '%d/%m/%y %H:%M:%S') - timedelta(hours=3) #BRT=GMT-3

def main (request):
    config = None

    config = json.loads(open("config_local.json").read()) if "-local" in sys.argv else json.loads(open("config.json").read())
    
    if "-local" in sys.argv:
        print(start_time," | ", end_time)

        data_to_upload = data_generator(
            start_time=start_time, 
            end_time=end_time, 
            nodes=[
                {"collector_node_id": "5A:EA:E6:3F:3B:99", "central_node_id": "34:0A:C4:59:1A:77", "lat_long": "-23.545889,-46.733944", "location_id": "TIETE 2 - PTE. JG"},
                {"collector_node_id": "8A:0A:D5:5E:3A:28", "central_node_id": "34:0A:C4:59:1A:77", "lat_long": "-23.5583716,-46.7113053", "location_id": "TIETE 1 -  PTE. CD UN"}
            ]
        )
        print(f"Uploading {len(data_to_upload)} documents...")
    else:
        #TODO: pubsub
        print("Not implemented yet")
        return

    FH = FirestoreHandler()
    try:
        for data in data_to_upload:
            FH.add_document_to_collection(
                collection='sensors_data',
                data=data,
                data_type="sensor"
            )
        print(f"Documents uploaded. Total: {len(data_to_upload)}")
    except:
        print(f"Failed to upload {len(data_to_upload)} documents")

    
    
if "-local" in sys.argv:
    main(None)