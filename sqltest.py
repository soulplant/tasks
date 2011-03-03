from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Time, Text, DateTime, Boolean, Enum
from sqlalchemy.orm import sessionmaker, relationship, backref

import datetime
import sqlalchemy

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    finished_at = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime)
    status = Column(Enum("active", "inbox", "done"))

    def __init__(self, name):
        self.name = name
        self.created_at = datetime.datetime.now()
        self.status = "inbox"

    def add_url(self, url, name=None):
        self.urls.append(URL(url, name))

    def add_tomato(self, whole=True):
        self.tomatoes.append(Tomato(whole))

    def finish(self):
        self.finished_at = datetime.datetime.now()
        self.status = "done"

    def activate(self):
        self.status = "active"

    def deactivate(self):
        self.status = "inbox"

    def log(self, message):
        self.logs.append(LogEntry(message))

class URL(Base):
    __tablename__ = 'urls'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    task = relationship(Task, backref=backref('urls', order_by=id))
    url = Column(String)

    def __init__(self, url, name=None):
        self.url = url
        self.name = name

class LogEntry(Base):
    __tablename__ = 'log_entries'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    message = Column(String)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    task = relationship(Task, backref=backref('logs', order_by=created_at))

    def __init__(self, message):
        self.message = message
        self.created_at = datetime.datetime.now()

class Tomato(Base):
    __tablename__ = 'tomatoes'

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    task = relationship(Task, backref=backref('tomatoes', order_by=id))
    whole = Column(Boolean)
    finished_at = Column(DateTime)

    def __init__(self, whole=True):
        self.whole = whole
        self.finished_at = datetime.datetime.now()

engine = create_engine('sqlite:///test.db', echo=False)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


t = Task('do some stuff')
t.activate()
t.notes = 'hey there'
t.add_url('http://www.google.com', "Where to search for for stuff.")
t.add_url('http://www.yahoo.com', "Somewhere else to search.")
t.log("Broke the build.")
t.log("Mailed to Ojan.")
t.add_tomato()
t.add_tomato()
t.add_tomato()
t.add_tomato(False)
session.add(t)

session.commit()

t = session.query(Task).all()[0]
print "Finished tasks:"
for u in session.query(Task).filter_by(status='done'):
    print u
print "Tasks in the inbox:"
for u in session.query(Task).filter_by(status='inbox'):
    print u
print "Active tasks:"
for u in session.query(Task).filter_by(status='active'):
    print map(lambda u: u.name, u.urls)
