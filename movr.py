import boto3
import os
import requests
import shutil
from dotenv import load_dotenv

load_dotenv()

dynamodb = boto3.resource('dynamodb')
db = dynamodb.Table('downloadr')

# constants
DELUGE_API_URL = os.getenv('DELUGE_API_URL')
BOT_PASSWORD = os.getenv('BOT_PASSWORD')
PATH_TO_SORTING_BOX = os.getenv('PATH_TO_SORTING_BOX')
PATH_TO_MOVIES = os.getenv('PATH_TO_MOVIES')
# PATH_TO_TV = ''
# PATH_TO_AUDIOBOOK = ''
# PATH_TO_MUSIC = ''

def db_items():
    items = db.scan()['Items']
    return items

def update():
    for item in db_items():
        if 'name' not in item:
            id = item['id']
            url = DELUGE_API_URL + "/" + id
            r = requests.get(url, auth=('bot', BOT_PASSWORD))
            name = r.json()['name']
            db.update_item(Key={'id': id}, AttributeUpdates={'name': {'Value': name}})

def move():
    # list of downloads to process
    # drawn from db, added by downloadr
    downloads = db_items()

    with os.scandir(PATH_TO_SORTING_BOX) as scan:
        for item in scan:
            for download in downloads:
                if item.name in download['name']:
                    # do something
                    table_key = {'id': download['id']}
                    type = db.get_item(Key=table_key)['Item']['type']
                    if type == 'movie':
                        dl_source = PATH_TO_SORTING_BOX + '/' + item.name
                        shutil.move(dl_source, PATH_TO_MOVIES)
                        url = DELUGE_API_URL + '/' + download['id']
                        requests.delete(url, auth=('bot', BOT_PASSWORD))
                        db.delete_item(Key=table_key)

if __name__ == '__main__':
    update()
    move()
