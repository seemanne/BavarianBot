import datetime
import discord
import re
import queue as que
import random
import pandas as pd
import sqlite3
import time
import my_secrets
from discord import app_commands

#import giffer
import cinephile
import games
#import imagesnail
import disutils
from my_secrets import MOD_ID



intents = discord.Intents.all()
print('Intents set')
inputfile = open('var.txt', 'r')
bavarianid = inputfile.read()
print('files imported succesfully')
#df = pd.DataFrame(columns = ['contentaware'])
#print('created fresh imagehash database')
#df.to_csv('images.csv', index = False)
con = sqlite3.connect('chalkotheke.db')
emoji_con = sqlite3.connect('emojis.db')
#con = sqlite3.connect('newexample.db')




class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents, **options):
        super().__init__(intents=intents, **options)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=my_secrets.MY_GUILD)
        await self.tree.sync(guild=my_secrets.MY_GUILD)

client = MyClient(intents=intents, activity = discord.Game(name = 'squashing illegal bavarian pings'))

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    me = client.get_user(my_secrets.MY_ACC_ID)
    await me.create_dm()
    global me_dm
    me_dm = me.dm_channel
    await me_dm.send('Bot is now active!')
    await client.get_channel(my_secrets.LOG_CHANNEL).send('Snailbot is now active.')

@client.event
async def on_message(message: discord.Message):

    if message.author.bot:
        #print('bot account')
        return
    if message.author == client.user:
        return
    if message.content.startswith('£'):
        await admin(message)
    
    if(str(message.channel.type) == 'private'): return


    global enabled
    #core features
    if(enabled):

        await checkSnail(message)
        await bavarianVerification(message)
        await mapStarrer(message)
        await cinephile.cinemaCheck(message)
        global mods
        await games.vibeCheck(message, mods)

    global twitterfix
    if(twitterfix): await twitterFix(message)
    #debug


    #experimental features
    global experimental
    if(experimental):
        #await imagesnail.detect(message)
        await randomFlair(message, 0.0001)
        await cinephile.wikiCrawl(message)
    con.commit()

@client.event
async def on_message_delete(message: discord.Message):
    global recent_snails_list
    for i in iter(recent_snails_list):
        if i == message.id:
            await message.channel.send(f'It looks like {message.author.mention} tried to delete their snail. Here is their message in its full glory: \n {message.content}')
    
@client.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    if isinstance(reaction.emoji, str): return
    usable = True
    try:
        usable = reaction.emoji.is_usable()
    except:
        return
    if not usable: return
    emoji_cursor = emoji_con.cursor()
    res = emoji_cursor.execute(f'select * from emojitable where emoji_id = {reaction.emoji.id}')
    registered = True
    if res.fetchone() == None: registered = False
    if not registered:
        emoji_cursor.execute(f'insert into emojitable values ({reaction.emoji.id}, 1, \'<:{reaction.emoji.name}:{reaction.emoji.id}>\')')
    else:
        res = emoji_cursor.execute(f'select * from emojitable where emoji_id = {reaction.emoji.id}')
        emoji_cursor.execute(f'update emojitable set count = {res.fetchmany()[0][1] + 1} where emoji_id = {reaction.emoji.id}')
    emoji_con.commit()


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
            await disutils.messageCarousel(message, responses)

