import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI
from dotenv import load_dotenv
from os import environ as env

load_dotenv()  # carrega o .env

cred_path = env["FIREBASE_SERVICE_KEY"]

if not firebase_admin._apps: 
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}
