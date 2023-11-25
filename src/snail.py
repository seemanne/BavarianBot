import re
import datetime
import discord

import src.datastructures

def check_for_twitter_link(message: str):

    matchli = re.match(r"https://[a-zA-Z]*\.com/.*/status/(\d*)", message)
    if not matchli:
        return False, None
    tweet_id = matchli.group(1)
    return True, tweet_id

def snail_check(message: discord.Message, cache: src.datastructures.LRUCache):

    has_link, tweet_id = check_for_twitter_link(message.content)
    if not has_link:
        return False, None
    
    cached_item = cache.get(tweet_id)
    if not cached_item:
        cache.put(tweet_id, (message.author.name, datetime.datetime.utcnow()))
        return True, None
    
    return True, cached_item
    
    
    

    
    