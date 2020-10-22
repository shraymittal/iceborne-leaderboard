# Serves database queries to the site

import os
import time

from flask import request
from flask import Flask, render_template
import mysql.connector
from mysql.connector import errorcode
import glob
from slugify import slugify
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import re

import config

application = Flask(__name__)
app = application

monsters = []
monsters_time = 0
quests = []
quests_time = 0
runs = []
runs_time = 0
runs_date = []
runs_date_time = 0
runners = []
runners_time = 0
rankings = []
rankings_time = 0
weapons = ['Bow', 'Charge Blade', 'Dual Blades', 'Great Sword', 'Gunlance', 'Hammer', 'Heavy Bowgun', 'Hunting Horn', 'Insect Glaive', 'Lance', 'Light Bowgun', 'Long Sword', 'Switch Axe', 'Sword & Shield']
rulesets = ['TA Wiki', 'Freestyle']
platforms = ['All', 'Console', 'PC', 'PS4', 'Xbox']
weapons_dict = {}
weapons_dict['all'] = "All"
weapons_dict['bow'] = "Bow"
weapons_dict['charge-blade'] = "Charge Blade"
weapons_dict['dual-blades'] = "Dual Blades"
weapons_dict['great-sword'] = "Great Sword"
weapons_dict['gunlance'] = "Gunlance"
weapons_dict['hammer'] = "Hammer"
weapons_dict['heavy-bowgun'] = "Heavy Bowgun"
weapons_dict['hunting-horn'] = "Hunting Horn"
weapons_dict['insect-glaive'] = "Insect Glaive"
weapons_dict['lance'] = "Lance"
weapons_dict['light-bowgun'] = "Light Bowgun"
weapons_dict['long-sword'] = "Long Sword"
weapons_dict['switch-axe'] = "Switch Axe"
weapons_dict['sword-and-shield'] = "Sword & Shield"
weapons_dict['All'] = "all"
weapons_dict['Bow'] = "bow"
weapons_dict['Charge Blade'] = "charge-blade"
weapons_dict['Dual Blades'] = "dual-blades"
weapons_dict['Great Sword'] = "great-sword"
weapons_dict['Gunlance'] = "gunlance"
weapons_dict['Hammer'] = "hammer"
weapons_dict['Heavy Bowgun'] = "heavy-bowgun"
weapons_dict['Hunting Horn'] = "hunting-horn"
weapons_dict['Insect Glaive'] = "insect-glaive"
weapons_dict['Lance'] = "lance"
weapons_dict['Light Bowgun'] = "light-bowgun"
weapons_dict['Long Sword'] = "long-sword"
weapons_dict['Switch Axe'] = "switch-axe"
weapons_dict['Sword & Shield'] = "sword-and-shield"
weapons_dict['TA Wiki'] = 'ta-wiki-rules'
weapons_dict['Freestyle'] = 'freestyle'
weapons_dict['freestyle'] = 'Freestyle'
weapons_dict['ta-wiki-rules'] = 'TA Wiki'

cached_paths = {}

def get_db_creds():
    db = config.db
    username = config.username
    password = config.password
    hostname = config.hostname
    return db, username, password, hostname

@app.route("/")
def home():

    return monsters_list()
    

