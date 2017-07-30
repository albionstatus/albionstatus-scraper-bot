import json
from pprint import pprint

import twitter
import MySQLdb

api = None
config = None
db = None


# TODO Daemonize (every 60 sec)
# TODO Grab last status from MySQL
# TODO Read from online file and save to MySQL
# TODO Compare current and last status
# TODO Then tweet with current status, message and possible comment
# TODO When page not accessible: Add comment and use default all good status


def load_config():
    global config
    with open("config.json", "r") as json_file:
        config = json.load(json_file)
    pprint(config)


def setup_api():
    global api
    api = twitter.Api(consumer_key=config['twitter']['consumer_key'],
                      consumer_secret=config['twitter']['consumer_secret'],
                      access_token_key=config['twitter']['access_token_key'],
                      access_token_secret=config['twitter']['access_token_secret'])


def setup_mysql():
    global db
    db = MySQLdb.connect(config['mysql']['host'], config['mysql']['user'], config['mysql']['password'],
                         config['mysql']['database'])


def get_current_status():
    pass


def get_last_status():
    pass


def compareStatuses():
    pass


def insertNewStatus():
    pass


def tweet(msg):
    api.PostUpdate(msg)


def main():
    load_config()
    setup_api()
    setup_mysql()


if __name__ == "__main__":
    main()
