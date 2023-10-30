import re
import newspaper
import discord
import asyncio

def parse_movie(message: discord.Message):
    content = message.content
    content = content.replace('\'', '')
    content = content.replace(',', '')
    content = content.replace('/', ' ')
    movie_search = re.search('(([A-Z|0-9]+ )+)\((\d{4})\)', content)
    if(movie_search):
        movie = movie_search.group(1)
        year = movie_search.group(3)
    else:
        return [False, False]
    return [movie, year]


def create_letterboxd_string(match: str, year: str):
    letterstring = match.replace(' ', "-")
    letterstring = letterstring.rstrip('-')
    letterstring = letterstring.lower()
    wiyear = 'https://letterboxd.com/film/' + letterstring + '-' + year + '/reviews/by/activity/'
    woyear = 'https://letterboxd.com/film/' + letterstring + '/reviews/by/activity/'
    widirectlink = 'https://letterboxd.com/film/' + letterstring + '-' + year
    wodirectlink = 'https://letterboxd.com/film/' + letterstring
    return [wiyear, woyear, widirectlink, wodirectlink]

def cinema_check(message: discord.Message):
    withyear = True
    content = parse_movie(message)
    if (not content[0]):
        return
    url = create_letterboxd_string(content[0], content[1])
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
        embed = discord.Embed(title = content[0] + content [1], url = url[2], description = wiarticle.text, color = discord.Color.blue())
    else:
        embed = discord.Embed(title = content[0], url = url[3], description = woarticle.text, color = discord.Color.blue())
    loop = asyncio.get_event_loop()
    loop.create_task(message.channel.send(embed = embed))
    return