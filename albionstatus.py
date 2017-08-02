#!/usr/bin/env python3.5 -u
import time
import json
import logging

import sys
import traceback

import twitter
import mysql.connector
import requests

api = None
config = None
db = None
albion_url = "http://live.albiononline.com/status.txt"
headers = {
    'User-Agent': 'AlbionStatus Bot @ albionstatus.com',
}
logger = logging.getLogger("albionstatus")
sleep_time = 60


def setup_logging():
    logger.setLevel(logging.INFO)

    # create a file handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(handler)


def load_config():
    global config
    with open("config.json", "r") as json_file:
        config = json.load(json_file)


def setup_api():
    global api
    api = twitter.Api(consumer_key=config['twitter']['consumer_key'],
                      consumer_secret=config['twitter']['consumer_secret'],
                      access_token_key=config['twitter']['access_token_key'],
                      access_token_secret=config['twitter']['access_token_secret'])


def setup_mysql():
    global db
    db = mysql.connector.connect(host=config['mysql']['host'],
                                 user=config['mysql']['user'],
                                 password=config['mysql']['password'],
                                 database=config['mysql']['database'])


def setup_everything():
    setup_logging()
    load_config()
    setup_api()
    setup_mysql()


def get_current_status():
    try:
        response = requests.get(albion_url, headers=headers)
        response.encoding = "utf-8"
        status = response.text
        status = status.replace('\n', ' ').replace("\r", '').replace('\ufeff', '')
        status = json.loads(status)
        status["current_status"] = status.pop("status")
        return status
    except:
        logger.log(logging.ERROR, "Couldn't fetch server status! Error:" + traceback.format_exc())
        return {"current_status": "online", "message": "All good.", "comment": "Could not fetch status."}


def get_last_status():
    sql = "SELECT current_status, message, comment FROM `status` ORDER BY id DESC LIMIT 1"
    cursor = db.cursor(buffered=True)
    cursor.execute(sql)
    db.commit()

    status, message, comment = cursor.fetchall()[0]
    cursor.close()
    # TODO Check if status object is correct
    return {"current_status": status, "message": message, "comment": comment}


def insert_new_status(status):
    sql = "INSERT INTO `status` (current_status, message) VALUES ( %(current_status)s , %(message)s)"
    cursor = db.cursor(buffered=True)
    cursor.execute(sql, status)
    db.commit()
    cursor.close()


def is_different(current_status, last_status):
    return not current_status["message"] == last_status["message"] or \
           not current_status["current_status"] == last_status["current_status"]


def run_albionstatus():
    current_status = get_current_status()
    last_status = get_last_status()

    insert_new_status(current_status)

    if is_different(current_status, last_status):
        logger.info("Server status changed! Tweeting now")
        msg = "Server status: {0}! Reason: {1}".format(current_status["current_status"], current_status["message"])
        if len(msg) > 140:
            msg = "Server status: {0}! Reason: Too long for that tweet, please check above!" \
                .format(current_status["current_status"])
            tweet(msg[:140])
            reason = "Reason: {0}...".format(current_status["message"][:129])
            tweet(reason)
        else:
            tweet(msg)
    else:
        logger.info("No change in server status!")


def tweet(msg):
    api.PostUpdate(msg)


if __name__ == "__main__":
    setup_everything()

    while True:
        run_albionstatus()
        logger.info("Sleep now for {} seconds".format(sleep_time))
        time.sleep(sleep_time)
