from fastapi import FastAPI, Request
import pandas as pd
import pulp
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

  # Split Roster Position column for players with multiple positions
  # df['Roster Position'] = df['Roster Position'].str.split('/')
  # outfield = df[df['Roster Position'] == '1B']
  split = df['Roster Position'].str.split('/', expand=True)

  df['Position 1'] = split[0]
  df['Position 2'] = split[1]

  # pitcher = df[(df['Position 1'] == 'P') | (df['Position 2'] == 'P')]
  # catcher = df[(df['Position 1'] == 'C') | (df['Position 2'] == 'C')]
  # first = df[(df['Position 1'] == '1B') | (df['Position 2'] == '1B')]
  # second = df[(df['Position 1'] == '2B') | (df['Position 2'] == '2B')]
  # third = df[(df['Position 1'] == '3B') | (df['Position 2'] == '3B')]
  # short = df[(df['Position 1'] == 'SS') | (df['Position 2'] == 'SS')]
  # outfield = df[(df['Position 1'] == 'OF') | (df['Position 2'] == 'OF')]


  # lists
  players = list(df['Name'])
  salaries = list(df['Salary'])
  position_1 = list(df['Position 1'])
  position_2 = list(df['Position 2'])
  points = list(df['AvgPointsPerGame'])

  # dictionaries to associate values with players
  player_salaries = dict(zip(players, salaries))
  player_position_1 = dict(zip(players, position_1))
  player_position_2 = dict(zip(players, position_2))
  player_points = dict(zip(players, points))

  prob = pulp.LpProblem('Draftkings', pulp.LpMaximize)
  SALARY_CAP = 50000

  pd.set_option('display.max_columns', None)
  # pd.set_option('display.max_rows', None)
  print(df)
  # print("Python data:  ", data)
  return df.to_dict(orient='records')

# # Server
# @app.get('/')
# def read_root():
#   # print('hello world')
#   return {'Hello': 'World'}