import datetime
import discord
import re
import queue as que
import random
import pandas as pd
import cinephile
import games

intents = discord.Intents.all()
print('Intents set')
inputfile = open('var.txt', 'r')
bavarianid = inputfile.read()
print('files imported succesfully')


client = discord.Client(intents=intents, activity = discord.Game(name = 'squashing illegal bavarian pings'))

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message: discord.Message):

    if message.author.bot:
        #print('bot account')
        return
    if message.author == client.user:
        return
    if message.content.startswith('£'):
        await admin(message)
    
    #core features
    await checkSnail(message)
    await bavarianVerification(message)
    await mapStarrer(message)
    await cinephile.cinemaCheck(message)
    global mods
    await games.vibeCheck(message, mods)

    #debug


    #experimental features
    global experimental
    if(experimental):
        await randomFlair(message, 0.001)
        await cinephile.wikiCrawl(message)
        #await twitterFix(message)

    
async def mapStarrer(message: discord.Message):
    linksearch = re.search('//www.geoguessr.com/', message.content)
    rand = random.random()
    if (linksearch):
        print('found geoguessr link')
        if (rand < 0.01):
            responses = [
            f"ffs {message.author.display_name} stop staring at maps and do something productive",
            f"{message.author.display_name} this NEET behavior is something I only wish to see in Berlin",
            f'Hey {message.author.display_name}, a real bavarian would go outside instead!',
            f'geoguesser? I hardly knew \'er']
            await messageCarousel(message, responses)

async def bavarianVerification(message: discord.Message):
    global bavarianid
    author = message.author
    authorRoles = author.roles
    rolesPinged = message.role_mentions
    for i in range(len(rolesPinged)):
        if rolesPinged[i].name == bavarianid:
            illegal = True
            for j in range(len(authorRoles)):
                if (authorRoles[j] == rolesPinged[i]):
                    illegal = False
            if(illegal):
                if (defcon == 1):
                    timenow = message.created_at
                    slaptime = datetime.timedelta(minutes=1)
                    await message.author.edit(timed_out_until=timenow + slaptime)
                    await message.channel.send(f"{author.mention} <:ir_discussion_bain:918147188499021935>")
                else: 
                    await message.channel.send(f"{author.mention} <:ir_discussion_bain:918147188499021935>")
            else:
                rand = random.random()
                if (rand < 0.01):
                    responses = [
                        f"This is a one-in-a-million shitpost {author.name}, gigantic dub *sips Tegernseebräu*",
                        f"{author.name} I liked that poast very much, hmu if you want to do social media for Bavaria One, our homegrown space program",
                        f"Hey {author.name} that kind of king content is reserved for the Wiesen oida",
                        f"Lieber {author.name} das is ja ein legendärer Post, freundliche Grüsse Dein Maggus",
                        f"Neeeee oida {author.name} so guten kontent hast du ja ewig nicht rausgehauen"]
                    await messageCarousel(message, responses)
                else:
                    print("lost a roll")

async def twitterFix(message: discord.Message):
    link_search = re.search('twitter.com/\w*/status/(\w*)', message.content)
    if (not link_search):
        return
    linkid = link_search.group(1)
    names = [
        'MarkusSoeder',
        'gammbus',
        'yourmumlmaoxD',
        'realDonaldTrump',
        'bainsothis',
        'rarebavarianuser',
        'ifyoureadthis',
        'bainpog',
        'johnpostbabbypls'
    ]
    rand = random.random()
    rand = rand * (len(names) - 1)
    rand = round(rand)
    await message.channel.send(f'Hold up, let me fix this for you {message.author.display_name} \nhttps://twitter.com/'+ str(names[rand]) +'/status/' + str(linkid))
    


