
import os
import sys
import json

from datetime import datetime
from google.cloud import bigquery
import google.auth

# https://cloud.google.com/bigquery/docs/loading-data-local

class BigQueryHandler():
    def __init__(self, config):
        self.bq_project = config["bq_project"]
        self.dataset_id =  self.bq_project["dataset_id"]
        self.table_id_patterns = self.bq_project["table_id_patterns"]

        service_account_path = 'service_account_local.json' if "-local" in sys.argv else 'service_account.json'
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_path

        # open and load service account & project id
        sa_file = open(service_account_path)
        sa_json = json.loads(sa_file.read())
        self.project_id = sa_json['project_id']

        # Both APIs must be enabled for your project before running this code.
        # credentials, project = google.auth.default(
        #         scopes=[
        #             "https://www.googleapis.com/auth/bigquery",
        #         ]
        # )

        # Create a client
        self.client = bigquery.Client.from_service_account_json(service_account_path)
        # self.client = bigquery.Client(credentials=credentials, project=project_id)
    
    def insert_data(self, data, table_type, table_date):

        dateYYYYMMDD = table_date.replace("-","")

        # Table id in the format TABLE_YYYYMMDD
        self.table_id = self.table_id_patterns[table_type] + dateYYYYMMDD

        table_full_path = self.project_id+"."+self.dataset_id+"."+self.table_id

        # Check if table already exists
        try:
            table_exists = self.client.get_table(table_full_path)
        except:
            # Table doesnt exist, lets create it

            schema = self._getSchema(table_type)

            new_table = bigquery.Table(table_full_path, schema=schema)
            new_table = self.client.create_table(new_table)  # Make an API request.
        
        if type(data) is not list: 
            data_aux = data
            data = []
            data.append(data_aux)

        try:
            status = self.client.insert_rows_json(table=table_full_path, json_rows=data) # Make an API request.
            if len(status) == 0:
                return True
            else:
                try:
                    print("One or more errors happened")
                    for item in status:
                        errors = item["errors"]
                        for error in errors:
                            print(f'Reason: {error["reason"]}, issue: {error["message"]}')
                except:
                    print("Failed in showing all the errors")
                return False

        except Exception as e:
            print("Failed to insert data into BigQuery\n",e)
            return False
    
    def _getSchema(self,table_type):
        if table_type == "sensors_data_fs":
            return [
                bigquery.SchemaField("date", "DATE", mode="REQUIRED"),
                bigquery.SchemaField("timestamp_ms", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("collector_node_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("central_node_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("water_level", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("lat_long", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("location_id", "STRING", mode="REQUIRED")
            ]
        else:
            print("Schema not found for the table type")
            None
    



import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

class FirestoreHandler():
    def __init__(self):
        service_account_path = 'service_account_local.json' if "-local" in sys.argv else 'service_account.json'

        # firestore document state (fs_state)
        self.fs_state = {
            1: "Waiting to send to BQ",
            2: "Sent to BQ",
        }

        # open and load service account & project id
        sa_file = open(service_account_path)
        sa_json = json.loads(sa_file.read())
        project_id = sa_json['project_id']

        if "-local" not in sys.argv:
            # Use the application default credentials, in GCP
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {
            'projectId': project_id,
            })

            self.db = firestore.client()
        else:
            # Testing locally
            # Use a service account
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)

            self.db = firestore.client()
    
    def add_document_to_collection(self,collection,data,data_type):

        doc_ref = self.db.collection(collection).document(data["collector_node_id"]+":"+ data["timestamp_ms"])

        try:
            if data_type == "sensor":
                doc_ref.set({
                    'date': data["date"],
                    'timestamp_ms': data["timestamp_ms"],
                    'collector_node_id': data["collector_node_id"],
                    'central_node_id': data["central_node_id"],
                    'water_level': data["water_level"],
                    'lat_long': data["lat_long"],
                    'location_id': data["location_id"],
                    'fs_state': 1
                },merge=True)
            else:
                print(f"data_type not recognized {data_type}")
        except:
            print("Missing field for the document. Data:",data)
    
    def get_documents(self,collection):
        
        # Create a reference to the sensors data
        sensors_data_ref = self.db.collection(collection)

        try:
            sensors_data_ref = sensors_data_ref.where(u'fs_state', u'==', 1)
            
        except Exception as e:
            print("Failed on getting documents\n",e)
            return None

        docs = sensors_data_ref.stream()

        # for doc in docs:
        #     print(f'{doc.id} => {doc.to_dict()}')
        
        return docs
    
    def set_sent_to_bq_fs_state(self, collection, doc_ids):

        for doc_id in doc_ids:
            doc_ref = self.db.collection(collection).document(doc_id)

            doc_ref.set({
                'fs_state': 2
            },merge=True)
    
    def delete_documents(self, collection, doc_ids):

        for doc_id in doc_ids:
            doc_ref = self.db.collection(collection).document(doc_id)

            doc_ref.delete()
        
