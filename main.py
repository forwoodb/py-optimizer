from fastapi import FastAPI, Request
import pandas as pd
# from pydantic import BaseModel
# from typing import List

app = FastAPI()
# class Player(BaseModel):
#   Position: str
#   Name: str
#   ID: str
#   Salary: str
#   Game_Info: str
#   # "Game Info": str
#   TeamAbbrev: str
#   AvgPointsPerGame: str

# @app.post('/optimize')
# def optimize(body: List[Player]):
#   return body

@app.post('/optimize')
async def optimize(body: Request):
  data = await body.json()
  
  # print("Python data:  ", data)
  return {'Python': data}

# # Server
# @app.get('/')
# def read_root():
#   # print('hello world')
#   return {'Hello': 'World'}