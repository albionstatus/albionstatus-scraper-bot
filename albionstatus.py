#!/usr/bin/env python3.5 -u
import time
import json
import logging

import sys
import traceback

import datetime
import twitter
import mysql.connector
import requests

api = None
config = None
db = None
albion_url = "http://serverstatus.albiononline.com:9099/"
headers = {
    'User-Agent': 'AlbionStatus Bot @ albionstatus.com',
}
logger = logging.getLogger("albionstatus")
sleep_time = 60
failing_status = {"current_status": "online", "message": "All good.", "comment": "Could not fetch status."}


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


def parse_status(status):
    # Parse weird status messages
    return {
        '500': "offline",
    }.get(status, status)


def parse_message(message):
    # Parse weird messages
    message = message.lower()
    timeout = "Timeout - is a DDOS ongoing?"
    return {
        'connect timed out': timeout,
        'read timed out': timeout,
    }.get(message, message)


def get_current_status():
    try:
        response = requests.get(albion_url, headers=headers)
        response.encoding = "utf-8"
        status = response.text
        status = status.replace('\n', ' ').replace("\r", '').replace('\ufeff', '')
        status = json.loads(status)
        status["current_status"] = parse_status(status.pop("status"))
        status["message"] = parse_message(status["message"])

        return status
    except:
        logger.log(logging.ERROR, "Couldn't fetch server status! Error:" + traceback.format_exc())
        return failing_status


def get_last_status():
    sql = "SELECT current_status, message, comment FROM `status` ORDER BY id DESC LIMIT 1"
    cursor = db.cursor(buffered=True)
    cursor.execute(sql)
    db.commit()

    try:
        status, message, comment = cursor.fetchall()[0]
        cursor.close()
        return {"current_status": status, "message": message, "comment": comment}
    except:
        cursor.close()
        logger.log(logging.ERROR, "Couldn't fetch status from DB! Error:" + traceback.format_exc())
        return failing_status
        # TODO Check if status object is correct


def insert_new_status(status):
    sql = "INSERT INTO `status` (current_status, message) VALUES ( %(current_status)s , %(message)s)"
    cursor = db.cursor(buffered=True)
    cursor.execute(sql, status)
    db.commit()
    cursor.close()


def is_different(current_status, last_status):
    return not current_status["current_status"] == last_status["current_status"] or \
           not current_status["message"] == last_status["message"]


def run_albionstatus():
    current_status = get_current_status()
    last_status = get_last_status()

    insert_new_status(current_status)

    if is_different(current_status, last_status):
        logger.info("Server status changed from {0} to {1}! Tweeting now"
                    .format(current_status["current_status"], last_status["current_status"]))
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
    try:
        api.PostUpdate(msg)
    except:
        logger.log(logging.ERROR, "Couldn't tweet! Error:" + traceback.format_exc())
        logger.log(logging.INFO, "Try again!")
        if len(msg) < 140:
            utc_datetime = datetime.datetime.utcnow()
            time = utc_datetime.strftime("%H:%M:%S")
            msg = msg + " | Time: " + time
            try:
                api.PostUpdate(msg[:140])
            except:
                logger.log(logging.ERROR, "Couldn't tweet again Stop trying! Error:" + traceback.format_exc())


if __name__ == "__main__":
    setup_everything()

    while True:
        run_albionstatus()
        logger.info("Sleep now for {} seconds".format(sleep_time))
        time.sleep(sleep_time)