@app.route("/monsters")
def monsters_list():
    global monsters
    global monsters_time

    if not monsters or time.time() - monsters_time > 1800:
        db, username, password, hostname = get_db_creds()
        
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM monsters ORDER BY star DESC, name")
        monsters = cur.fetchall()
        monsters_time = time.time()
        cnx.commit()

    global cached_paths

    quest_dict = {}

    if ('/monsters' not in cached_paths or time.time() - cached_paths['/monsters'][0] > 1800):
        six = [dict(name=row[0], url_name=row[1], runs=row[4]) for row in monsters if row[2] == 6]
        five = [dict(name=row[0], url_name=row[1], runs=row[4]) for row in monsters if row[2] == 5]
        four = [dict(name=row[0], url_name=row[1], runs=row[4]) for row in monsters if row[2] == 4]
        three = [dict(name=row[0], url_name=row[1], runs=row[4]) for row in monsters if row[2] == 3]
        two = [dict(name=row[0], url_name=row[1], runs=row[4]) for row in monsters if row[2] == 2]
        one = [dict(name=row[0], url_name=row[1], runs=row[4]) for row in monsters if row[2] == 1]
        quest_dict['six_star'] = six
        quest_dict['five_star'] = five
        quest_dict['four_star'] = four
        quest_dict['three_star'] = three
        quest_dict['two_star'] = two
        quest_dict['one_star'] = one
        cached_paths['/monsters'] = (time.time(), quest_dict)
    else:
        quest_dict = cached_paths['/monsters'][1]

    return render_template('monsters.html', monsterlist=True, six_star=quest_dict['six_star'], five_star=quest_dict['five_star'], four_star=quest_dict['four_star'], three_star=quest_dict['three_star'], two_star=quest_dict['two_star'], one_star=quest_dict['one_star'])

@app.route("/monsters/<monster_url>/<tbl_weapon>/<tbl_ruleset>/<tbl_platform>")
def monster_page(monster_url, tbl_weapon, tbl_ruleset, tbl_platform):
    global runs
    global runs_time
    if not runs or time.time() - runs_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM runs ORDER BY time, runner")
        runs = cur.fetchall()
        runs_time = time.time()
        cnx.commit()
    
    global quests
    global quests_time
    if not quests or time.time() - quests_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)
        cur = cnx.cursor()
        cur.execute("SELECT * FROM quests ORDER BY star, type DESC, name")
        quests = cur.fetchall()
        quests_time = time.time()
        cnx.commit()

    global runners
    global runners_time
    if not runners or time.time() - runners_time > 1800:
        db, username, password, hostname = get_db_creds()
        
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM runners ORDER BY name")
        runners = cur.fetchall()
        runners_time = time.time()
        cnx.commit()    

    global monsters
    global monsters_time
    if not monsters or time.time() - monsters_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM monsters ORDER BY star DESC, name")
        monsters = cur.fetchall()
        monsters_time = time.time()
        cnx.commit()

    monster = ''
    monster_runs = []
    monster_quests = []

    global cached_paths

    if (request.path not in cached_paths or time.time() - cached_paths[request.path][0] > 1800):
        monster = get_monster(monster_url)
        for run in runs:
            if run[1] == monster and (run[5] == tbl_weapon or tbl_weapon == 'all'):
                if (tbl_ruleset == 'ta-wiki-rules' and run[4] == tbl_ruleset) or tbl_ruleset == 'freestyle':
                    if (tbl_platform == 'all') or (tbl_platform == 'pc' and run[6] == 'pc') or (tbl_platform == 'ps4' and run[6] == 'ps4') or (tbl_platform == 'xbox' and run[6] == 'xbox') or (tbl_platform =='console' and (run[6] == 'ps4' or run[6] == 'xbox')):
                        runner = run[0]
                        runner_url = get_runner_url(runner)
                        run_time = run[3]
                        weapon = run[5]
                        quest_url = run[2]
                        quest = get_quest(quest_url)
                        platform = ''
                        if not run[6] == 'xbox':
                            platform=run[6].upper()
                        else:
                            platform='Xbox'
                        platform_url = run[6]
                        link = run[8]
                        ruleset = ''
                        if run[4] == 'freestyle':
                            ruleset = 'Freestyle'
                        else:
                            ruleset = 'TA Rules'
                        monster_runs.append(dict(runner=runner, runner_url=runner_url, time=run_time, weapon=weapon, quest_url=quest_url, quest=quest, link=link, ruleset=ruleset, platform=platform, platform_url=platform_url))
        monster_quests = [dict(name=row[0], url_name=row[1], monster=row[2], num_runs=row[5]) for row in quests if row[2] == monster]
        cached_paths[request.path] = (time.time(), monster_runs, monster_quests, monster)
    else:
        monster_runs = cached_paths[request.path][1]
        monster_quests = cached_paths[request.path][2]
        monster = cached_paths[request.path][3]

    global weapons_dict

    return render_template('monsters.html', monsterList=False, runs=monster_runs, monster_url=monster_url, weapon=tbl_weapon, ruleset=tbl_ruleset, platform=tbl_platform, monster=monster, monster_quests=monster_quests, weapon_name=weapons_dict[tbl_weapon])

