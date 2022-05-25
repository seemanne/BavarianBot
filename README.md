# BavarianBot
Public version of a barebones discord bot based on discord.py, this repo is mainly used to push updates of the bot to the Raspberry Pi sitting on my desk.

# Current feature palette

**bavarianVerifier**

Checks any message containing a group ping and verifies whether the author is actually part of that group and gives a timeout if he isn't. Comes with an additional flair message for group members.

**checkSnail**

Holds a list of the unique id of the last 1000 tweets posted in channels and calls out a user for a repost. 

**cinephile** 

Uses regex to extract movie titles mentioned in the message and combines it with newspapers nlp methods to respond with a letterboxd review of said movie

**scholar**

Uses regex to extract authors and year of a paper mentioned in the message and then crawls google scholar to figure out the title and abstract of the paper

**wikiCrawl**

Uses a wikipedia-api to obtain the summary of the wikipedia article of a given term
