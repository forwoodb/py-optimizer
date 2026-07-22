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

  # # position lists
  # pitcher = []
  # catcher = []
  # first = []
  # second = []
  # third = []
  # short = []
  # outfield = []

  # for p in player_position_1:
  #   pos1 = player_position_1[p]
  #   pos2 = player_position_2[p]

  #   if pos1 == 'P'  or pos2 == 'P':
  #     pitcher.append(p)
  #   if pos1 == 'C'  or pos2 == 'C':
  #     catcher.append(p)
  #   if pos1 == '1B'  or pos2 == '1B':
  #     first.append(p)
  #   if pos1 == '2B'  or pos2 == '2B':
  #     second.append(p)
  #   if pos1 == '3B'  or pos2 == '3B':
  #     third.append(p)
  #   if pos1 == 'SS'  or pos2 == 'SS':
  #     short.append(p)
  #   if pos1 == 'OF'  or pos2 == 'OF':
  #     outfield.append(p)

  # https://gemini.google.com/app/484145b94e9b3555
  player_eligible_positions = {}

  for p in player_position_1:
    pos_list = [player_position_1[p]]

    if player_position_2[p]:
      pos_list.append(player_position_2[p])
    
    player_eligible_positions[p] = pos_list

  player_pos_pairs = [
    (p, pos) for p in players for pos in player_eligible_positions[p]
  ]

  # print(player_pos_pairs)

  # # https://chatgpt.com/c/6a5dc821-4d7c-83ea-a9e6-67170ee3056e
  # eligible = []  

  # for p in players:
  #   eligible.append((p, player_position_1[p]))

  #   if pd.notna(player_position_2[p]):
  #     eligible.append((p, player_position_2[p]))

  # print(eligible)



  prob = pulp.LpProblem('Draftkings', pulp.LpMaximize)
  SALARY_CAP = 50000

  # Decision Variables
#   use_vars = pulp.LpVariable.dicts('Player', players, cat='Binary')
  use_vars = pulp.LpVariable.dicts('Roster', player_pos_pairs, cat='Binary')

#   # Objective: Maximize
#   prob += pulp.lpSum(player_points[p] * use_vars[p] for p in players)
  prob += pulp.lpSum(player_points[p] * use_vars[p, pos] for p, pos in player_pos_pairs)

  # Constraints

  # Constraint: A player can be chosen only once
  for p in players:
    prob += pulp.lpSum(use_vars[p, pos] for pos in player_eligible_positions[p] ) <= 1

  # Constrain: Salary Cap  
  prob += pulp.lpSum(player_salaries[p] * use_vars[p, pos] for p, pos in player_pos_pairs) <= SALARY_CAP

  # Constraint: Roster size
  prob += pulp.lpSum(use_vars[p, pos] for p, pos in player_pos_pairs) == 10
#   prob += pulp.lpSum(use_vars[p] for p in pitcher) == 2
#   prob += pulp.lpSum(use_vars[p] for p in catcher) == 1
#   prob += pulp.lpSum(use_vars[p] for p in first) == 1
#   prob += pulp.lpSum(use_vars[p] for p in second) == 1
#   prob += pulp.lpSum(use_vars[p] for p in third) == 1
#   prob += pulp.lpSum(use_vars[p] for p in short) == 1
#   prob += pulp.lpSum(use_vars[p] for p in outfield) == 3

  prob.solve()

#   print(pulp.LpStatus(prob.status))

  # pd.set_option('display.max_columns', None)
  # pd.set_option('display.max_rows', None)

  lineup = []

  for p, pos in player_pos_pairs:
    if use_vars[p, pos].varValue != 0:
      player = {
        "Roster Position": pos, 
        "Name": p, 
        "Points": player_points[p],
        "Salary": player_salaries[p]
      }
      # print(pos)
      # print(pos, p)
      # print(player)
      lineup.append(player)
  # print("Python data:  ", data)
  # return prob.status.to_dict(orient='records')
  # print(pulp.value(prob.objective))
  return lineup

# # # Server
# # @app.get('/')
# # def read_root():
# #   # print('hello world')
# #   return {'Hello': 'World'}