def get_monster(monster_url):
    global monsters
    global monsters_time
    if not monsters or time.time() - monsters_time > 1800:
        db, username, password, hostname = get_db_creds()
        
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM monsters ORDER BY star DESC, name")
        monsters = cur.fetchall()
        monsters_time = time.time()
        cnx.commit()

    monster = ''
    for mon in monsters:
        if mon[1] == monster_url:
            monster = mon[0]
    
    return monster

def get_runner_url(runner):
    global runners
    global runners_time
    if not runners or time.time() - runners_time > 1800:
        db, username, password, hostname = get_db_creds()
        
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM runners ORDER BY name")
        runners = cur.fetchall()
        runners_time = time.time()
        cnx.commit()

    runner_url = ''
    for runner_entry in runners:
        if runner_entry[0] == runner:
            runner_url = runner_entry[1]
    
    return runner_url

def get_runner(runner_url):
    global runners
    global runners_time
    if not runners or time.time() - runners_time > 1800:
        db, username, password, hostname = get_db_creds()
        
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM runners ORDER BY name")
        runners = cur.fetchall()
        runners_time = time.time()
        cnx.commit()

    runner = ''
    for runner_entry in runners:
        if runner_entry[1] == runner_url:
            runner = runner_entry[0]
    
    return runner

def get_quest(quest_url):
    global quests
    global quests_time
    if not quests or time.time() - quests_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)
        cur = cnx.cursor()
        cur.execute("SELECT * FROM quests ORDER BY star, type DESC, name")
        quests = cur.fetchall()
        quests_time = time.time()
        cnx.commit()

    quest = ''
    for quest_entry in quests:
        if quest_entry[1] == quest_url:
            quest = quest_entry[0]
    
    return quest

def get_quest_url(quest):
    global quests
    global quests_time
    if not quests or time.time() - quests_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)
        cur = cnx.cursor()
        cur.execute("SELECT * FROM quests ORDER BY star, type DESC, name")
        quests = cur.fetchall()
        quests_time = time.time()
        cnx.commit()

    quest_url = ''
    for quest_entry in quests:
        if quest_entry[0] == quest:
            quest_url = quest_entry[1]
    
    return quest_url

def get_quest_monster(quest):
    global quests
    global quests_time
    if not quests or time.time() - quests_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)
        cur = cnx.cursor()
        cur.execute("SELECT * FROM quests ORDER BY star, type DESC, name")
        quests = cur.fetchall()
        quests_time = time.time()
        cnx.commit()

    monster = {}
    monster_name = ''
    monster_url = ''
    monster_num_runs = 0
    for quest_entry in quests:
        if quest_entry[0] == quest:
            monster_name = quest_entry[2]
    
    if monster_name:
        for monster_entry in monsters:
            if monster_entry[0] == monster_name:
                monster_url = monster_entry[1]
                monster_num_runs = monster_entry[4]
    
    monster['name'] = monster_name
    monster['url_name'] = monster_url
    monster['num_runs'] = monster_num_runs

    return monster
    

