import json
import os

print(os.getcwd())

with open('setup.json') as fp:
    SETUP = json.load(fp)