async def checkSnail(message: discord.Message):
    global queue
    global leaderboard
    content = message.content
    link_search = re.search('twitter.com/\w*/status/(\w*)', content)
    if (link_search):
        linkid = link_search.group(1)
    else:
        #print('no link found in message')
        return
    linkid = int(linkid)
    for i in range(len(queue)):
        if (queue[i][0] == linkid):
            print('match found')
            timestamp = message.created_at - pd.to_datetime(queue[i][1])
            author = queue[i][2]
            queue[i][3] += 1
            if (author == message.author.display_name):
                return
            temptime = datetime.datetime(2020,1,1)
            temptime += timestamp
            responses = [
                f'Sorry, {message.author.name}, but that is the biggest snail I\'ve ever seen! It was first posted by {author} {temptime.hour} hours {temptime.minute} minutes and {temptime.second} seconds ago and has since been posted {queue[i][3]} time(s)',
                f'Lol {message.author.name}, you\'re such a snail, {author} already posted that {temptime.hour} hours {temptime.minute} minutes and {temptime.second} seconds ago',
                f'{message.author.name}, your snailing is so extreme I won\'t bother to check the time. This link has already been posted {queue[i][3]} time(s)',
                f'Hey, {message.author.name}, if you were to scroll up instead of piping your twitterfeed straight into discord you would see the same post just {temptime.hour} hours {temptime.minute} minutes and {temptime.second} seconds earlier',
                f'I regret to inform you, {message.author.name}, but it has been {temptime.hour} hours {temptime.minute} minutes and {temptime.second} seconds since this was first posted.'
            ]
            await messageCarousel(message, responses)
            registered = False
            for entry in leaderboard:
                if entry[0] == message.author.id:
                    entry[1] += 1
                    registered = True
            if not registered:
                leaderboard.append([message.author.id, 1, message.author.mention])
            return
    queue.append([linkid, str(message.created_at), message.author.display_name, 1])
    print(queue)
    if (len(queue) > 1000):
        queue.pop(0)

async def messageCarousel(message: discord.Message, responses: list):
    rand = random.random()
    rand = rand * (len(responses) - 1)
    rand = round(rand)
    await message.channel.send(responses[rand])

async def randomFlair(message: discord.Message, p: int):
    rand = random.random()
    if(rand > p):
        return
    if(message.channel.name == 'pensive-cowboy-saloon'):
        return
    responses = [
        f'This is such a cursed chain of comments',
        f'Why are we here? Just to poast?',
        f'Look, {message.author.display_name}, I think its time to zipperclown',
        f'{message.author.mention} who is the most fascinating person you know?',
        f'God I hate doing the dishes, I just wish Karin was here to do it for me...'
    ]
    await messageCarousel(message, responses)

#administrative function to take care of config
async def admin(message: discord.Message):


    #checks privileges
    if(message.author.id != 143379423494799360):
        return
    
    global bavarianid
    global defcon
    global experimental
    global queue
    global leaderboard
    global mods

    #initializes the bot and sets variables
    if message.content.startswith('£init'):
        outputfile = open('var.txt', 'w')
        defcondetection = re.search('defcon: (\d)', message.content)
        bavarianid = message.role_mentions[0].name
        outputfile.write(bavarianid)
        await message.channel.send("Bavarian Verification initialized")
        print(defcondetection.group(1))
        if (defcondetection.group(1) == '1'):
            await message.channel.send('Bringing verification to DEFCON 1')
            defcon = 1
        return
    
    if message.content.startswith('£mods'):
        mods = message.role_mentions[0].id

    #checks if the bot is online and reports on variables
    if message.content.startswith('£wifecheck'):
        await message.channel.send('Yes, I\'m here!' + ' DEFCON is ' + str(defcon) + ' Experimental is ' + str(experimental))

    if message.content.startswith('£experimental'):
        experimental = not experimental
        await message.channel.send('Setting experimental to ' + str(experimental))

    if message.content.startswith('£export'):
        print(queue)
        df = pd.DataFrame(queue, columns=['linkid', 'timestamp', 'author', 'count'])
        df.to_csv('tweets.csv', index = False)
        df = pd.DataFrame(leaderboard, columns=['author_id', 'count', 'author_mention'])
        df.to_csv('leaderboard.csv', index = False)

    if message.content.startswith('£import'):
        df = pd.read_csv('tweets.csv')
        queue = df.values.tolist()
        df = pd.read_csv('leaderboard.csv')
        leaderboard = df.values.tolist()
        message.channel.send(f'Successfully imported files. Tweet log with {len(queue)} entries, Leaderboard with {len(leaderboard)} entries.')
        print(df.head())

    if message.content.startswith('£leaderboard'):
        sortboard = sorted(leaderboard, key = lambda snails: snails[1])
        content = ''
        for entry in sortboard:
            content += entry[2] + ' has ' + str(entry[1]) + ' tracked snails. \n'
        embed = discord.Embed(title = 'Snailboard', description= content )
        await message.channel.send(embed = embed)


experimental = True
defcon = 1
queue = []
mods = 0
leaderboard = []
auth = open('auth.txt', 'r')
authString = auth.read()
client.run(authString)
