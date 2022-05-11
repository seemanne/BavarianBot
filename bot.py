import datetime
import discord
import re
import queue as que
import random
import cinephile

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
async def on_message(message):

    
    
    if message.author == client.user:
        return
    if message.content.startswith('£init'):
        if(message.author.id != 143379423494799360):
            return
        global bavarianid
        global defcon
        
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
    
    if message.content.startswith('£wifecheck'):
        await message.channel.send('Yes, I\'m here, DEFCON is: ' + str(defcon))
    await checkSnail(message)
    await bavarianVerification(message)
    await mapStarrer(message)
    await cinephile.cinemaCheck(message)
    
async def mapStarrer(message: discord.Message):
    linksearch = re.search('//www.geoguessr.com/', message.content)
    rand = random.random()
    if (linksearch):
        if (rand < 0.1):
            responses = [
            f"ffs {message.author.display_name} stop staring at maps and do something productive",
            f"{message.author.display_name} this NEET behavior is something I see in Berlin",
            f'Hey {message.author.display_name}, a real bavarian would go outside instead!']
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
    print(linkid)
    print(message.created_at)
    for i in range(len(queue)):
        if (queue[i][0] == linkid):
            timestamp = message.created_at - queue[i][1]
            author = queue[i][2].display_name
            temptime = datetime.datetime(2020,1,1)
            temptime += timestamp
            await message.channel.send(f'Sorry, {message.author.name}, but that is the biggest snail I\'ve ever seen! It was first posted by {author} {temptime.hour} hours {temptime.minute} minutes and {temptime.second} seconds ago')
            return
    queue.append([linkid, message.created_at, message.author])
    if (len(queue) > 1000):
        queue.pop(0)

async def messageCarousel(message: discord.Message, responses: list):
    rand = random.random()
    rand = rand * (len(responses) - 1)
    rand = round(rand)
    await message.channel.send(responses[rand])

defcon = 0
queue = []
auth = open('auth.txt', 'r')
for row in auth:
    authString = row
client.run(authString)
