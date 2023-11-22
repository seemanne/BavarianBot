import re
import sqlalchemy
import discord
from sqlalchemy import select, desc
from sqlalchemy.sql import func, text
from src.orm import Tag, Config

def add_tag(tag_data: dict, engine: sqlalchemy.Engine):

    with engine.connect() as conn:
        query = select(func.max(Tag.num)).where(Tag.name == tag_data["name"])
        res = conn.execute(query)
        id = res.first()[0]

        if not id:
            id = 0
        else:
            id = int(id)
        id = id + 1
        query = sqlalchemy.insert(Tag).values(num=id, name=tag_data["name"], description=tag_data["description"], content=tag_data["image_link"])
        conn.execute(query)
        conn.commit()

def list_tags(tag_name: str, engine: sqlalchemy.Engine):

    message = ""
    with engine.connect() as conn:

        query = select(Tag.num, Tag.description).where(Tag.name == tag_name)
        for row in conn.execute(query):
            message += f"{row[0]} | {row[1]}\n"
    return discord.Embed(title=f'Found the following tags for "{tag_name}":', description=message)

def list_all_tags(engine: sqlalchemy.Engine):

    message = ""
    with engine.connect() as conn:

        query = select(Tag.name, func.count("*").label("count")).group_by(Tag.name).order_by(desc(text("count")))
        for row in conn.execute(query):
            message += f"'{row[0]}' : {row[1]} tags\n"
    return discord.Embed(title="Available tags", description=message)

def get_tag(content: str, engine: sqlalchemy.Engine):

    matchli = re.search(r"(.*) (\d*)", content)
    if matchli:
        with engine.connect() as conn:

            query = select(Tag.content).where(Tag.name == matchli.group(1), Tag.num == matchli.group(2))
            res = conn.execute(query).first()[0]
            return res
    
    return f"Failed to find tag with name: {matchli.group(1)}, id: {matchli.group(2)}"