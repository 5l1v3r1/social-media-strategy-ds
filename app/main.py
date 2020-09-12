from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from routers.optimize_time import data_wrangling

from pydantic import BaseModel

import requests 
import os
from dotenv import load_dotenv

load_dotenv()
BACKEND_AUTHORIZATION = os.getenv("BACKEND_AUTHORIZATION")

app = FastAPI()

class timeRequest(BaseModel):
    id: int
    screenname: str
    class Config:
        schem_example = {
            'id': 1,
            'screenname': 'elonmusk'
        }

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post('/recommend')
async def recommendation(user_input: timeRequest):
    print('helloooo')
    request_dict = user_input.dict()

    twitter_handle = request_dict['screenname']
    _id = request_dict['id']

    backend_url = 'https://api.so-me.net/api/posts/' + str(_id)
    header_data = {'Authorization' : BACKEND_AUTHORIZATION}

    dw = data_wrangling(twitter_handle, 5)
    followers_ids = dw.followers_ids()
    get_follower_data = dw.get_follower_data(followers_ids)
    optimal_time = dw.optimal_time(get_follower_data)

    baseline_time = {"optimal_time": optimal_time}

    r = requests.put(backend_url, headers = header_data, json=baseline_time)
    
    return JSONResponse(content=baseline_time)