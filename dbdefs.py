import sqlite3 as sq
from typing import List


con = sq.connect("database.db", check_same_thread=False)
cur = con.cursor()

def add_user(tg_id, tg_firstname):
    cur.execute('SELECT * FROM users WHERE tg_id=?', (tg_id,))
    user = cur.fetchall()

    if user:
        return user
    
    cur.execute('INSERT INTO users (tg_id, tg_firstname, points, gp_completed, team_cost) VALUES (?,?,?,?,?)', (tg_id, tg_firstname, 0, 0, 0))
    con.commit()

def add_team(tg_id):
    cur.execute('SELECT * FROM teams WHERE user_id=?', (tg_id,))
    team = cur.fetchall()

    if team:
        return True
    
    cur.execute('INSERT INTO teams (user_id, cost, first_driver, second_driver, third_driver, engine, pit_team) VALUES (?,?,?,?,?,?,?)', (tg_id, 0, "-", "-", "-", "-", "-"))
    con.commit()
    return False

def get_team(tg_id):
    cur.execute('SELECT * FROM teams WHERE user_id=?', (tg_id,))
    team = cur.fetchall()
    return list(team[0])

def get_profile(tg_id):
    cur.execute('SELECT * FROM users WHERE tg_id=?', (tg_id,))
    profile = list(cur.fetchall()[0])
    return profile

def get_leaderboard():
    cur.execute('SELECT tg_id, points FROM users')
    users = list(map(list, cur.fetchall()))
    users.sort(key=lambda x: x[1])
    users.reverse()
    return users

def get_driver(id):
    cur.execute('SELECT name, cost FROM drivers WHERE id=?', (id,))
    driver = list(map(list, cur.fetchall()))
    return driver[0]

def get_engine(id):
    cur.execute('SELECT name, cost FROM engines WHERE id=?', (id,))
    engine = list(map(list, cur.fetchall()))
    return engine[0]
    
def get_pit_team(id):
    cur.execute('SELECT name, cost FROM pit_teams WHERE id=?', (id,))
    pit_team = list(map(list, cur.fetchall()))
    return pit_team[0]
    
def change_1_driver(tg_id, driver_name, driver_cost):
    cur.execute('SELECT cost FROM teams WHERE user_id = ?', (tg_id,))
    cost = cur.fetchall()[0][0]
    cost += driver_cost
    cur.execute('UPDATE teams SET first_driver = ? WHERE user_id = ?', (driver_name, tg_id,))
    cur.execute('UPDATE teams SET cost = ? WHERE user_id = ?', (cost, tg_id,))
    con.commit()

def change_2_driver(tg_id, driver_name, driver_cost):
    cur.execute('SELECT cost FROM teams WHERE user_id = ?', (tg_id,))
    cost = cur.fetchall()[0][0]
    cost += driver_cost
    cur.execute('UPDATE teams SET second_driver = ? WHERE user_id = ?', (driver_name, tg_id,))
    cur.execute('UPDATE teams SET cost = ? WHERE user_id = ?', (cost, tg_id,))
    con.commit()

def change_3_driver(tg_id, driver_name, driver_cost):
    cur.execute('SELECT cost FROM teams WHERE user_id = ?', (tg_id,))
    cost = cur.fetchall()[0][0]
    cost += driver_cost
    cur.execute('UPDATE teams SET third_driver = ? WHERE user_id = ?', (driver_name, tg_id,))
    cur.execute('UPDATE teams SET cost = ? WHERE user_id = ?', (cost, tg_id,))
    con.commit()

def change_engine(tg_id, engine_name, engine_cost):
    cur.execute('SELECT cost FROM teams WHERE user_id = ?', (tg_id,))
    cost = cur.fetchall()[0][0]
    cost += engine_cost
    cur.execute('UPDATE teams SET engine = ? WHERE user_id = ?', (engine_name, tg_id,))
    cur.execute('UPDATE teams SET cost = ? WHERE user_id = ?', (cost, tg_id,))
    con.commit()

def change_pit(tg_id, pit_team_name, pit_team_cost):
    cur.execute('SELECT cost FROM teams WHERE user_id = ?', (tg_id,))
    cost = cur.fetchall()[0][0]
    cost += pit_team_cost
    cur.execute('UPDATE teams SET pit_team = ? WHERE user_id = ?', (pit_team_name, tg_id,))
    cur.execute('UPDATE teams SET cost = ? WHERE user_id = ?', (cost, tg_id,))
    con.commit()

def get_name_from_msg(msg):
    res = msg.split(' - ')
    name = res[0]
    return name

def get_cost_from_msg(msg):
    res = msg.split(' - ')
    cost = res[1][1:-1]
    return int(cost)

def set_cost_zero(tg_id):
    cur.execute('UPDATE teams SET cost = ? WHERE user_id = ?', (0, tg_id,))
    con.commit()

def get_team_cost(tg_id):
    cur.execute('SELECT cost FROM teams WHERE user_id = ?', (tg_id,))
    cost = cur.fetchall()[0][0]
    return cost

def check_team_cost(tg_id):
    cur.execute('SELECT cost FROM teams WHERE user_id = ?', (tg_id,))
    cost = cur.fetchall()[0][0]
    if cost <= 60:
        return True
    return False

def check_team_composition(tg_id):
    cur.execute('SELECT first_driver, second_driver, third_driver FROM teams WHERE user_id = ?', (tg_id,))
    team_composition = cur.fetchall()[0]
    if team_composition[0] == team_composition[1] or team_composition[1] == team_composition[2] or team_composition[0] == team_composition[2]:
        return False
    return True

def get_points_by_pos_race(driver_result_race):
    cur.execute('SELECT points FROM driver_points_race WHERE id = ?', (driver_result_race,))
    points = cur.fetchall()[0][0]
    return points

def get_engine_drivers(engine_name):
    cur.execute('SELECT drivers FROM engines WHERE name = ?', (engine_name,))
    drivers_str = cur.fetchall()[0][0]
    drivers = drivers_str.split()
    return drivers

def get_pit_place(pit_team_name):
    cur.execute('SELECT id FROM pit_results WHERE name = ?', (pit_team_name,))
    pits = cur.fetchall()
    for i in range(len(pits)):
        pits[i] = pits[i][0]
    return pits

def get_pit_points(pit_place):
    if pit_place <= 6:
        cur.execute('SELECT points FROM pit_team_points_race WHERE id = ?', (pit_place,))
        points = cur.fetchall()[0][0]
        return points
    return 0

def change_points(tg_id, points):
    cur.execute('SELECT points FROM users WHERE tg_id = ?', (tg_id,))
    user_points = cur.fetchall()[0][0]
    user_points += points
    cur.execute('UPDATE users SET points = ? WHERE tg_id = ?', (user_points, tg_id,))
    con.commit()

def get_driver_number(driver_name):
    cur.execute('SELECT number FROM drivers WHERE name = ?', (driver_name,))
    number = cur.fetchall()[0][0]
    return number

def change_user_team_cost(tg_id, cost):
    cur.execute('UPDATE users SET team_cost = ? WHERE tg_id = ?', (cost, tg_id,))
    cur.execute('SELECT gp_completed FROM users WHERE tg_id = ?', (tg_id,))
    con.commit()

def change_gp_completed(tg_id):
    cur.execute('SELECT gp_completed FROM users WHERE tg_id = ?', (tg_id,))
    gp_completed = cur.fetchall()[0][0] + 1
    cur.execute('UPDATE users SET gp_completed = ? WHERE tg_id = ?', (gp_completed, tg_id,))
    con.commit()