@app.route("/quests")
def quests_list():
    
    global quests
    global quests_time
    if not quests or time.time() - quests_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)
        cur = cnx.cursor()
        cur.execute("SELECT * FROM quests ORDER BY star, type DESC, name")
        quests = cur.fetchall()
        quests_time = time.time()
        cnx.commit()

    global cached_paths

    quest_dict = {}

    if ('/quests' not in cached_paths or time.time() - cached_paths['/quests'][0] > 1800):
        six = [dict(name=row[0], url_name=row[1], runs=row[5]) for row in quests if row[3] == 6]
        five = [dict(name=row[0], url_name=row[1], runs=row[5]) for row in quests if row[3] == 5]
        four = [dict(name=row[0], url_name=row[1], runs=row[5]) for row in quests if row[3] == 4]
        three = [dict(name=row[0], url_name=row[1], runs=row[5]) for row in quests if row[3] == 3]
        two = [dict(name=row[0], url_name=row[1], runs=row[5]) for row in quests if row[3] == 2]
        one = [dict(name=row[0], url_name=row[1], runs=row[5]) for row in quests if row[3] == 1]
        quest_dict['six_star'] = six
        quest_dict['five_star'] = five
        quest_dict['four_star'] = four
        quest_dict['three_star'] = three
        quest_dict['two_star'] = two
        quest_dict['one_star'] = one
        cached_paths['/quests'] = (time.time(), quest_dict)
    else:
        quest_dict = cached_paths['/quests'][1]

    return render_template('quests.html', questlist=True, six_star=quest_dict['six_star'], five_star=quest_dict['five_star'], four_star=quest_dict['four_star'], three_star=quest_dict['three_star'], two_star=quest_dict['two_star'], one_star=quest_dict['one_star'])

@app.route("/quests/<quest_url>/<tbl_weapon>/<tbl_ruleset>/<tbl_platform>")
def quest_page(quest_url, tbl_weapon, tbl_ruleset, tbl_platform):
    global runs
    global runs_time
    if not runs or time.time() - runs_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM runs ORDER BY time, runner")
        runs = cur.fetchall()
        runs_time = time.time()
        cnx.commit()
    
    global quests
    global quests_time
    if not quests or time.time() - quests_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)
        cur = cnx.cursor()
        cur.execute("SELECT * FROM quests ORDER BY star, type DESC, name")
        quests = cur.fetchall()
        quests_time = time.time()
        cnx.commit()

    global runners
    global runners_time
    if not runners or time.time() - runners_time > 1800:
        db, username, password, hostname = get_db_creds()
        
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM runners ORDER BY name")
        runners = cur.fetchall()
        runners_time = time.time()
        cnx.commit()    

    global monsters
    global monsters_time
    if not monsters or time.time() - monsters_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM monsters ORDER BY star DESC, name")
        monsters = cur.fetchall()
        monsters_time = time.time()
        cnx.commit()

    quest_runs = []
    quest = ''
    quest_monster = {}

    global cached_paths

    if (request.path not in cached_paths or time.time() - cached_paths[request.path][0] > 1800):
        quest = get_quest(quest_url)
        quest_monster = get_quest_monster(quest)
        for run in runs:
            if run[2] == quest_url and (run[5] == tbl_weapon or tbl_weapon == 'all'):
                if (tbl_ruleset == 'ta-wiki-rules' and run[4] == tbl_ruleset) or tbl_ruleset == 'freestyle':
                    if (tbl_platform == 'all') or (tbl_platform == 'pc' and run[6] == 'pc') or (tbl_platform == 'ps4' and run[6] == 'ps4') or (tbl_platform == 'xbox' and run[6] == 'xbox') or (tbl_platform =='console' and (run[6] == 'ps4' or run[6] == 'xbox')):
                        runner = run[0]
                        runner_url = get_runner_url(runner)
                        run_time = run[3]
                        weapon = run[5]
                        quest_url = run[2]
                        quest = get_quest(quest_url)
                        platform = ''
                        if not run[6] == 'xbox':
                            platform=run[6].upper()
                        else:
                            platform='Xbox'
                        platform_url = run[6]
                        link = run[8]
                        ruleset = ''
                        if run[4] == 'freestyle':
                            ruleset = 'Freestyle'
                        else:
                            ruleset = 'TA Rules'
                        quest_runs.append(dict(runner=runner, runner_url=runner_url, time=run_time, weapon=weapon, quest_url=quest_url, quest=quest, link=link, ruleset=ruleset, platform=platform, platform_url=platform_url))
        cached_paths[request.path] = (time.time(), quest_runs, quest, quest_monster)
    else:
        quest_runs = cached_paths[request.path][1]
        quest = cached_paths[request.path][2]
        quest_monster = cached_paths[request.path][3]
    
    global weapons_dict

    return render_template('quests.html', questList=False, runs=quest_runs, quest_url=quest_url, weapon=tbl_weapon, ruleset=tbl_ruleset, platform=tbl_platform, quest_name=quest, monster=quest_monster, weapon_name=weapons_dict[tbl_weapon])

