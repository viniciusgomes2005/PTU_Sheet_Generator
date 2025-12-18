from fastapi import FastAPI
from firestore_service import (
    get_edges,
    get_features,
    get_classes
)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/edges")
def edges():
    return get_edges()

@app.get("/features")
def features():
    return get_features()

@app.get("/classes")
def classes():
    return get_classes()