async def bavarianVerification(message: discord.Message):
    global bavarianid
    author = message.author
    authorRoles = author.roles
    rolesPinged = message.role_mentions
    for i in range(len(rolesPinged)):
        if rolesPinged[i].name == bavarianid:
            illegal = True
            for j in range(len(authorRoles)):
                if (authorRoles[j].id == rolesPinged[i].id):
                    illegal = False
            if(illegal):
                if message.author.id == my_secrets.MOOSER_ID & len(message.attachments) > 0 & random.random() > 0.75:
                    responses = [
                        'That is the most adorable thing I\'ve ever seen',
                        'Moose, this is cute as hell!',
                        'The vibe of this picture is so high john will have to... wait what?',
                        'Oh man, she\'s just like gammbus',
                    ]
                if (defcon == 1):
                    slaptime = datetime.timedelta(minutes=1)
                    await message.channel.send(f"{author.mention} <:ir_discussion_bain:918147188499021935>")
                    await message.author.timeout(slaptime, reason='Illegal Bavarian Ping')
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
                    await disutils.messageCarousel(message, responses)

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
    global recent_snails_list
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
            timestamp = message.created_at - pd.to_datetime(queue[i][1])
            sniper_id = queue[i][2]
            sniper = client.get_user(sniper_id)
            global me_dm
            if message.author.id == my_secrets.TRACK_ID:
                content = f'Snail by {message.author.name} \n In channel: {message.channel.name} \n Channel type: {message.channel.type} \n posted at {message.created_at}'
                embed = discord.Embed(title= 'Snail report', description=content)
                await me_dm.send(embed=embed)
            if str(message.channel.type) == 'private_thread':
                #await me_dm.send(f'Snailbot found snail in thread {message.channel.name} by f{message.author.name}')
                responses = [
                    f'You should have better things to do than snailing in this channel {message.author.mention}!',
                    f'{message.author.mention} its time to go outside and touch some grass!',
                    f'Stop, lol!',
                    f'Find another hobby than snailing around {message.author.mention}.'
                ]
            if queue[i][3] > 3:
                await me_dm.send(f'something fuckie going on')
                await me_dm.send(f'user: {message.author.name}, server: {message.guild.name}, channel: {message.channel.name}')
            if (sniper.id == message.author.id):
                print('selfsnail, lol')
                #return
            queue[i][3] += 1
            temptime = datetime.datetime(2020,1,1)
            temptime += timestamp
            timestring = []
            if temptime.day > 0:
                timestring.append(f"{temptime.day} day{'s' if temptime.day != 1 else ''}")
            if temptime.hour > 0:
                timestring.append(f"{temptime.hour} hour{'s' if temptime.hour != 1 else ''}")
            if temptime.minute > 0:
                timestring.append(f"{temptime.minute} minute{'s' if temptime.minute != 1 else ''}")
            if temptime.second > 0:
                timestring.append(f"{temptime.second} second{'s' if temptime.second != 1 else ''}")
            responses = [
                f'Sorry, {message.author.name}, but that is the biggest snail I\'ve ever seen! It was first posted by {sniper.display_name} {" ".join(timestring) or "0 seconds"} ago and has since been posted {disutils.numeral_adverb(queue[i][3]- 1)}.',
                f'Lol {message.author.name}, you\'re such a snail, {sniper.display_name} already posted that {" ".join(timestring) or "0 seconds"} ago',
                f'{message.author.name}, your snailing is so extreme I won\'t bother to check the time. This link has now been posted {disutils.numeral_adverb(queue[i][3])}!',
                f'Hey, {message.author.name}, if you were to scroll up instead of piping your twitterfeed straight into discord you would see the same post just {" ".join(timestring) or "0 seconds"} earlier',
                f'I regret to inform you, {message.author.name}, but it has been {" ".join(timestring) or "0 seconds"} since this was first posted.'
            ]
            await disutils.messageCarousel(message, responses)

            recent_snails_list.append(message.id)
            if (len(recent_snails_list) > 5): recent_snails_list.pop(0)

            registered = True
            cur = con.cursor()
            res = cur.execute(f'select * from leaderboard where author_id = {message.author.id}')
            if res.fetchone() == None: registered = False
            if not registered:
                cur.execute(f'insert into leaderboard values ({message.author.id}, 1, \'{message.author.mention}\')')
                await message.channel.send(f'Adding new user to db, {message.author.mention} congrats on your first snail!')
            else:
                res = cur.execute(f'select * from leaderboard where author_id = {message.author.id}')
                cur.execute(f'update leaderboard set count = {res.fetchmany()[0][1] + 1} where author_id = {message.author.id}')
            
            registered = True
            res = cur.execute(f'select * from snipeboard where author_id = {sniper.id}')
            if res.fetchone() == None: registered = False
            if not registered:
                cur.execute(f'insert into snipeboard values ({sniper.id}, 1, \'{sniper.mention}\')')
            else:
                res = cur.execute(f'select * from snipeboard where author_id = {sniper.id}')
                cur.execute(f'update snipeboard set score = {res.fetchmany()[0][1] + 1} where author_id = {sniper.id}')            
            cur.close()
            return
    queue.append([linkid, str(message.created_at), message.author.id, 1])
    if (len(queue) > 1000):
        queue.pop(0)

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
    await disutils.messageCarousel(message, responses)

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
    global enabled
    global twitterfix

    cur = con.cursor()
    cur.arraysize = 5

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

    if message.content.startswith('£sql'):
        content = message.content.replace('£sql ','')
        t0 = time.process_time()
        await message.channel.send('executing: ' + content)
        try: 
            res = cur.execute(content)
        except Exception as e:
            await message.channel.send('Querry failed with: ' + str(e))
            return
        clown = res.fetchmany()
        await message.channel.send(clown)
        await message.channel.send('execution time: ' + str(time.process_time()-t0))


    #checks if the bot is online and reports on variables
    if message.content.startswith('£wifecheck'):
        await message.channel.send('Yes, I\'m here!' + ' DEFCON is ' + str(defcon) + ' Experimental is ' + str(experimental))

    if message.content.startswith('£experimental'):
        experimental = not experimental
        await message.channel.send('Setting experimental to ' + str(experimental))

    if message.content.startswith('£twitterfix'):
        twitterfix = not twitterfix

    if message.content.startswith('£export'):
        print(queue)
        df = pd.DataFrame(queue, columns=['linkid', 'timestamp', 'author', 'count'])
        df.to_csv('tweets.csv', index = False)

    if message.content.startswith('£migrate'):
        cur.execute('create table snipeboard(author_id int, score int, author_mention text)')
        await message.channel.send('Created snipeboard')
        cur.execute('create unique index idx_author_id on snipeboard (author_id)')
        con.commit()
        await message.channel.send('Created index column on variable author_id')

    if message.content.startswith('£import'):
        df = pd.read_csv('tweets.csv')
        queue = df.values.tolist()
        await message.channel.send(f'Successfully imported files. Tweet log with {len(queue)} entries.')

    if message.content.startswith('£emojirank'):
        content = ''
        emoji_cursor = emoji_con.cursor()
        for row in emoji_cursor.execute('select emoji_text, count from emojitable order by count desc limit 40'):
            content += f'{row[0]} has been used {row[1]} times. \n'
        embed = discord.Embed(title = 'Emojirank', description= content)
        await message.channel.send(embed = embed)        

    if message.content.startswith('£snailboard'):
        content = ''
        for row in cur.execute('select author_mention, count from leaderboard order by count desc'):
            content += f'{row[0]} has {row[1]} tracked snails. \n'
        embed = discord.Embed(title = 'Snailboard', description= content)
        await message.channel.send(embed = embed)

    if message.content.startswith('£snipeboard'):
        content = ''
        for row in cur.execute('select author_mention, score from snipeboard order by score desc'):
            content += f'{row[0]} has {row[1]} tracked snipes. \n'
        embed = discord.Embed(title = 'Snipeboard', description= content)
        await message.channel.send(embed = embed)
    
    if message.content.startswith('£toggle'):
        enabled = not enabled
        if(enabled):
            await message.channel.send('Enabling core features')
        else:
            await message.channel.send('Disabling the bots core features')

    
    
    cur.close()