@app.route("/runners")
def runners_list():

    global runners
    global runners_time
    if not runners or time.time() - runners_time > 1800:
        db, username, password, hostname = get_db_creds()
        
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM runners ORDER BY name")
        runners = cur.fetchall()
        runners_time = time.time()
        cnx.commit()    

    global cached_paths

    runner_list = []

    if (request.path not in cached_paths or time.time() - cached_paths[request.path][0] > 1800):
        runner_list = [dict(name = row[0], url_name = row[1], num_runs = row[2]) for row in runners]
        cached_paths[request.path] = (time.time(), runner_list)
    else:
        runner_list = cached_paths[request.path][1]

    return render_template('runners.html', runnerlist=True, runners=runner_list)

@app.route("/runners/<runner_url>")
def runner_page(runner_url):
    global runs
    global runs_time
    if not runs or time.time() - runs_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM runs ORDER BY time, runner")
        runs = cur.fetchall()
        runs_time = time.time()
        cnx.commit()
    
    global runs_date
    global runs_date_time
    if not runs_date or time.time() - runs_date_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM runs ORDER BY run_date DESC")
        runs_date = cur.fetchall()
        runs_date_time = time.time()
        cnx.commit()

    global quests
    global quests_time
    if not quests or time.time() - quests_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)
        cur = cnx.cursor()
        cur.execute("SELECT * FROM quests ORDER BY star, type DESC, name")
        quests = cur.fetchall()
        quests_time = time.time()
        cnx.commit()

    global runners
    global runners_time
    if not runners or time.time() - runners_time > 1800:
        db, username, password, hostname = get_db_creds()
        
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM runners ORDER BY name")
        runners = cur.fetchall()
        runners_time = time.time()
        cnx.commit()

    global monsters
    global monsters_time
    if not monsters or time.time() - monsters_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM monsters ORDER BY star DESC, name")
        monsters = cur.fetchall()
        monsters_time = time.time()
        cnx.commit()

    runner = ''
    runner_runs = []

    global cached_paths

    if (request.path not in cached_paths or time.time() - cached_paths[request.path][0] > 1800):
        runner = get_runner(runner_url)
        for run in runs_date:
            if run[0] == runner:
                runner = run[0]
                runner_url = get_runner_url(runner)
                run_time = run[3]
                weapon = run[5]
                quest_url = run[2]
                quest = get_quest(quest_url)
                platform = ''
                if not run[6] == 'xbox':
                    platform=run[6].upper()
                else:
                    platform='Xbox'
                platform_url = run[6]
                link = run[8]
                ruleset = ''
                if run[4] == 'freestyle':
                    ruleset = 'Freestyle'
                else:
                    ruleset = 'TA Rules'
                runner_runs.append(dict(runner=runner, runner_url=runner_url, time=run_time, weapon=weapon, quest_url=quest_url, quest=quest, link=link, ruleset=ruleset, platform=platform, platform_url=platform_url))
        cached_paths[request.path] = (time.time(), runner_runs, runner)
    else:
        runner_runs = cached_paths[request.path][1]
        runner = cached_paths[request.path][2]

    return render_template('runners.html', runnerlist=False, runs=runner_runs, runner_url=runner_url, runner=runner)

def get_runner(runner_url):
    global runners
    global runners_time
    if not runners or time.time() - runners_time > 1800:
        db, username, password, hostname = get_db_creds()
        
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM runners ORDER BY name")
        runners = cur.fetchall()
        runners_time = time.time()
        cnx.commit()
    
    for row in runners:
        if row[1] == runner_url:
            return row[0]

@app.route("/rankings")
def rankings():
    return rankings_path(weapon='all', ruleset='freestyle', platform='all')

