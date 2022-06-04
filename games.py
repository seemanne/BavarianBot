import discord
import random
import pandas as pd
import datetime as dt

#vibes.csv: userid (int) | user mention (str) | most recent vibe (int) | checkcount last hour (int) | datetime of last check (str) 

async def vibeCheck(message: discord.Message, mods):
    if(not message.content.startswith('€vibe')):
        return
    
    czechmode = False
    if(message.content.startswith('€vibeczech')):
        czechmode = True
    
    briishmode = False
    if(message.content.startswith('€vibecheque')):
        briishmode = True
    
    rand = random.randint(0, 100)
    delta = dt.timedelta(minutes = 15)
    cutoff = 0
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
        if role.id == mods:
            punishment += modrate
    for row in data:
        if row[0] == message.author.id:
            recent = row[3]
            if recent > cutoff:
                punishment += recent - cutoff
    

    rand = round(rand/punishment)

    #generate response dicts

    english = {
        0 : 'Yikes!',
        15 : '<:ir_discussion_bain:918147188499021935>',
        27 : '(and thats ok)',
        40 : 'It\'s getting there, don\'t worry',
        51 : 'Thats an above average vibe!',
        69 : 'Nice!',
        70 : 'WOWZERS what a vibe',
        84 : 'L I T E R A L L Y  84',
        85 : 'Big dub of a vibe there',
        100 : 'Your vibe is so high john will have to poast babbies',
        200 : f'{message.author.display_name} your vibe is at ' + str(rand) + '%! '
    }
    czech = {
        0 : 'Jejda!',
        27 : '(to neva)',
        40 : 'Moc nechybí, nevěš hlavu',
        51 : 'To je nadprůměrnej vajb!',
        69 : 'Hezky!',
        70 : 'TÝJO! To je vajb!',
        84 : 'D O S L O V A 84',
        85 : 'No ty krávo, ty si dobře vajbíš!',
        89 : '✌️ získáváš certifikát svobody',
        90 : 'To sem dlouho neviděl někoho takhle vajbit!',
        100 : 'Tvůj vajb je tak vysokej, že Johnovi nezbyde nic než poastnout špunty',
        200 : f'{message.author.display_name} tvůj vajb je ' + str(rand) + ' %! '
    }
    british = {
        0 : 'Whew!',
        15 : '<:ir_discussion_bain:918147188499021935>',
        27 : '(and that is alright fellow)',
        40 : 'It is getting there, do not worry friend',
        48 : 'Oi mate do not mention that number too much.',
        49 : 'It is getting there, do not worry friend',
        51 : 'That is indeed an above average vibe!',
        52 : 'Oi mate do not mention that number too much.',
        53 : 'That is indeed an above average vibe!',
        69 : 'Blimey!',
        70 : 'Incredible vibe',
        84 : 'Q U I T E  F R A N K L Y 84',
        85 : 'That vibe is bigger than the Elizabeth Tower!',
        100 : 'Your vibes are so good, they might host an illegal lockdown party!',
        200 : f'{message.author.display_name}, by her majesty decree, you have a vibe of ' + str(rand) + '%! '
    }
    language = english
    if(czechmode): language = czech
    if(briishmode): language = british


    for key in language.keys():
        if (rand >= key):
            flavortext = language[key]
    text = language[200] + flavortext

    await message.channel.send(text)

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