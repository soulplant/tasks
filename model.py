from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Time, Text, DateTime, Boolean, Enum
from sqlalchemy.orm import sessionmaker, relationship, backref

import datetime
import os
import sqlalchemy

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    finished_at = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime)
    status = Column(Enum("active", "inbox", "done", "blocked"))
    active_order = Column(Integer)

    def __init__(self, name):
        self.name = name
        self.created_at = datetime.datetime.now()
        self.status = "inbox"
        self.active_order = 0

    def _set_status(self, status):
        if status == self.status:
            return
        self.log("Status changed from %s to %s." % (self.status, status))
        self.status = status

    def add_url(self, url, name=None):
        self.urls.append(URL(url, name))

    def add_tomato(self, whole=True):
        self.tomatoes.append(Tomato(whole))

    def done(self):
        self.finished_at = datetime.datetime.now()
        self._set_status("done")
        self.active_order = 0

    def activate(self):
        self._set_status("active")
        self.active_order = 0

    def deactivate(self):
        self.inbox()

    def inbox(self):
        self._set_status("inbox")
        self.active_order = 0

    def block(self, reason):
        self._set_status("blocked")
        self.log("Blocked: %s" % reason)

    def log(self, message):
        self.logs.append(LogEntry(message))

    def show_progress(self):
        print "=== %s" % self.name
        tomato_str = ""
        for t in self.tomatoes:
            tomato_str += t.char()
        print tomato_str

    def set_active_order(self, active_order):
        self.active_order = active_order

    def show_status_line(self):
        print "%3d %s" % (self.id, self.name)

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

    def char(self):
        if self.whole:
            return 'X'
        return '-'

engine = create_engine('sqlite:///%s/.tasks.db' % os.environ['HOME'], echo=False)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
