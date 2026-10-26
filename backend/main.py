# This is the entry point of our backend API.
# Right now it only has one route, just to prove the server works.

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    # A simple health-check style response.
    return {"message": "Notes Organizer is running"}
