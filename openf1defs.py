from urllib.request import urlopen
import json
import ssl
import dbdefs as rq
import requests

ssl._create_default_https_context = ssl._create_unverified_context

driver_numbers = [81,4,1,63,16,44,12,23,55,6,31,27,18,10,22,14,87,30,5,7]

def get_driver_result_race(driver_number):
    url_ = f'https://api.openf1.org/v1/position?driver_number={driver_number}&session_key=latest'
    response = urlopen(url_)
    data = json.loads(response.read().decode('utf-8'))
    return data[-1]['position']

def get_fastest_lap():
    url_ = 'https://api.openf1.org/v1/laps?session_key=latest'
    response = urlopen(url_)
    data = json.loads(response.read().decode('utf-8'))
    valid_laps = [lap for lap in data if lap.get("lap_duration") is not None]
    fastest_lap = min(valid_laps, key=lambda x: x["lap_duration"])
    return fastest_lap['driver_number']

def check_driver_fastest_lap(driver_number):
    if get_fastest_lap() == driver_number:
        return 5
    return 0

def check_driver_pole(driver_number):
    qualik = get_quali_sessk()
    url_ = f'https://api.openf1.org/v1/position?driver_number={driver_number}&session_key={qualik}'
    response = urlopen(url_)
    data = json.loads(response.read().decode('utf-8'))
    if data[-1]['position'] == 1:
        return 10
    return 0

def get_quali_sessk():
    url_ = 'https://api.openf1.org/v1/sessions?session_key=latest'
    response = urlopen(url_)
    data = json.loads(response.read().decode('utf-8'))
    return data[0]['session_key'] - 4

def get_driver_points(driver_number):
    driver_result_race = get_driver_result_race(driver_number)
    points = rq.get_points_by_pos_race(driver_result_race)
    points += check_driver_pole(driver_number)
    points += check_driver_fastest_lap(driver_number)
    return points

def get_engine_points(engine_name):
    drivers = rq.get_engine_drivers(engine_name)
    points = 0
    for i in drivers:
        driver_number = int(i)
        driver_result_race = get_driver_result_race(driver_number)
        points += rq.get_points_by_pos_race(driver_result_race)
    points = int(round(points / len(drivers), 0) * 2)
    return points

def get_pit_team_points(pit_team_name):
    pits = rq.get_pit_place(pit_team_name)
    points = 0
    for i in range(len(pits)):
        points += rq.get_pit_points(pits[i])
    return points

def count_user_points(tg_id):
    team = rq.get_team(tg_id)
    points = 0
    for i in range(3):
        driver_number = rq.get_driver_number(team[i+3])
        points += get_driver_points(driver_number)
    points += get_engine_points(team[6])
    points += get_pit_team_points(team[7])
    rq.change_points(tg_id, points)
    rq.change_gp_completed(tg_id)