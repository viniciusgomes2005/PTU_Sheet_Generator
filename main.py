# main.py
from fastapi import FastAPI

# Create a FastAPI "instance"
app = FastAPI()

# Define a path operation decorator for the root URL ("/") and a GET operation
@app.get("/")
def read_root():
    return {"message": "Hello World"}