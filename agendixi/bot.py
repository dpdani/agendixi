#!/usr/bin/python3


import threading
import argparse
import datetime
import telegram
import sqlalchemy as sqlal
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


scheduled_events = []
threads = []
timers = []


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
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    return engine, session


def db_poll():
    for event in session.query(Event).filter_by(Sent=False):
        if event.ID not in shceduled_events:
            schedule_message(event)
    t = threading.Timer(10, db_poll)  # polling time: 10 secs
    t.start()
    timers.append(t)


def schedule_message(event):
    scheduled_events.append(event.ID)
    timer = threading.Timer(
        (evt.SendAt - datetime.datetime.now()).total_seconds(),
        send_message,
        args=None
    )
    timer.start()
    timers.append(timer)


def main(args):
    password = input('Please enter database password for \'agendixi\': ')
    engine, session = db_connect(password)
    session.query(Event).first()
    while True:
        inp = input('$ ')
        if inp in ('q',):
            break
        exec(inp)
    session.close()


def shutdown():
    for th in threads:
        pass
    for ti in timers:
        ti.cancel()


if __name__ == '__main__':
    args = argparse.ArgumentParser('agendixi-bot')
    # args.add_argument()
    args = args.parse_args()
    main(args)

