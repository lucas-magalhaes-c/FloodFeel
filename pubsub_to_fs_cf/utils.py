
import os
import sys
import json

from datetime import datetime, timedelta
import google.auth
import numpy as np

def data_generator(start_time, end_time, nodes, delta_ms=300000):
    # 300000 ms is 5 minutes
    data_generated = []

    if not isinstance(start_time,datetime) or not isinstance(end_time,datetime):
        print("Start time and end_time must be instance of datetime")
        return []

    if end_time < start_time:
        print("End time must be less than start time")
        return []

    date = start_time
    end_timestamp_ms = end_time.timestamp() * 1000
    water_level_base = 0

    # start water level of each node
    water_level = {}
    for i in range(len(nodes)):
        water_level[i]=0

    timestamp_ms = start_time.timestamp() * 1000
    date = start_time

    while timestamp_ms <= end_timestamp_ms:
        water_level_base = water_level_base + (np.random.randint(-3, 4) if water_level_base <= 55 else np.random.randint(-4, 0))
        water_level_base = water_level_base if water_level_base > -25 else water_level_base + np.random.randint(1, 6)

        for index in water_level:
            water_level[index] = water_level_base + np.random.randint(-2, 3)

            # get the node of related index
            node = nodes[index]

            data = {}

            data["date"] = date.strftime('%Y-%m-%d')
            data["timestamp_ms"] = timestamp_ms
            data["collector_node_id"] = node["collector_node_id"]
            data["central_node_id"] = node["central_node_id"]
            data["water_level"] = water_level[index]
            data["lat_long"] = node["lat_long"]
            data["location_id"] = node["location_id"]

            data_generated.append(data)

        water_level_base = water_level[0]
        timestamp_ms = timestamp_ms + delta_ms 
        date = date + timedelta(minutes=5)

    return data_generated


import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

class FirestoreHandler():
    def __init__(self):
        service_account_path = 'service_account_local.json' if "-local" in sys.argv or "-sim" in sys.argv  else 'service_account.json'

        # firestore document state (fs_state)
        self.fs_state = {
            1: "Waiting to send to BQ",
            2: "Sent to BQ",
        }

        # open and load service account & project id
        sa_file = open(service_account_path)
        sa_json = json.loads(sa_file.read())
        project_id = sa_json['project_id']

        if "-local" in sys.argv or "-sim" in sys.argv:
            # Testing locally
            # Use a service account
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)

        else:
            # Use the application default credentials, in GCP
            if (not len(firebase_admin._apps)):
                cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(
                    cred, 
                    {'projectId': project_id}
                )

        self.db = firestore.client()
    
    def add_document_to_collection(self,collection,data,data_type):

        doc_ref = self.db.collection(collection).document(data["collector_node_id"]+":"+ str(int(data["timestamp_ms"])))

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
        