@client.tree.command()
@app_commands.describe(
    link='The twitter link you want to check'
)
async def snail_gamble(interaction: discord.Interaction, link: str):
    """Tests your tweet against the current tweet queue. Careful: the bot slaps you if it isn't snail."""
    global queue
    link_search = re.search('twitter.com/\w*/status/(\w*)', link)
    for role in interaction.user.roles:
        if role.id == my_secrets.MOD_ID: 
            await interaction.channel.send(f'Sorry {interaction.user.display_name}, but I don\'t serve the mods.')
            return
    if (link_search):
        linkid = link_search.group(1)
    else:
        await interaction.response.send_message(f'Sorry, but this is not a valid twitter link!', ephemeral= True)
        return
    linkid = int(linkid)
    for i in range(len(queue)):
        if (queue[i][0] == linkid):
            await interaction.response.send_message('This link is snail, post at your own risk!', ephemeral = True)
            await interaction.channel.send('Oh wow, looks like someone just managed to dodge a snail using /snail_gamble, guess you\'ll never find out who it was!')
            return
    await interaction.response.send_message('This link is not snail!',ephemeral= True)
    await interaction.channel.send(f'Someone just wanted to post this twitter link, but they risked a snail_gamble so now they cannot post it. I\'m taking care of it: https://{link_search.group(0)}')
    queue.append([linkid, str(interaction.created_at), client.user.id, 1])
    if (len(queue) > 1000):
        queue.pop(0)
    await interaction.user.timeout(datetime.timedelta(minutes = 1), reason = 'Lost snail gamble!')
    return

