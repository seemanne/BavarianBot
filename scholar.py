#testcase: 'A Time-Series Model of Interest Rates with the Effective Lower Bound'
#INPUT: Clown, Gammbus et al. (2020)
#OUTPUT: Abstract and Title

#print(author['publications'][0].get('bib').get('author')) : Steven A Cholewiak and Kwangtaek Kim and Hong Z Tan and Bernard D Adelstein

#INPUT
year = 2018
inputauthor = 'Clown'
coauthor = 'Hoffmann'

from scholarly import scholarly
import discord
import re


#OUPUT: tuple containing title and abstract of paper if it exists
async def getAbstract(author: str, coauthor: str, year: str):
    title , abstract = None, None
    search_query = scholarly.search_author('Vincent Kusters')
    author = scholarly.fill(next(search_query))
    pub = author['publications'][0]
    for pub in author['publications']:
        if (pub['bib']['pub_year'] == year):
            pub = scholarly.fill(pub)
            if (pub['bib']['author'].__contains__(coauthor)):
                abstract = pub['bib']['abstract']
                title = pub['bib']['title']
                break
    return (title, abstract)

#input: discord message in the format €paper author (year)
#output: [author, coauthor, year]
async def sanitizeInput(message: discord.Message):
    input = re.search('(\w*) & (\w*) \((\d{4}\))', message.content)
    author = input.group(1)
    coauthor = input.group(2)
    year = input.group(3)
    if(not input):
        input = re.search('(\w*) et al. \((\d{4}\))', message.content)
        author = input.group(1)
        coauthor = 'et al.'
        year = input.group(2)
    if(not input):
        input = re.search('(\w*) \((\d{4}\))', message.content)
        author = input.group(1)
        coauthor = None
        year = input.group(2)
    else:
        return None
    return [author, coauthor, year]

async def scholar(message: discord.Message):
    inputs = await sanitizeInput(message)
    if(inputs):
        outputs = await getAbstract(inputs[0], inputs[1], inputs[2])
    if(outputs):
        await message.channel.send(outputs(0) + '\n' + outputs(1))

embed=discord.Embed(title="peepeepoopoo", url="https://peepee.poopoo.com/", description="This is an embed that will peepeepoopoo", color=discord.Color.blue())


clown = 'peepee & poopoo (6942)'
input = re.search('(\w*) & (\w*) \((\d{4})\)', clown)
print(input.group(3))