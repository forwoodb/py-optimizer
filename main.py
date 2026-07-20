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

  # Convert strings to numeric values
  df['Salary'] = pd.to_numeric(df['Salary'])
  df['AvgPointsPerGame'] = pd.to_numeric(df['AvgPointsPerGame'])

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
  points = list(df['AvgPointsPerGame'])
  salaries = list(df['Salary'])
  position_1 = list(df['Position 1'])
  position_2 = list(df['Position 2'])

  # dictionaries to associate values with players
  player_salaries = dict(zip(players, salaries))
  player_position_1 = dict(zip(players, position_1))
  player_position_2 = dict(zip(players, position_2))
  player_points = dict(zip(players, points))

  # position lists
  pitcher = []
  catcher = []
  first = []
  second = []
  third = []
  short = []
  outfield = []

  for p in player_position_1:
    if player_position_1[p] == 'P':
      pitcher.append(p)
    if player_position_1[p] == 'C':
      catcher.append(p)
    if player_position_1[p] == '1B':
      first.append(p)
    if player_position_1[p] == '2B':
      second.append(p)
    if player_position_1[p] == '3B':
      third.append(p)
    if player_position_1[p] == 'SS':
      short.append(p)
    if player_position_1[p] == 'OF':
      outfield.append(p)

  for p in player_position_2:
    if player_position_2[p] == 'P':
      pitcher.append(p)
    if player_position_2[p] == 'C':
      catcher.append(p)
    if player_position_2[p] == '1B':
      first.append(p)
    if player_position_2[p] == '2B':
      second.append(p)
    if player_position_2[p] == '3B':
      third.append(p)
    if player_position_2[p] == 'SS':
      short.append(p)
    if player_position_2[p] == 'OF':
      outfield.append(p)

  prob = pulp.LpProblem('Draftkings', pulp.LpMaximize)
  SALARY_CAP = 50000

  # Decision Variables
  use_vars = pulp.LpVariable.dicts('Player', players, cat='Binary')

  # Maximize
  prob += pulp.lpSum(player_points[p] * use_vars[p] for p in players)

  # Constraints
  prob += pulp.lpSum(player_salaries[p] * use_vars[p] for p in players) <= SALARY_CAP
  prob += pulp.lpSum(use_vars[p] for p in players) == 10
  prob += pulp.lpSum(use_vars[p] for p in pitcher) == 2
  prob += pulp.lpSum(use_vars[p] for p in catcher) == 1
  prob += pulp.lpSum(use_vars[p] for p in first) == 1
  prob += pulp.lpSum(use_vars[p] for p in second) == 1
  prob += pulp.lpSum(use_vars[p] for p in third) == 1
  prob += pulp.lpSum(use_vars[p] for p in short) == 1
  prob += pulp.lpSum(use_vars[p] for p in outfield) == 3

  prob.solve()

  pd.set_option('display.max_columns', None)
  # pd.set_option('display.max_rows', None)
  for p in players:
    if use_vars[p].varValue != 0:
      print(player_position_1[p], use_vars[p].name, '=', player_points[p])
  # print("Python data:  ", data)
  # return prob.status.to_dict(orient='records')

# # Server
# @app.get('/')
# def read_root():
#   # print('hello world')
#   return {'Hello': 'World'}