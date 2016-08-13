#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot thah look inside the database and see if the pokemon requested is appeared during the last scan
# This program is dedicated to the public domain under the CC0 license.
# First iteration made by eugenio412
# based on timerbot made inside python-telegram-bot example folder

# better on python3.4

#HOW TO RUN IT:
#launch pokemon go map, and scan an area
#generate a token for telegram bot contacting the bot father on telegram @botfather
#put it into the script at the place of TOKEN
#install python telegram bot: sudo pip3 install python-telegram-bot
#then run python3.4 telegrambot.py
#write to your bot on telegram

import datetime
import sqlite3 as lite
from telegram.ext import Updater, CommandHandler, Job
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
timers = dict()
sent = dict()
#read the database
con = lite.connect('pogom.db',check_same_thread=False)
cur = con.cursor()


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hello! write /set and the number of the pokemon to scan.\nexample for bulbasaur:\n/set 1')


def alarm(bot, job):
    with con:
        cur = con.cursor()
        pokemon = int(job.context[1])
        cur.execute("SELECT * FROM pokemon WHERE pokemon_id = ?",(pokemon,))
        rows = cur.fetchall()
        for row in rows:
            encounter_id = str(row[0])
            spaw_point = str(row[1])
            pok_id = str(row[2])
            latitude = str(row[3])
            longitude = str(row[4])
            disappear = str(row[5])
            link = "http://maps.google.com/maps?q=" + latitude + "," + longitude + "&ll=" + latitude + "," + longitude + "&z=17"
            text_message = "Pokemon number " + pok_id + \
            "\nDisappear at :" + disappear + "\n" + link + \
            "\n/unset to stop the scan"
            if encounter_id not in sent:
                sent[encounter_id] = (encounter_id,spaw_point,pok_id,latitude,longitude,disappear)
                """Function to send the message"""
                bot.sendMessage(job.context[0], text = text_message)


def set(bot, update, args, job_queue):
    """Adds a job to the queue"""
    chat_id = update.message.chat_id
    try:
        pokemon = args[0]
        # Add job to queue
        job = Job(alarm, 30, repeat=True, context=(chat_id,pokemon))
        timers[chat_id] = job
        job_queue.put(job)
        #but first, save the pokemon already appeared
        with con:
            cur = con.cursor()
            pokemon = int(job.context[1])
            cur.execute("SELECT * FROM pokemon WHERE pokemon_id = ?",(pokemon,))
            rows = cur.fetchall()
            for row in rows:
                encounter_id = str(row[0])
                spaw_point = str(row[1])
                pok_id = str(row[2])
                latitude = str(row[3])
                longitude = str(row[4])
                disappear = str(row[5])
                sent[encounter_id] = (encounter_id,spaw_point,pok_id,latitude,longitude,disappear)
        bot.sendMessage(chat_id, text='scanner on!')
    except (IndexError, ValueError):
        bot.sendMessage(chat_id, text='usage: /set <#pokemon>')



def unset(bot, update):
    """Removes the job if the user changed their mind"""
    chat_id = update.message.chat_id

    if chat_id not in timers:
        bot.sendMessage(chat_id, text='You have no active scanner')
        return

    job = timers[chat_id]
    job.schedule_removal()
    del timers[chat_id]

    bot.sendMessage(chat_id, text='scanner successfully unset!')


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    #ask it to the bot father in telegram
    updater = Updater("TOKEN")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("set", set, pass_args=True, pass_job_queue=True))
    dp.add_handler(CommandHandler("unset", unset))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
