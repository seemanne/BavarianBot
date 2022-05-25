import discord
import random
import pandas as pd
import datetime as dt

#vibes.csv: userid (int) | user mention (str) | most recent vibe (int) | checkcount last hour (int) | datetime of last check (str) 

async def vibeCheck(message: discord.Message, mods: str):
    if(not message.content.startswith('vibecheck')):
        return
    
    rand = random.randint(0, 100)
    delta = dt.timedelta(hours=2)
    cutoff = 2
    modrate = 2
    currenttime = message.created_at

    #import and clean up data
    data = []
    try:
         df = pd.read_csv('vibes.csv')
         data = df.values.tolist()
    except:
        pass
    for row in data:
        row[0] = int(row[0])
        row[2] = int(row[2])
        row[3] = int(row[3])
        row[4] = pd.to_datetime(row[4])
        if (currenttime > row[4] + delta):
            row[3] = 0

    
    #figure out punishment level
    punishment = 1
    for role in message.author.roles:
        if role.name == mods:
            punishment += modrate
    for row in data:
        if row[0] == message.author.id:
            recent = row[3]
            if recent > cutoff:
                punishment += recent - cutoff
    

    rand = round(rand/punishment)


    if (rand < 27):
        flavortext = ' Yikes!'
    if (rand > 27):
        flavortext = ' (and thats ok)'
    if (rand > 40):
        flavortext = ' It\'s getting there, don\'t worry'
    if (rand > 50):
        flavortext = ' Thats an above average vibe!'
    if (rand == 69):
        flavortext = ' Nice!'
    if (rand > 69):
        flavortext = ' WOWZERS what a vibe'
    if (rand == 84):
        flavortext = ' L I T E R A L L Y  8 4'
    if (rand > 84):
        flavortext = ' Big dub of a vibe there!'
    if (rand > 99):
        flavortext = ' Your vibe is so high John will have to poast babbies'

    

    await message.channel.send(f'{message.author.display_name} your vibe is at ' + str(rand) + '%!' + flavortext)

    exists = False
    for row in data:
        if row[0] == message.author.id:
            row[2] = rand
            row[3] += 1
            row[4] = str(message.created_at)
            exists = True
    if not exists:
        data.append([message.author.id, message.author.mention, rand, 1, str(message.created_at)])

    #write to db
    
    df = pd.DataFrame(data, columns=['userid', 'mention', 'most recent vibe', 'count', 'datetime'])
    df.to_csv('vibes.csv', index = False)