@app.route("/get-runs")
def get_runs():
    db, username, password, hostname = get_db_creds()
    
    cnx = ''
    try:
        cnx = mysql.connector.connect(user=username, password=password,
                                      host=hostname,
                                      database=db)
    except Exception as exp:
        print(exp)

    cur = cnx.cursor()

    cur.execute("SELECT url_name, monster FROM quests")
    query = cur.fetchall()
    quests = [row[0] for row in query]
    monsters = [row[1] for row in query]

    cur.execute("SELECT name FROM runners")
    query = cur.fetchall()
    runners = [row[0] for row in query]
    new_runners = []

    create_statements = 'USE leaderboard_db;\n'
    unknown_quests = ''

    files = glob.glob('runs/2020-04/*')
    for run in files:
        r = open(run, encoding='utf-8')
        run_str = r.read()
        link = run_str[run_str.find('video          : ') + len('video          : '):run_str.find('\n', run_str.find('video       '))]
        ruleset = run_str[run_str.find('run_type       : ') + len('run_type       : '):run_str.find('\n', run_str.find('run_type       : '))]
        platform = run_str[run_str.find('platform       : ') + len('platform       : '):run_str.find('\n', run_str.find('platform       : '))]
        run_date = run_str[run_str.find('date           : ') + len('date           : '):run_str.find('\n', run_str.find('date           : '))]
        time = run_str[run_str.find('time           : ') + len('time           : '):run_str.find('\n', run_str.find('time           : '))]
        time = time.replace('\'', '\'\'')
        time = time.replace('"', '\\"')
        quest = run_str[run_str.find('quest          : ') + len('quest          : ') + 3:run_str.find('\n', run_str.find('quest          : '))]
        runner = run_str[run_str.find('runners:\n    - ') + len('runners:\n    - '):run_str.find('\n', run_str.find('runners:\n    - ') + 13)]
        if '6743' in runner:
            runner = '6743'
        if runner == '"19"':
            runner = '19'
        if runner == "'19'":
            runner = '19'
        if 'shio ' in runner:
            runner = 'shio'
        if '黒化 # 黑化由岐' in runner:
            runner = '黒化'
        if 'refill' in runner:
            runner = 'refill'
        runner_str = open('runners/' + runner + '.md', encoding='utf-8').read()
        runner = runner_str[runner_str.find('title   : ') + len('title   : '):runner_str.find('\n', runner_str.find('title   : '))]
        if '\n' in runner:
            runner = runner_str[runner_str.find('title: ') + len('title: '):runner_str.find('\n', runner_str.find('title: '))]
        runner = runner.replace('\'', '\'\'')
        runner = runner.replace('"', '\\"')
        weapon = run_str[run_str.find('weapons:\n    - ') + len('weapons:\n    - '):run_str.find('\n', run_str.find('weapons:\n    - ') + 13)]
        monster = ''
        if quest in quests:
            monster = monsters[quests.index(quest)]
            monster = monster.replace('\'', '\'\'')
            monster = monster.replace('"', '\\"')
            create_statements += "INSERT INTO runs (runner, monster, quest, time, ruleset, weapon, platform, run_date, link) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');\n" % (runner, monster, quest, time, ruleset, weapon, platform, run_date, link)
            create_statements += "UPDATE quests SET num_runs = num_runs + 1 WHERE url_name='%s';\n" % (quest)
            if monster:
                create_statements += "UPDATE monsters SET num_runs = num_runs + 1 WHERE name='%s';\n" % (monster)
            if runner not in runners and runner not in new_runners:
                new_runners.append(runner)
                create_statements += "INSERT INTO runners (name, url_name) VALUES('%s', '%s');\n" % (runner, slugify(runner))
        else:
            print(quest)

    print(create_statements, file=open('add_runs', 'w', encoding='utf-8'))

    return render_template('monsters.html', monsterlist=True)