@app.route("/rankings/<weapon>/<ruleset>/<platform>")
def rankings_path(weapon, ruleset, platform):
    
    global runs
    global runs_time
    if not runs or time.time() - runs_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM runs ORDER BY time, runner")
        runs = cur.fetchall()
        runs_time = time.time()
        cnx.commit()
    
    global runs_date
    global runs_date_time
    if not runs_date or time.time() - runs_date_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM runs ORDER BY run_date DESC")
        runs_date = cur.fetchall()
        runs_date_time = time.time()
        cnx.commit()

    global quests
    global quests_time
    if not quests or time.time() - quests_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)
        cur = cnx.cursor()
        cur.execute("SELECT * FROM quests ORDER BY star, type DESC, name")
        quests = cur.fetchall()
        quests_time = time.time()
        cnx.commit()

    global runners
    global runners_time
    if not runners or time.time() - runners_time > 1800:
        db, username, password, hostname = get_db_creds()
        
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM runners ORDER BY name")
        runners = cur.fetchall()
        runners_time = time.time()
        cnx.commit()

    global monsters
    global monsters_time
    if not monsters or time.time() - monsters_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM monsters ORDER BY star DESC, name")
        monsters = cur.fetchall()
        monsters_time = time.time()
        cnx.commit()
    
    global rankings
    global rankings_time
    if not rankings or time.time() - rankings_time > 1800:
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM rankings ORDER BY quest")
        rankings = cur.fetchall()
        rankings_time = time.time()
        cnx.commit()

    
    global cached_paths
    global weapons_dict
    leaderboard = {}
    top10 = []
    top10_slugs = {}
    top10_medals = {}

    if (request.path not in cached_paths or time.time() - cached_paths[request.path][0] > 1800):
        queried_rankings = []
        for entry in rankings:
            if weapon == 'all':
                if entry[2] == weapons_dict[ruleset] and entry[3].lower() == platform:
                    queried_rankings.append(entry)
            else:
                if entry[1] == weapons_dict[weapon] and entry[2] == weapons_dict[ruleset] and entry[3].lower() == platform:
                    queried_rankings.append(entry)
        
        leaderboard = {}
        for entry in queried_rankings:
            if entry[4] != '':
                if entry[4] not in leaderboard:
                    leaderboard[entry[4]] = [[], [], []]
                leaderboard[entry[4]][0].append(entry[1] + " - " + entry[0] + " - " + entry[5])
            if entry[6] != '':
                if entry[6] not in leaderboard:
                    leaderboard[entry[6]] = [[], [], []]
                leaderboard[entry[6]][1].append(entry[1] + " - " + entry[0] + " - " + entry[7])
            if entry[8] != '':
                if entry[8] not in leaderboard:
                    leaderboard[entry[8]] = [[], [], []]
                leaderboard[entry[8]][2].append(entry[1] + " - " + entry[0] + " - " + entry[9])
        
        top10 = []
        top10_medals = {}
        for i in range(0, len(leaderboard)):
            top_runner = ''
            gold_medals = 0
            silver_medals = 0
            bronze_medals = 0
            for runner in leaderboard:
                if runner not in top10:
                    if len(leaderboard[runner][0]) > gold_medals:
                        top_runner = runner
                        gold_medals = len(leaderboard[runner][0])
                        silver_medals = len(leaderboard[runner][1])
                        bronze_medals = len(leaderboard[runner][2])
                    elif len(leaderboard[runner][0]) == gold_medals:
                        if len(leaderboard[runner][1]) > silver_medals:
                            top_runner = runner
                            gold_medals = len(leaderboard[runner][0])
                            silver_medals = len(leaderboard[runner][1])
                            bronze_medals = len(leaderboard[runner][2])
                        elif len(leaderboard[runner][1]) == silver_medals:
                            if len(leaderboard[runner][2]) > bronze_medals:
                                top_runner = runner
                                gold_medals = len(leaderboard[runner][0])
                                silver_medals = len(leaderboard[runner][1])
                                bronze_medals = len(leaderboard[runner][2])
            top10.append(top_runner)
            top10_medals[top_runner] = (gold_medals, silver_medals, bronze_medals)
            top10_slugs[top_runner] = [slugify(top_runner), i + 1]
            

        cached_paths[request.path] = (time.time(), leaderboard, top10, top10_medals, top10_slugs)
    else:
        leaderboard = cached_paths[request.path][1]
        top10 = cached_paths[request.path][2]
        top10_medals = cached_paths[request.path][3]
        top10_slugs = cached_paths[request.path][4]

    return render_template('rankings.html', weapon=weapon, weapon_name=weapons_dict[weapon], ruleset=ruleset, platform=platform, quest_ranks=leaderboard, top10=top10, top10_medals=top10_medals, top10_slugs=top10_slugs)

