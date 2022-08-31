#import _json
from flask import json
from pathlib import Path
#edit blinkspeed in settings_template.json
def edit_blinkspeed(blinkspeed):


    with open('settings_template.json', 'r') as f:
        data = json.load(f)
    data['blinkspeed'] = blinkspeed
    with open('settings_template.json', 'w') as f:
        json.dump(data, f)
    return data['blinkspeed']

