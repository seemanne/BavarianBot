# BavarianBot
Public version of a barebones discord bot based on discord.py, this repo is mainly used to push updates of the bot to the Raspberry Pi sitting on my desk (and also so fellow users can contribute patches for bugs that annoy them) (thanks @lyingbain)

# Current feature palette

**checkSnail**

Holds a list of the unique id of the last 1000 tweets posted in channels and calls out a user for a repost. 

**cinephile** 

Uses regex to extract movie titles mentioned in the message (using the criterion collection format, i.e. <TITLE> (\<year of release\>) ) and combines it with newspapers nlp methods to respond with a letterboxd review of said movie

**fishing**

Small game where users can call `/fish` to start fishing which will after a random time spawn a fish that they can catch using `/reel`. The pond is stateful, fish that aren't caught are fed and returned to the pond. 

**tagging (WIP)**

Provides a more advanced version of dynos `!tag` command backed by the attached database. Supports description and automatic numbering of tags and a more exhaustive creation process.

# Deployment

Deployment is containerized and can be done using rootless podman (docker should work out-of-the-box but I don't test for it)
The container needs to be given the following environment variables to work:
```
AUTH=<your discord bot auth token>
```
Optionally a `WEBHOOK` can be provided for the `/feedback` command and one can specify `DEV=1` to turn on dev mode.

Note that starting the container does not start the bot directly, it only sets up the management api. For a first run one needs to call this api to set up the sqllite with the right schema and start the bot.

```
# set up sqlite and bot
curl -X 'GET' \
  'http://localhost:8000/service/init_db' \
  -H 'accept: application/json'

# connect bot to discord API
curl -X 'PUT' \
  'http://localhost:8000/service/start' \
  -H 'accept: application/json'

# start acting on events
curl -X 'PUT' \
  'http://localhost:8000/client/activate' \
  -H 'accept: application/json'
```

The repo provides both a compose file for a basic configuration and deploy scripts in the deploy folder, so best start from there.

# Development

Some notes:

* There is an extensive testing framework that allows running tests on fake api objects and I try to keep coverage in an ok spot. CI will run tests and check for `ruff format`. 
* Try to keep the Client in `client.py` at least somewhat free of application logic. This makes it easier to test and the code is easier to maintain
* Any persistent state should be put into the attached sqlite db
* The management API allows debugging the internal state while the bot is running, use it if tests aren't helping with debugging
* I'm always here to help, just ping me