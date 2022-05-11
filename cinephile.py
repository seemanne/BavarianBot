import imp
import discord
import re
import wikipediaapi as wkpa
import newspaper

#INPUT: discord.Message
#OUTPUT: movie title as a string, None if there is no title
async def parseMovie(message: discord.Message):
    content = message.content
    movie_search = re.search('(([A-Z]+ )+)\(\d{4}\)', content)
    if(movie_search):
        movie = movie_search.group(1)
    else:
        return None
    print('done parsing')
    return movie


#INPUT: string containing movie title in all caps
#OUTPUT: string containing possible wikipedia url for the film
async def createWikistring(match: str):
    wikistring = match.replace(" ", "_")
    change = False
    for letter in wikistring:
        if (letter.isupper() and change):
            wikistring = wikistring.replace(letter, letter.lower())
        else:
            change = True
        if (letter == '_'):
            change = False 
    return wikistring

#INPUT: string containing movie title in all caps
#OUTPUT: string containing possible letterboxd url for the film
async def createLetterboxdstring(match: str):
    letterstring = match.replace(' ', "-")
    letterstring = letterstring.rstrip('-')
    letterstring = letterstring.lower()
    letterstring = 'https://letterboxd.com/film/' + letterstring + '/reviews/by/activity/'
    return letterstring



#teststring = "Ve RTigo CLOWN "
#wiki = wkpa.Wikipedia("en")
#page = wiki.page(teststring)
#boo = page.exists()
#print(createWikistring(teststring))
async def cinemaCheck(message: discord.Message):
    content = await parseMovie(message)
    if (not content):
        return
    url = await createLetterboxdstring(content)
    url_i = newspaper.Article(url="%s" % (url), language='en',fetch_images = False, memoize_articles = False, keep_article_html = True)
    url_i.download()
    url_i.parse()
    await message.channel.send(f'God I love that movie {message.author.display_name} but I think: ' + url_i.text)
    

