import asyncio

'''
some functions for async prompt to annoy the calendar app developed by an
enemy developer ;-)
'''


async def annoy_calendar():
    namensliste = [
        'kevin', 'jolle', 'dieter', 'messer-meshut', 'deine mutter',
        'ramon', 'umut', 'gruschka', 'sven', 'peter', 'trichtan', 'ferdi'
    ]
    anlassliste = [
        'geburtstag', 'tot', 'weg', 'wieder da', 'egal', 'arbeiten',
        'urlaub', 'party', 'scheisse', 'aufräumen', 'putzen'
    ]
    rollenliste = [
        'superidiot', 'reggaekasper', 'saufbold', 'egal'
    ]
    gruppenliste = [
        'juden', 'neger', 'subversives pack', 'nazis', 'zecken',
        'reggaekasper',
    ]

    colors = ['red', 'green', 'yellow', 'black', 'white', 'blue']

    starts_temp = "2018-03-{day}T20:59:59.999Z"
    ends_temp = "2018-03-{day}T20:59:59.999Z"

    event_address = 'http://192.168.88.46:3006/api/setEvents/'
    user_address = 'http://192.168.88.46:3006/api/setUserData/'

    userlist = []

    while True:
        random_day = str(random.randint(1, 29))
        if len(random_day) == 1:
            random_day = '0' + random_day
        year = str(random.randint(1000, 3000))
        data_event = {
            'title': '%s %s %s' % (random.choice(gruppenliste), random.choice(namensliste), random.choice(anlassliste)),
            'xpos': '1',
            "startsAt": "{year}-03-{day}T14:00:00.000Z".format(day=random_day, year=year),
            "endsAt": "{year}-03-{day}T22:59:59.999Z".format(day=random_day, year=year),
            "color": {
                "primary": webcolors.name_to_hex(random.choice(colors)),
                "secondary": webcolors.name_to_hex(random.choice(colors)),
            },
            "draggable": True,
            "resizable": True,
            "eventHours": 10,
            "shiftPlan": {
                "purchaser": random.choice(gruppenliste),
                "preparer": random.choice(gruppenliste),
                "cleaner": random.choice(gruppenliste),
                "debuilder": random.choice(gruppenliste),
                "timeLine": [i for i in range(14, 24)],
                "taskMembers": {
                    "Theke": [random.choice(namensliste) for i in range(10)],
                    "Tür": [random.choice(namensliste) for i in range(10)],
                    "Kasse": [random.choice(namensliste) for i in range(10)],
                    "Support": [random.choice(namensliste) for i in range(10)],
                    "Sound": [random.choice(namensliste) for i in range(10)],
                    "Bands": [random.choice(namensliste) for i in range(10)],
                },
            },
        }

        p = requests.post(event_address, json=data_event)
        print('Event posted. Result: %s' % p.text)

        userlist.append(random.choice(namensliste))
        # userdict = {}

        userdict = []
        for index, username in enumerate(userlist):
            userdict.append({
                'name': username,
                'rolle': random.choice(rollenliste)
            })

        p = requests.post(user_address, json=userdict)
        print('Users posted. Result: %s' % p.text)

        await asyncio.sleep(.1)


async def spawn_kevin():
    process = await asyncio.create_subprocess_exec(
        *['bash', 'spawn_kevin.sh'],
        stdout=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
