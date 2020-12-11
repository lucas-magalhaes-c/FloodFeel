from google.api_core.datetime_helpers import DatetimeWithNanoseconds
from utils import FirestoreHandler, data_generator
from datetime import datetime, timedelta
import sys
import json

# start_time = datetime.strptime('20/11/20 18:35:00', '%d/%m/%y %H:%M:%s') - timedelta(hours=3) #BRT=GMT-3
# end_time = datetime.strptime('20/11/20 18:36:00', '%d/%m/%y %H:%M:%S') - timedelta(hours=3) #BRT=GMT-3

def main (request):
    config = None

    config = json.loads(open("config_local.json").read()) if "-local" in sys.argv or "-sim" in sys.argv else json.loads(open("config.json").read())
    
    request_json = None
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
        # expected fields - example: {"collector_node_id": "5A:EA:E6:3F:3B:99", "central_node_id": "34:0A:C4:59:1A:77", "water_level": 20}
        if "-sim" in sys.argv:
            # data simulation
            data_to_upload = {"collector_node_id": "5A:EA:E6:3F:3B:99", "central_node_id": "34:0A:C4:59:1A:77", "water_level": 20}
        else:
            data_to_upload = request.get_json()

        now =  datetime.now()
        date = datetime.now().strftime('%Y-%m-%d')
        timestamp_ms = round((now - timedelta(hours=3)).timestamp() * 1000)

        data_to_upload["date"] = date
        data_to_upload["timestamp_ms"] = timestamp_ms

        if data_to_upload["collector_node_id"] in config["collector_nodes"]:
            data_to_upload["lat_long"] = config["collector_nodes"][data_to_upload["collector_node_id"]]["lat_long"]
            data_to_upload["location_id"] = config["collector_nodes"][data_to_upload["collector_node_id"]]["location_id"]
        else:
            print("Collector id missing in config. Using default for missing values")
            data_to_upload["lat_long"] = "0,0"
            data_to_upload["location_id"] = "Ausente"
        
        print("Uploading data:", data_to_upload)

    FH = FirestoreHandler()
    try:
        if type(data_to_upload) is list:
            for data in data_to_upload:
                FH.add_document_to_collection(
                    collection='sensors_data',
                    data=data,
                    data_type="sensor"
                )
            print(f"Documents uploaded. Total: {len(data_to_upload)}")
        else:
            FH.add_document_to_collection(
                    collection='sensors_data',
                    data=data_to_upload,
                    data_type="sensor"
            )
            print(f"Document uploaded.")
            return '', 201
    except:
        print(f"Failed to upload {len(data_to_upload)} documents")
        return '', 500
    

    
if "-local" in sys.argv or "-sim" in sys.argv:
    main(None)