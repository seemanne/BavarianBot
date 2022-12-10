import discord
import pandas as pd
import random
import datetime

async def display_table(message: discord.Message, table: pd.DataFrame, title = 'Unnamed embed'):
    content = ''
    printlist = table.values.tolist()
    for entry in printlist:
        content += str(entry) + '\n'
    embed = discord.Embed(title = title, description= content )
    await message.channel.send(embed = embed)
    
async def messageCarousel(message: discord.Message, responses: list):
    rand = random.random()
    rand = rand * (len(responses) - 1)
    rand = round(rand)
    await message.channel.send(responses[rand])

async def dynamic_display_table(message: discord.Message, table: pd.DataFrame, title = 'Unnamed embed', **kwargs):
    """
    pass on a dict titled custom_format and print message with key starting with § indicating a table key and the others coming in plain text
    """
    content = ''
    printlist = table.values.tolist()
    if ('custom_format' in kwargs.keys()):
        for entry in printlist:
            for key, value in kwargs.custom_format:
                if key.startswith('§'):
                    content += entry[value] + ' '
                else: 
                    content += value
            content += '\n'
    else:
        for entry in printlist:
            content += str(entry) + '\n'
    embed = discord.Embed(title = title, description = content)
    try: 
        await message.channel.send(embed = embed)
    except Exception as e:
        await message.channel.send('Embed creation failed with error: ' + e)
    
def numeral_adverb(occurence_count: int):
    if occurence_count == 1: return 'once'
    if occurence_count == 2: return 'twice'
    return f'{occurence_count} times'

def get_time_in_fifa_format(nowtime: datetime.datetime):

    return str(nowtime.hour*60 + nowtime.minute) + ':' + str(nowtime.second)

