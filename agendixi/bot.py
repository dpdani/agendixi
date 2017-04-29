#!/usr/bin/python3


import time
import threading
import argparse
import getpass
import datetime
import telegram
from telegram.ext import Updater, CommandHandler
import sqlalchemy as sqlal
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


scheduled_events = []
threads = []
timers = []

subscribers = []


class Event(declarative_base()):
    __tablename__ = 'Events'
    ID = sqlal.Column(sqlal.Integer, primary_key=True)
    SendAt = sqlal.Column(sqlal.DateTime)
    Sent = sqlal.Column(sqlal.Boolean)
    Description = sqlal.Column(sqlal.String(255))
    
    def __repr__(self):
        return '<Event#{} {} {} "{}">'.format(self.ID, self.SendAt, 'sent' if self.Sent else 'to-be-sent', self.Description)


def db_connect(passwd):
    #                             mysql+pymysql://<username>:<password>@<host>/<dbname>
    engine = sqlal.create_engine('mysql+pymysql://agendixi:{}@localhost/agendixi'.format(passwd))
    Session = sessionmaker(autocommit=True)
    Session.configure(bind=engine)
    session = Session()
    return engine, session


def db_poll(session):
    while True:
        for event in session.query(Event).filter_by(Sent=False):
            if event.ID not in scheduled_events and event.Sent == False:
                schedule_message(event)
        time.sleep(2)


def schedule_message(event):
    scheduled_events.append(event.ID)
    timer = threading.Timer(
        (event.SendAt - datetime.datetime.now()).total_seconds(),
        send_event,
        args=(event,)
    )
    timer.start()
    print("Event scheduled: {}".format(event))
    timers.append(timer)


def send_event(event):
    message = "Event#{}\n{}".format(event.ID, event.Description)
    event.Sent = True
    for sub in subscribers:
        try:
            bot_updater.bot.send_message(chat_id=sub, text=message)
        except telegram.error.Unauthorized:
            print("User '{}' unsubscribed.".format(sub))
            subscribers.remove(sub)
    print("Message regarding event#{} was dispatched.".format(event.ID))


def bot_start(bot, update):
    update.message.reply_text('Hi bro!\nIf you wish to subscribe to this service, use the /sub command.')


def bot_subscribe(bot, update):
    chat_id = update.message.chat_id
    if chat_id not in subscribers:
        subscribers.append(chat_id)
        update.message.reply_text('You were correctly subscribed to the agendixi service.')
    else:
        update.message.reply_text('Luca puzza.')


with open('bot-token.txt', 'r') as f:
    for line in f:
        if line.startswith('#'):
            continue
        print(line.strip())
        bot_updater = Updater(line.strip())
        break

bot_updater.dispatcher.add_handler(CommandHandler('start', bot_start))
bot_updater.dispatcher.add_handler(CommandHandler('sub', bot_subscribe))

def bot_thread():
    bot_updater.start_polling()
    bot_updater.idle()


def main(args):
    try:
        password = getpass.getpass('Please enter database password for \'agendixi\': ')
    except KeyboardInterrupt:
        print('Bye!')
        return
    try:
        engine, session = db_connect(password)
        session.query(Event).first()
    except sqlal.exc.OperationalError:
        print('\nIncorrect password.')
        return
    with open('subscribers', 'r') as f:
        for line in f:
            if line.strip() != '':
                subscribers.append(line.strip())
    # bth = threading.Thread(target=bot_thread)
    # bth.start()
    # threads.append(bth)
    # while True:
    #     inp = input('$ ')
    #     if inp in ('q',):
    #         break
    #     exec(inp)
    print(bot_updater.bot)
    db_thread = threading.Thread(target=db_poll, args=(session,))
    db_thread.start()
    threads.append(db_thread)
    bot_thread()
    session.close()
    with open('subscribers', 'w') as f:
        for sub in subscribers:
            f.write(str(sub)+'\n')


def shutdown():
    bot_updater.stop()
    for ti in timers:
        ti.cancel()
    for th in threads:
        th.join()


if __name__ == '__main__':
    args = argparse.ArgumentParser('agendixi-bot')
    # args.add_argument()
    args = args.parse_args()
    main(args)
