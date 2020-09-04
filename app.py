#!/usr/bin/env python

from tg import expose, TGController, MinimalApplicationConfigurator
from tg.configurator.components.statics import StaticsConfigurationComponent
from tg.configurator.components.sqlalchemy import SQLAlchemyConfigurationComponent
from wsgiref.simple_server import make_server
from tg.util import Bunch
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, String
from datetime import datetime

import webhelpers2
import webhelpers2.text

DeclarativeBase = declarative_base()
DBSession = scoped_session(sessionmaker(autoflush=True, autocommit=False))

## Define a controller for the application
class RootController(TGController):
  @expose(content_type='text/plain')
  def index(self):
    logs = DBSession.query(Log).order_by(Log.timestamp.desc()).all()
    return 'Past Greetings\n' + '\n'.join(['%s - %s' % (l.timestamp, l.person) for l in logs])

  @expose('hello.xhtml')
  def hello(self, person=None):
    DBSession.add(Log(person=person or ''))
    DBSession.commit()
    return dict(person=person)


class Log(DeclarativeBase):
    __tablename__ = 'logs'

    uid = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    person = Column(String(50), nullable=False)

def init_model(engine):
    DBSession.configure(bind=engine)
    DeclarativeBase.metadata.create_all(engine)  # Create tables if they do not exist

## Create the application through the configurator
config = MinimalApplicationConfigurator()
config.register(StaticsConfigurationComponent)
config.register(SQLAlchemyConfigurationComponent)
config.update_blueprint({
  'root_controller': RootController(),
  'renderers': ['kajiki'],
  'helpers': webhelpers2,
  'serve_static': True,
    'paths': {
        'static_files': 'public'
    },
    'use_sqlalchemy': True,
    'sqlalchemy.url': 'sqlite:///devdata.db',
    'model': Bunch(
        DBSession=DBSession,
        init_model=init_model
    )
})
application = config.make_wsgi_app()

## Set up database




# config.update_blueprint({})


## Serve the application
print("Serving on port 8080...")
httpd = make_server('', 8080, application)
httpd.serve_forever()
