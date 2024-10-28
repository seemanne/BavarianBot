import re
import sqlalchemy
import discord
from sqlalchemy import select, desc, insert, update
from sqlalchemy.sql import func, text
from src.orm import Tag, Config, FishResult, SnailBet


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
        query = sqlalchemy.insert(Tag).values(
            num=id,
            name=tag_data["name"],
            description=tag_data["description"],
            content=tag_data["image_link"],
        )
        conn.execute(query)
        conn.commit()


def list_tags(tag_name: str, engine: sqlalchemy.Engine):
    message = ""
    with engine.connect() as conn:
        query = select(Tag.num, Tag.description).where(Tag.name == tag_name)
        for row in conn.execute(query):
            message += f"{row[0]} | {row[1]}\n"
    return discord.Embed(
        title=f'Found the following tags for "{tag_name}":', description=message.strip()
    )


def list_all_tags(engine: sqlalchemy.Engine):
    message = ""
    with engine.connect() as conn:
        query = (
            select(Tag.name, func.count("*").label("count"))
            .group_by(Tag.name)
            .order_by(desc(text("count")))
        )
        for row in conn.execute(query):
            message += f"'{row[0]}' : {row[1]} tags\n"
    return discord.Embed(title="Available tags", description=message.strip())


def get_tag(content: str, engine: sqlalchemy.Engine):
    matchli = re.search(r"(.*) (\d*)", content)
    if matchli:
        with engine.connect() as conn:
            query = select(Tag.content).where(
                Tag.name == matchli.group(1), Tag.num == matchli.group(2)
            )
            res = conn.execute(query).first()
            if res:
                return res[0]
            return f"Failed to find tag with name: {matchli.group(1)}, id: {matchli.group(2)}"
    return f"Sorry, I couldn't parse this query. If this is a bug use /feedback"


def get_config(key: str, engine: sqlalchemy.Engine):
    with engine.connect() as conn:
        query = select(Config.value).where(Config.key == key)
        res = conn.execute(query).first()

        if not res:
            return None
        return res[0]


def set_config(key: str, value: str, engine: sqlalchemy.Engine):
    with engine.connect() as conn:
        query = select(Config).where(Config.key == key)
        existing_record = conn.execute(query).first()
        if existing_record:
            query = update(Config).values(value=value).where(Config.key == key)
        else:
            query = insert(Config).values(key=key, value=value)
        conn.execute(query)
        conn.commit()


def load_full_config(engine: sqlalchemy.Engine):
    with engine.connect() as conn:
        query = select(Config.key, Config.value)
        res = conn.execute(query).all()

    ret_dict = {k: v for k, v in res}
    return ret_dict


def save_fish(
    user_name: str, fish_weight: int, fish_fed: int, engine: sqlalchemy.Engine
):
    with engine.connect() as conn:
        query = insert(FishResult).values(
            user_name=user_name, fish_weight=fish_weight, fish_fed=fish_fed
        )
        conn.execute(query)
        conn.commit()


def get_all_catches_by_username(user_name: str, engine: sqlalchemy.Engine):
    with engine.connect() as conn:
        query = (
            select(FishResult.id, FishResult.fish_weight, FishResult.caught_at)
            .where(FishResult.user_name == user_name)
            .order_by(desc(FishResult.id))
        )
        res = conn.execute(query).all()

    ret = {}
    count = 0
    for _, weight, caught_at in res:
        ret[str(count)] = (weight, str(caught_at))
        count += 1

    return ret


def bulk_insert_snail_votes(snail_list: list[SnailBet], engine: sqlalchemy.Engine):

    with engine.connect() as conn:
        query = (
            insert(SnailBet).values(
                [bet.to_dict_for_insert() for bet in snail_list]
            )
        )
        conn.execute(query)
        conn.commit()