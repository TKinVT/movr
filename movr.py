import boto3
import os
import shutil

dynamodb = boto3.resource('dynamodb')
db = dynamodb.Table('downloadr')

PATH_TO_SORTING_BOX = '/path/to/ExtMedia/Sorting_Box'
PATH_TO_MOVIES = '/path/to/ExtMedia/Movies'
# PATH_TO_TV = ''
# PATH_TO_AUDIOBOOK = ''
# PATH_TO_MUSIC = ''

def move():
    # list of downloads to process
    # drawn from db, added by downloadr
    downloads = [download['name'] for download in db.scan()['Items']]

    with os.scandir(PATH_TO_SORTING_BOX) as scan:
        for item in scan:
            if item.name in downloads:
                # do something
                table_key = {'name': item.name}
                type = db.get_item(Key=table_key)['Item']['type']
                if type == 'movie':
                    dl_source = PATH_TO_SORTING_BOX + '/{}'.format(item.name)
                    print(dl_source)
                    shutil.move(dl_source, PATH_TO_MOVIES)
                    db.delete_item(Key=table_key)

if __name__ == '__main__':
    move()
