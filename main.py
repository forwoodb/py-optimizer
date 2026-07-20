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

  # convert to dataframe
  df = pd.DataFrame(data)

  split = df['Roster Position'].str.split('/', expand=True)

  df['Position 1'] = split[0]
  df['Position 2'] = split[1]

  # pitcher = df[df['Roster Position'] == 'P']

  pd.set_option('display.max_columns', None)
  pd.set_option('display.max_rows', None)
  print(df)
  # print("Python data:  ", data)
  return data

# # Server
# @app.get('/')
# def read_root():
#   # print('hello world')
#   return {'Hello': 'World'}