import datetime
import discord
import re
import queue as que
import random
import cinephile
import games
import pandas as pd

intents = discord.Intents.all()
print('Intents set')
inputfile = open('var.txt', 'r')
for row in inputfile:
    bavarianid = row
print('files imported succesfully')


client = discord.Client(intents=intents, activity = discord.Game(name = 'squashing illegal bavarian pings'))

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message: discord.Message):

    
    
    if message.author == client.user:
        return
    if message.content.startswith('£'):
        await admin(message)
    
    #core features
    await checkSnail(message)
    await bavarianVerification(message)
    await mapStarrer(message)

    #debug

    #experimental features
    global experimental
    if(experimental):
        await cinephile.cinemaCheck(message)
        await games.vibeCheck(message, 'Mods')
        await cinephile.wikiCrawl(message)
        await randomFlair(message, 0.001)
    
async def mapStarrer(message: discord.Message):
    linksearch = re.search('//www.geoguessr.com/', message.content)
    rand = random.random()
    if (linksearch):
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
                    timenow = discord.utils.utcnow()
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


async def checkSnail(message: discord.Message):
    global queue
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
            if (author == message.author.display_name + 'test'):
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

#administrative function to take care of config
async def admin(message: discord.Message):

    #checks privileges
    if(message.author.id != 143379423494799360):
        return
    
    global bavarianid
    global defcon
    global experimental
    global queue

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

    if message.content.startswith('£import'):
        df = pd.read_csv('tweets.csv')
        queue = df.values.tolist()
        print(queue)


experimental = True
defcon = 1
queue = []
auth = open('auth.txt', 'r')
for row in auth:
    authString = row
client.run(authString)
