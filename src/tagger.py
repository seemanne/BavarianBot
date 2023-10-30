import asyncio
import re
import discord

PRIVILEGED_WORDS = set(["help", "add", "list", "alter", "delete", "tidy"])

class TagCreationFlow:

    def __init__(self, message: discord.Message) -> None:

        self.owner_id = message.author.id
        self.owner_mention = message.author.mention
        self.next_creation_step = self.step_1
        self.loop = asyncio.get_event_loop()
        self.data = {}
        self.status = 0

        self.loop.create_task(message.reply("Starting interactive tag creation. You can cancel anytime using $cancel. \nPlease send a message containing the link to the image."))

    def next_step(self, message: discord.Message):

        if message.content.startswith("$cancel"):

            self.loop.create_task(message.reply("Aborting tag creation flow"))
            return -1
        
        status, result = self.next_creation_step(message)
        
        if status:
            ret_message = result
        else:
            ret_message = f"Tag creation step failed with: {result}"
        
        self.loop.create_task(message.reply(ret_message))

        return self.status

    
    def step_1(self, message: discord.Message):

        self.data["image_link"] = message.content.strip()
        self.next_creation_step = self.step_2
        return True, "Next, send the name (not id) you want the tag to fall under i.e. maggus and not maggus69"

    def step_2(self, message: discord.Message):

        if message.content.strip() in PRIVILEGED_WORDS:
            return False, "Banned tag name"
        self.data["name"] = message.content.strip()
        self.next_creation_step = self.step_3
        return True, "Next, enter a short description of the tag to make it easier to find"
    
    def step_3(self, message: discord.Message):

        self.data["description"] = message.content.strip()
        self.next_creation_step = None
        self.status = 1
        return True, "Tag creation successful"
    
def parse_tag_command(string: str):

    matchli = re.search("\$tag (\w*)", string)
    if matchli:
        return matchli.group(1)
    
    return None

def help(message: discord.Message):

    text = """
The following commands are supported:
$tag help - show this message
$tag add - start the interactive tag addition process
$tag list <name> - list all tags corresponding to this name
$tag alter - start the interactive tag alteration process
$tag delete <name> <id> - delete a given tag
$tag <name> <id> - display a given tag"""
    asyncio.get_event_loop().create_task(message.reply(text))
    return