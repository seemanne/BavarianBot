import discord
import random

async def vibeCheck(message: discord.Message, mods: str):
    if(not message.content.startswith('vibecheck')):
        return
    rand = random.randint(0, 100)
    for role in message.author.roles:
        if role.name == mods:
            rand = round(rand/4)
    if (rand < 27):
        flavortext = ' Yikes!'
    if (rand > 27):
        flavortext = ' (and thats ok)'
    if (rand > 50):
        flavortext = ' Thats an above average vibe!'
    if (rand == 69):
        flavortext = ' Nice!'
    if (rand > 69):
        flavortext = ' WOWZERS what a vibe'
    if (rand > 99):
        flavortext = ' Your vibe is so high John will have to poast babbies'

    await message.channel.send(f'{message.author.display_name} your vibe is at ' + str(rand) + '%!' + flavortext)