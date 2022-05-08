from re import A
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy.orm import backref
from forms import *
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost:5432/fyyur'

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

artist_venue = db.Table('artist_venue',
    db.Column('Venue', db.Integer, db.ForeignKey('Venue.id'), primary_key=True),
    db.Column('Artist', db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seek = db.Column(db.Boolean, nullable=False)
    seek_description = db.Column(db.String())
    shows = db.relationship('Show',backref='venue')


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seek = db.Column(db.Boolean, nullable=False)
    seek_description = db.Column(db.String())
    shows = db.relationship('Show',backref='artist')
    venue = db.relationship('Venue', secondary=artist_venue,
      backref=db.backref('artists'))



#active is for if the show is still going to play or have been played and finished

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime,nullable=False)
  active = db.Column(db.Boolean, nullable=False,default=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'),nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'),nullable=False)
