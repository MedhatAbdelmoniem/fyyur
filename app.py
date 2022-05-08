#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from re import A
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy.orm import backref
from forms import *
from flask_migrate import Migrate
from models import app,moment,db,migrate,Venue,artist_venue,Artist,Show

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  
  data = []
  getData = Venue.query.distinct(Venue.city)
  
  for venueCity in getData:
    venueCityData = []
    getVenue = Venue.query.filter_by(city=venueCity.city).all()
    for eachCity in getVenue:
      venueCityData.append({
      "id": eachCity.id,
      "name": eachCity.name,
      "num_upcoming_shows": len(eachCity.shows),
      })

    data.append({
      "city": venueCity.city,
      "state": venueCity.state,
      "venues": venueCityData
    })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  
  data = []
  search_term=request.form.get('search_term')
  test = db.session.query(Venue).filter(Venue.name.ilike('%' + search_term.lower() + '%')).all()
  for te in test:
    data.append({
      "id": te.id,
      "name": te.name,
      "num_upcoming_shows": len(te.shows),
    })
  
  response={
    "count": len(data),
    "data": data
  }
  
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  venueShow = Venue.query.get(venue_id)
  genres = venueShow.genres.split()


  past_shows = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time  < datetime.now()).all()
  upcoming_shows = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time > datetime.now()).all()
   #changing date to string
  for show in past_shows:
    show.start_time =  str(show.start_time)
  for show in upcoming_shows:
    show.start_time =  str(show.start_time)


  data={
    "id": venue_id,
    "name": venueShow.name,
    "genres": genres,
    "address": venueShow.address,
    "city": venueShow.city,
    "state": venueShow.state,
    "phone": venueShow.phone,
    "website": venueShow.website,
    "facebook_link": venueShow.facebook_link,
    "seeking_talent": venueShow.seek,
    "seeking_description": venueShow.seek_description,
    "image_link": venueShow.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
 
  try:
    seekTalent = False
    if(request.form.get("seeking_talent") == 'y'):
      seekTalent = True
    else:
      seekTalent = False
    #getting the list
    genres = request.form.getlist('genres')
    #joining all the list into one string separated by space for splitting later
    genresList = ' '.join(genres)
    venueData = Venue(name=request.form['name'],website=request.form['website_link'],city=request.form['city'],genres= genresList,state = request.form['state'],address=request.form['address'],phone=request.form['phone'],image_link=request.form['image_link'],facebook_link=request.form['facebook_link'],seek=seekTalent,seek_description=request.form['seeking_description'])
    db.session.add(venueData) 
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
 
  except():
    db.session.rollback()
    flash('error!!, listing was unsuccessful!')
  finally:
      db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    deleteV =  Venue.query.get(venue_id)
    db.session.delete(deleteV)
    db.session.commit()
  except():
    db.session.rollback()
  finally:
    db.session.close()
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  data=Artist.query.with_entities(Artist.id,Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  data = []
  search_term=request.form.get('search_term')
  test = db.session.query(Artist).filter(Artist.name.ilike('%' + search_term.lower() + '%')).all()
  for te in test:
    data.append({
      "id": te.id,
      "name": te.name,
      "num_upcoming_shows": len(te.shows),
    })
  
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
 
  artistShow = Artist.query.get(artist_id)
  genres = artistShow.genres.split()
 

  past_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time < datetime.now()).all()
  upcoming_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time > datetime.now()).all()
  #changing date to string
  for show in past_shows:
    show.start_time =  str(show.start_time)
  for show in upcoming_shows:
    show.start_time =  str(show.start_time)

  data={
    "id": artist_id,
    "name": artistShow.name,
    "genres": genres,
    "city": artistShow.city,
    "state": artistShow.state,
    "phone": artistShow.phone,
    "website": artistShow.website,
    "facebook_link": artistShow.facebook_link,
    "seeking_venue": artistShow.seek,
    "seeking_description": artistShow.seek_description,
    "image_link": artistShow.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  genres=artist.genres.split()
  seek = ''
  if artist.seek == True:
    seek='y'
  form = ArtistForm(name=artist.name,genres=genres,city=artist.city,state=artist.state,phone=artist.phone,website_link=artist.website,facebook_link=artist.facebook_link,image_link=artist.image_link,seeking_description=artist.seek_description,seeking_venue=seek)
  artist={
    "id": artist_id,
    "name": artist.name,
    "genres": genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seek,
    "seeking_description": artist.seek_description,
    "image_link": artist.image_link
  }
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    seekvenue = False
    if(request.form.get("seeking_venue") == 'y'):
      seekvenue = True
    else:
      seekvenue = False
    artist = Artist.query.get(artist_id)
    #getting the list
    genres = request.form.getlist('genres')
    #joining all the list into one string separated by space for splitting later
    genresList = ' '.join(genres)
    artist.name = request.form['name']
    artist.city=request.form['city']
    artist.genres= genresList
    artist.state = request.form['state']
    artist.phone=request.form['phone']
    artist.website=request.form['website_link']
    artist.image_link=request.form['image_link']
    artist.facebook_link=request.form['facebook_link']
    artist.seek = seekvenue
    artist.seek_description=request.form['seeking_description']
    db.session.commit()
  except():
    db.session.rollback()
  finally:
      db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue= Venue.query.get(venue_id)
  genres=venue.genres.split()
  seek = ''
  if venue.seek == True:
    seek='y'
  form = VenueForm(name=venue.name,genres=genres,address=venue.address,city=venue.city,state=venue.state,phone=venue.phone,website_link=venue.website,facebook_link=venue.facebook_link,image_link=venue.image_link,seeking_description=venue.seek_description,seeking_talent=seek)
  venue={
    "id": venue_id,
    "name": venue.name,
    "genres": genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seek,
    "seeking_description": venue.seek_description,
    "image_link": venue.image_link
  }

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  
  try:
    seek = False
    if(request.form.get("seeking_talent") == 'y'):
      seek = True
    else:
      seek = False
    venue = Venue.query.get(venue_id)
    #getting the list
    genres = request.form.getlist('genres')
    #joining all the list into one string separated by space for splitting later
    genresList = ' '.join(genres)
    venue.name = request.form['name']
    venue.city=request.form['city']
    venue.genres= genresList
    venue.state = request.form['state']
    venue.address=request.form['address']
    venue.phone=request.form['phone']
    venue.website=request.form['website_link']
    venue.image_link=request.form['image_link']
    venue.facebook_link=request.form['facebook_link']
    venue.seek = seek
    venue.seek_description=request.form['seeking_description']
    db.session.commit()
  except():
    db.session.rollback()
  finally:
      db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form

  try:
    seekvenue = False
    if(request.form.get("seeking_venue") == 'y'):
      seekvenue = True
    else:
      seekvenue = False
    #getting the list
    genres = request.form.getlist('genres')
    #joining all the list into one string separated by space for splitting later
    genresList = ' '.join(genres)
    ArtistData = Artist(name=request.form['name'],city=request.form['city'],genres= genresList,state = request.form['state'],phone=request.form['phone'],website=request.form['website_link'],image_link=request.form['image_link'],facebook_link=request.form['facebook_link'],seek=seekvenue,seek_description=request.form['seeking_description'])
    db.session.add(ArtistData) 
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except():
    db.session.rollback()
    flash('error!!, listing was unsuccessful!')
  finally:
      db.session.close()

  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
 
  data = []
  shows = Show.query.all()
  for show in shows:
    data.append({
    "venue_id": show.venue_id,
    "venue_name": Venue.query.get(show.venue_id).name,
    "artist_id": show.artist_id,
    "artist_name": Artist.query.get(show.artist_id).name,
    "artist_image_link": Artist.query.get(show.artist_id).image_link,
    "start_time": str(show.start_time)
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  try:
    
    ShowData = Show(venue_id=request.form['venue_id'],artist_id=request.form['artist_id'],start_time=request.form['start_time'])
    db.session.add(ShowData) 
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except():
    db.session.rollback()
    flash('error!!, listing was unsuccessful!')
  finally:
      db.session.close()

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