@app.route("/tierlist")
def tierlist():
    return render_template('tierlist.html')

@app.route("/rules")
def rules():
    return render_template('rules.html')

@app.route("/submit")
def submit():
    return render_template('submit.html')

@app.route("/about")
def about():
    return render_template('about.html')

'''
@app.route("/slug-test")
def slug_test():
    print(get_quest_url("USJ: Shine On Forever"))
    return render_template('about.html')
'''

#@app.route("/import")
def import_new_runs():

    global cached_paths
    global weapons
    global rulesets
    global platforms
    global weapons_dict

    if ('import' not in cached_paths or time.time() - cached_paths['import'][0] > 1800):
        db, username, password, hostname = get_db_creds()
        cnx = ''
        try:
            cnx = mysql.connector.connect(user=username, password=password,
                                        host=hostname,
                                        database=db)
        except Exception as exp:
            print(exp)

        cur = cnx.cursor()
        cur.execute("SELECT * FROM new_runs")
        new_runs = cur.fetchall()
        global weapons_dict
        new_runners = []
        for new_run in new_runs:
            runner = ''
            if new_run[8] == '' and new_run[1] not in new_runners:
                runner = new_run[1].replace('\'', '\'\'')
                cur.execute("INSERT INTO runners (name, url_name, num_runs) VALUES ('%s', '%s', 0)" % (runner, slugify(new_run[1])))
                new_runners.append(runner)
            elif new_run[1] in new_runners:
                runner = new_run[1]
            else:
                runner = get_runner(new_run[8]).replace('\'', '\'\'')
            monster = get_quest_monster(new_run[7])['name'].replace('\'', '\'\'')
            quest = get_quest_url(new_run[7]).replace('\'', '\'\'')
            print(quest)
            print(new_run[7])
            run_time = new_run[2].replace('\'', '\'\'')
            ruleset = weapons_dict[new_run[5]].replace('\'', '\'\'')
            weapon = weapons_dict[new_run[6]].replace('\'', '\'\'')
            platform = new_run[4].replace('\'', '\'\'')
            run_date = new_run[0]
            link = new_run[3].replace('\'', '\'\'')
            cur.execute("INSERT INTO runs (runner, monster, quest, time, ruleset, weapon, platform, run_date, link) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (runner, monster, quest, run_time, ruleset, weapon, platform, run_date, link))
            cur.execute("UPDATE runners SET num_runs = num_runs + 1 WHERE name='%s'" % (runner))
            cur.execute("UPDATE quests SET num_runs = num_runs + 1 WHERE url_name='%s'" % (quest))
            if monster != '':
                cur.execute("UPDATE monsters SET num_runs = num_runs + 1 WHERE name='%s'" % (monster))

        cur.execute("DELETE FROM new_runs")

        cur.execute("SELECT * FROM rankings ORDER BY quest")
        rankings = cur.fetchall()
        cur.execute("SELECT * FROM quests WHERE num_runs >= 30")
        quests = cur.fetchall()
        
        for quest in quests:
            found = False
            for entry in rankings:
                if entry[0] == quest[0]:
                    found = True
            if not found:
                quest_name = quest[0].replace('\'', '\'\'')
                print(quest_name)
                for weapon in weapons:
                    for ruleset in rulesets:
                        for platform in platforms:
                            cur.execute("INSERT INTO rankings (quest, weapon, ruleset, platform, runner1, time1, runner2, time2, runner3, time3, time_to_beat) VALUES ('%s', '%s', '%s', '%s', '', '', '', '', '', '', '%s')" % (quest_name, weapon, ruleset, platform, ""))

        cur.execute("SELECT * FROM rankings ORDER BY quest")
        rankings = cur.fetchall()

        for entry in rankings:
            entry = list(entry)
            if entry[3] == 'All':
                if entry[2] == 'TA Wiki':
                    cur.execute("SELECT * FROM runs WHERE quest='%s' AND weapon='%s' AND ruleset='%s' ORDER BY time" % (slugify(entry[0].replace("'", "")), weapons_dict[entry[1]], weapons_dict[entry[2]]))
                else:
                    cur.execute("SELECT * FROM runs WHERE quest='%s' AND weapon='%s' ORDER BY time" % (slugify(entry[0].replace("'", "")), weapons_dict[entry[1]]))
            elif entry[3] == 'Console':
                if entry[2] == 'TA Wiki':
                    cur.execute("SELECT * FROM runs WHERE quest='%s' AND weapon='%s' AND ruleset='%s' AND (platform='ps4' OR platform='xbox') ORDER BY time" % (slugify(entry[0].replace("'", "")), weapons_dict[entry[1]], weapons_dict[entry[2]]))
                else:
                    cur.execute("SELECT * FROM runs WHERE quest='%s' AND weapon='%s' AND (platform='ps4' OR platform='xbox') ORDER BY time" % (slugify(entry[0].replace("'", "")), weapons_dict[entry[1]]))
            else:
                if entry[2] == 'TA Wiki':
                    cur.execute("SELECT * FROM runs WHERE quest='%s' AND weapon='%s' AND ruleset='%s' AND platform='%s' ORDER BY time" % (slugify(entry[0].replace("'", "")), weapons_dict[entry[1]], weapons_dict[entry[2]], entry[3].lower()))
                else:
                    cur.execute("SELECT * FROM runs WHERE quest='%s' AND weapon='%s' AND platform='%s' ORDER BY time" % (slugify(entry[0].replace("'", "")), weapons_dict[entry[1]], entry[3].lower()))
            runs = cur.fetchall()
            num_runs = 0
            entry_runners = []
            for run in runs:
                if run[0] not in entry_runners and num_runs < 3:
                    entry[4 + num_runs * 2] = run[0].replace('\'', '\'\'')
                    entry[5 + num_runs * 2] = run[3].replace('\'', '\'\'')
                    entry_runners.append(run[0])
                    num_runs = num_runs + 1
            
            if num_runs == 0:
                entry[4] = ''
                entry[5] = ''
                entry[6] = ''
                entry[7] = ''
                entry[8] = ''
                entry[9] = ''
            elif num_runs == 1:
                entry[6] = ''
                entry[7] = ''
                entry[8] = ''
                entry[9] = ''
            elif num_runs == 2:
                entry[8] = ''
                entry[9] = ''

            print(entry)
            cur.execute("UPDATE rankings SET runner1='%s', time1='%s', runner2='%s', time2='%s', runner3='%s', time3='%s' WHERE quest='%s' AND weapon='%s' AND ruleset='%s' AND platform='%s'" % (entry[4], entry[5], entry[6], entry[7], entry[8], entry[9], entry[0].replace('\'', '\'\''), entry[1], entry[2], entry[3]))

        cnx.commit()
        return home()

def clean_urls():
    db, username, password, hostname = get_db_creds()
    cnx = ''
    try:
        cnx = mysql.connector.connect(user=username, password=password,
                                    host=hostname,
                                    database=db)
    except Exception as exp:
        print(exp)

    cur = cnx.cursor()
    cur.execute("SELECT * FROM runs")
    new_runs = cur.fetchall()
    for new_run in new_runs:
        link = new_run[8]
        new_link = re.sub('&t=([^/]+)$', '', link)
        if (not link == new_link):
            cur.execute("UPDATE runs SET link='%s' WHERE link='%s'" % (new_link, link))
    cnx.commit()
    return home()

#scheduler = BackgroundScheduler()
#scheduler.add_job(func=import_new_runs, trigger="interval", seconds=1800)
#scheduler.start()
#atexit.register(lambda: scheduler.shutdown())