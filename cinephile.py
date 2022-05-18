import discord
import re
import wikipediaapi as wkpa
import newspaper
import random

#INPUT: discord.Message
#OUTPUT: movie title as a string and year as string, None if there is no title
async def parseMovie(message: discord.Message):
    content = message.content
    content = content.replace('\'', '')
    movie_search = re.search('(([A-Z|0-9]+ )+)\((\d{4})\)', content)
    if(movie_search):
        movie = movie_search.group(1)
        year = movie_search.group(3)
    else:
        return [False, False]
    print('done parsing')
    return [movie, year]


#INPUT: string containing wikipedia title
#OUTPUT: string containing possible wikipedia url for the title
def createWikistring(match: str):
    wikistring = match.replace(" ", "_")
    big = True
    for letter in wikistring:
        if (big):
            wikistring = wikistring.replace(letter, letter.upper())
            big = False
        else:
            wikistring = wikistring.replace(letter, letter.lower())
        if (letter == '_'):
            big = True
    return wikistring

#INPUT: string containing movie title in all caps
#OUTPUT: string containing possible letterboxd url for the film
async def createLetterboxdstring(match: str, year: str):
    letterstring = match.replace(' ', "-")
    letterstring = letterstring.rstrip('-')
    letterstring = letterstring.lower()
    wiyear = 'https://letterboxd.com/film/' + letterstring + '-' + year + '/reviews/by/activity/'
    woyear = 'https://letterboxd.com/film/' + letterstring + '/reviews/by/activity/'
    return [wiyear, woyear]



teststring = "mArkus södEr"
string = createWikistring(teststring)

#wiki = wkpa.Wikipedia("en")
#page = wiki.page(teststring)
#boo = page.exists()
#print(createWikistring(teststring))
async def cinemaCheck(message: discord.Message):
    withyear = True
    content = await parseMovie(message)
    print(content)
    if (not content[0]):
        return
    url = await createLetterboxdstring(content[0], content[1])
    print(url)
    wiarticle = newspaper.Article(url[0], language='en',fetch_images = False, memoize_articles = False, keep_article_html = True)
    woarticle = newspaper.Article(url[1], language='en',fetch_images = False, memoize_articles = False, keep_article_html = True)
    wiarticle.download()
    woarticle.download()
    try: 
        wiarticle.parse()
    except:
        woarticle.parse()
        withyear = False
    if (withyear):
        embed = discord.Embed(title = content[0] + content [1], url = url[0].rstrip('/reviews/by/activity/'), description = wiarticle.text, color = discord.Color.blue())
    else:
        embed = discord.Embed(title = content[0] + content [1], url = url[1].rstrip('/reviews/by/activity/'), description = woarticle.text, color = discord.Color.blue())
    rand = random.random()
    #hardcoded rng for account holder
    if(message.author.id == 143379423494799360):
        rand = 0
    if(rand < 0.3):
        await message.channel.send(embed = embed)
    
async def wikiCrawl(message: discord.Message):
    content = message.content
    if(not content.startswith('£wiki')):
        return
    wiki = wkpa.Wikipedia("en")
    content = content.lstrip('£wiki ')
    url = createWikistring(content)
    page = wiki.page(url)
    boo = page.exists()
    if (boo):
        await message.channel.send(page.summary)
    print(url)