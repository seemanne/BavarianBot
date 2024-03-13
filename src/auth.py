import os

AUTH = os.environ.get("AUTH")
DEV = os.environ.get("DEV", None) is not None
WEBHOOK = os.environ.get("WEBHOOK")
