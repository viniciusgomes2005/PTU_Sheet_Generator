import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
from os import environ as env

load_dotenv()

cred_path = env["FIREBASE_SERVICE_KEY"]

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def get_edges():
    docs = db.collection("edges").stream()
    return [
        {**doc.to_dict(), "id": doc.id}
        for doc in docs
    ]

def get_features():
    docs = db.collection("features").stream()
    return [
        {**doc.to_dict(), "id": doc.id}
        for doc in docs
    ]

def get_classes():
    docs = db.collection("classes").stream()
    return [
        {**doc.to_dict(), "id": doc.id}
        for doc in docs
    ]
