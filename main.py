from fastapi import FastAPI, Request
import pandas as pd
import pulp

app = FastAPI()

@app.post('/optimize')
async def optimize(body: Request):
  data = await body.json()

  # convert to dataframe
  df = pd.DataFrame(data)

  # Convert strings to numeric values
  df['Salary'] = pd.to_numeric(df['Salary'])
  df['AvgPointsPerGame'] = pd.to_numeric(df['AvgPointsPerGame'])

  split = df['Roster Position'].str.split('/', expand=True)

  df['Position 1'] = split[0]
  df['Position 2'] = split[1]

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

  player_eligible_positions = {}

  for p in player_position_1:
    pos_list = [player_position_1[p]]

    if player_position_2[p]:
      pos_list.append(player_position_2[p])
    
    player_eligible_positions[p] = pos_list

  player_pos_pairs = [
    (p, pos) for p in players for pos in player_eligible_positions[p]
  ]


  prob = pulp.LpProblem('Draftkings', pulp.LpMaximize)
  SALARY_CAP = 50000

  # Decision Variables
  use_vars = pulp.LpVariable.dicts('Roster', player_pos_pairs, cat='Binary')

#   # Objective: Maximize
  prob += pulp.lpSum(player_points[p] * use_vars[p, pos] for p, pos in player_pos_pairs)

  # Constraints

  # Constraint: A player can be chosen only once
  for p in players:
    prob += pulp.lpSum(use_vars[p, pos] for pos in player_eligible_positions[p] ) <= 1

  # Constrain: Salary Cap  
  prob += pulp.lpSum(player_salaries[p] * use_vars[p, pos] for p, pos in player_pos_pairs) <= SALARY_CAP

  # Constraint: Roster size
  prob += pulp.lpSum(use_vars[p, pos] for p, pos in player_pos_pairs) == 10

  # Constraint:  Positions
  prob += pulp.lpSum(use_vars[p, 'P'] for p, pos in player_pos_pairs if pos == 'P') == 2
  prob += pulp.lpSum(use_vars[p, 'C'] for p, pos in player_pos_pairs if pos == 'C') == 1
  prob += pulp.lpSum(use_vars[p, '1B'] for p, pos in player_pos_pairs if pos == '1B') == 1
  prob += pulp.lpSum(use_vars[p, '2B'] for p, pos in player_pos_pairs if pos == '2B') == 1
  prob += pulp.lpSum(use_vars[p, '3B'] for p, pos in player_pos_pairs if pos == '3B') == 1
  prob += pulp.lpSum(use_vars[p, 'SS'] for p, pos in player_pos_pairs if pos == 'SS') == 1
  prob += pulp.lpSum(use_vars[p, 'OF'] for p, pos in player_pos_pairs if pos == 'OF') == 3

  prob.solve()

  lineup = []

  for p, pos in player_pos_pairs:
    if use_vars[p, pos].varValue != 0:
      player = {
        "Roster Position": pos, 
        "Name": p, 
        "Points": player_points[p],
        "Salary": player_salaries[p]
      }
      
      lineup.append(player)
  return lineup