@client.tree.command()
@app_commands.describe(
    link='The snail link you want to post'
)
async def snail_post(interaction: discord.Interaction, link: str):
    """Reposts a tweet which is snail. Will ban you from use if you abuse it."""
    global queue
    global ban_list
    for i in ban_list:
        if i == interaction.user.id:
            await interaction.response.send_message(f'Sorry, {interaction.user.display_name} but you are banned from snail_post!')
            return
    link_search = re.search('twitter.com/\w*/status/(\w*)', link)
    if (link_search):
        linkid = int(link_search.group(1))
    else:
        await interaction.response.send_message(f'Sorry, but this is not a valid twitter link!', ephemeral= True)
        return
    for i in range(len(queue)):
        if (queue[i][0] == linkid):
            await interaction.channel.send(f'Repost by {interaction.user.mention}: {link}')
            await interaction.response.send_message('Done!')
            return
    await interaction.response.send_message(f'Sorry, {interaction.user.mention} but that is not a known twitter link, you have been banned from snail_post')
    embed = discord.Embed(title= 'User mutation', description= f'User: {interaction.user.mention} \n Mutation: Banned from using /snail_post \n Reason: Non-snail link')
    await client.get_channel(my_secrets.LOG_CHANNEL).send(embed=embed)
    ban_list.append(interaction.user.id)
    return

@client.tree.command()
@app_commands.describe(
    timestamp='Your timestamp in the ms format'
)
async def timesync(interaction: discord.Interaction, timestamp: str):
    """Add your time to the current sync table. Can also update your time."""
    if len(timestamp) > 5:
        await interaction.response.send_message('Sorry but that string is too long!')
        return
    global timesync_table
    minutes = int(timestamp[:-2])
    seconds = int(timestamp[-2:])
    hours = 0
    while minutes > 60:
        minutes -= 60
        hours += 1

    user_timestamp = datetime.datetime.combine(datetime.date.today(), datetime.time(hour= hours, minute=minutes, second=seconds))
    interaction_timestamp = interaction.created_at
    user_id = interaction.user.id

    timesync_table[str(user_id)] = [user_timestamp, interaction_timestamp, interaction.user.mention]
    await interaction.response.send_message('Added your timestamp to the sync table!')
    
    print(user_timestamp)
    print(interaction.created_at)
    return

@client.tree.command()
async def timesynctable(interaction: discord.Interaction):
    """Show the current sync table"""
    global timesync_table
    interaction_timestamp = interaction.created_at
    content = ''
    
    for key in timesync_table.keys():
        content += f'{disutils.get_time_in_fifa_format(timesync_table[key][0] + (interaction_timestamp - timesync_table[key][1]))} by {timesync_table[key][2]} \n'
    
    embed = discord.Embed(title= 'Current tracked timestamps', description=content)
    await interaction.channel.send(embed=embed)
    await interaction.response.send_message('Done!')
    return

@client.tree.command()
async def timesyncreset(interaction: discord.Interaction):
    allowed = False
    for i in interaction.user.roles:
        if i.name == bavarianid:
            allowed = True
    if interaction.user.id == my_secrets.MY_ACC_ID:
        allowed = True
    if not allowed:
        await interaction.response.send_message('Sorry, but you cannot do this.')
        return
    global timesync_table
    timesync_table = {}
    await interaction.response.send_message('Cleared table!')
    return

@client.tree.command()
async def bettzeit(interaction: discord.Interaction):
    await interaction.response.send_message('This feature is not ready yet, come back later')
    return

me_dm = None
experimental = True
defcon = 1
queue = []
mods = 0
leaderboard = []
enabled = True
twitterfix = False
recent_snails_list = []
ban_list=[]
timesync_table = {}
client.run(my_secrets.AUTH)
