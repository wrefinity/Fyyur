#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
# Python -m venv ./venv
# .\venv\Scripts\activate
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import date, timedelta


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from models import *
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
db.create_all()

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

# Done
@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.with_entities(
    func.count(Venue.id), Venue.city, Venue.state
    ).group_by(Venue.city, Venue.state).all()
  
  data = []
  for venue in venues:
      city_venue = Venue.query.filter_by(state=venue.state).filter_by(city=venue.city).all()
      v_info = []
      for v in city_venue:
          v_info.append({
              "id": v.id,
              "name": v.name,
              "num_upcoming_shows": len(Show.query.filter(Show.venue_id == v.id).filter(datetime.now() < Show.start_time).all())
          })
      data.append({
          "city": venue.city,
          "state": venue.state,
          "venues": v_info
      })

  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  
  return render_template('pages/venues.html', areas=data)

# Done
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  response = {}
  query = request.form.get('search_term', '')
  search_query = f"%{query}%"
  result = Venue.query.filter(Venue.name.ilike(search_query)).all()

  data = []
  for res in result:
    data.append({
      "id": res.id,
      "name": res.name,
      "num_upcoming_shows": len(Show.query.filter(Show.venue_id == res.id).filter(datetime.now() < Show.start_time).all())
    })

  response['count'] = len(result)
  response['data'] =  result

  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
   
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

# Done
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  # venue =Venue.query.join(Show).filter(Venue.id == Show.id).all() 
  # venues = Venue.join(Artist, )

  venue = Venue.query.filter_by(id=venue_id).first()
  prev_shows = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()
  coming_shows = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()

  past_show = upcoming_shows = []
  for s in prev_shows:
    past_show.append({
        'artist_id': s.artist_id,
        'artist_name': s.artist.name,
        'artist_image_link': s.artist.image_link,
        "start_time": s.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  
  for s in coming_shows:
    upcoming_shows.append({
        'artist_id': s.artist_id,
        'artist_name': s.artist.name,
        'artist_image_link': s.artist.image_link,
        "start_time": s.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  
  data = {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres.split(","),
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_show,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_show),
      "upcoming_shows_count": len(upcoming_shows)
  }

  if not data:
    return render_template('errors/404.html')

 
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

# Done
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

# Done
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():  
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  err = False
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    genres = request.form.getlist('genres'),
    image_link = request.form.get('image_link')
    facebook_link = request.form.get('facebook_link')
    website_link = request.form.get('website_link')
    seeking_talent = True if 'seeking_talent' in request.form else False 
    seeking_description = request.form.get('seeking_description')
    print(genres[0])
    venue_entry = Venue(
      name=name, 
      city=city, 
      state=state, 
      address=address,
      genres = ''.join(genres[0]),
      phone=phone, 
      image_link=image_link, 
      facebook_link=facebook_link,
      website=website_link, 
      seeking_talent=seeking_talent, 
      seeking_description=seeking_description
    )
    db.session.add(venue_entry)
    db.session.commit()

  except:
    err = True
    db.session.rollback()
   
  finally:
    db.session.close()
  
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  flash("Ooop an error occured") if err else flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  er = False

  try:
    # Venue.query.filter_by(id=venue_id).delete()
    Venue.query.filter(Venue.id == venue_id).delete()
    db.session.commit()
    print("deleted")
  except:
    print('not deleted')
    er = True
    db.session.rollback()
  finally:
    db.session.close()

  flash("Oop an error occur") if er else flash(f'The venue with the id {venue_id} was deleted')
  render_template('/pages/home.html')


#  Artists
#  ----------------------------------------------------------------
# Done
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

# Done
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response = {}
  query = request.form.get('search_term', '')
  search_query = f"%{query}%"
  artist = Artist.query.filter(Artist.name.ilike(search_query)).all()
  
  data = []
  for a in artist:
    data.append({
        "id": a.id,
        "name": a.name,
        "num_upcoming_shows": len(Show.query.filter(Show.artist_id == a.id).filter(datetime.now() < Show.start_time).all())
    })
  response['count'] = len(artist)
  response['data'] = data

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

# Done
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get_or_404(artist_id)
  print(artist)
  prev_shows = db.session.query(Show).join(Venue).filter(
          Show.artist_id == artist.id
        ).filter(
          Show.start_time < datetime.now()
        ).all()
  coming_shows = db.session.query(Show).join(Venue).filter(
          Show.artist_id == artist.id     
        ).filter(
          Show.start_time > datetime.now()
        ).all()

  past_show = [] 
  upcoming_shows = []
  for s in prev_shows:
    past_show.append({
      'venue_id': s.venue_id,
      'venue_name': s.venue.name,
      'venue_image_link': s.venue.image_link,
      "start_time": s.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  
  
  for s in coming_shows:
    upcoming_shows.append({
        'venue_id': s.venue_id,
        'venue_name': s.venue.name,
        'venue_image_link': s.venue.image_link,
        "start_time": s.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })        




  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(","),
    "city": artist.city,
    "state": artist.state,    
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_show,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_show),
    "upcoming_shows_count": len(upcoming_shows)
  }
   
  if not data:
    return render_template('errors/404.html')
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get_or_404(artist_id)
  form = ArtistForm()

  if artist:
    form.name.data = artist.name
    form.genres.data = artist.genres
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website_link.data = artist.website
    form.seeking_description.data = artist.seeking_description
    form.seeking_venue.data = artist.seeking_venue

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

# Done
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)
  err = False
  try:
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form.get('facebook_link')
    artist.image_link = request.form.get('image_link')
    artist.website = request.form.get('website_link')
    artist.seeking_description = request.form.get('seeking_description')
    artist.seeking_venue = True if 'seeking_venue' in request.form else False
   
    db.session.commit()

  except:
    err = True
    db.session.rollback()
  finally:
    db.session.close()

  flash(f'An error occurred') if err else flash(f'artist was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get_or_404(venue_id)

  if venue:
    form.name.data = venue.name
    form.genres.data = venue.genres
    form.address.data = venue.address
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.website_link.data = venue.website
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.seeking_description.data = venue.seeking_description
    form.seeking_talent.data = venue.seeking_talent

  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

# Done
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  
  venue = Venue.query.get_or_404(venue_id)
  err = False

  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website = request.form['website_link']
    venue.seeking_description = request.form['seeking_description']
    venue.seeking_talent = True if 'seeking_talent' in request.form else False

    db.session.commit()

  except:
      err = True
      db.session.rollback()
  finally:
      db.session.close()
  flash('An error occurred') if err else flash(f'Venue updated successfully')
  

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------
# Done
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

# Done
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  error = False
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website_link = request.form['website_link']
    seeking_description = request.form['seeking_description']
    seeking_venue =  True if 'seeking_venue' in request.form else False

    artist = Artist(name=name, city=city, state=state, genres=genres, 
      phone=phone, image_link=image_link, facebook_link=facebook_link,
      website=website_link, seeking_venue=seeking_venue, 
      seeking_description=seeking_description
    )

    db.session.add(artist)
    db.session.commit()
  except:
      error = True
      db.session.rollback
  finally:
      db.session.close()

  if error:
      flash(f"An error occurred Artist {request.form['name']} could not be listed.")
  else:
      flash('Artist listed successfully')


  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

# Done
@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  
  # data = db.session.query(Show, Venue, Artist).filter(
  #   Venue.id==Show.venue_id, 
  #   Artist.id == Show.artist_id, 
  # ).all()
  # shws = db.session.query(Show, Venue, Artist).join(Venue, Venue.id==Show.venue_id).join(Artist, Artist.id == Show.artist_id).all()
  dt = db.session.query(Show).join(Artist).join(Venue).all()
  data = []
  for d in dt:
    data.append({
        "venue_id": d.venue_id,
        "venue_name": d.venue.name,
        "artist_id": d.artist_id,
        "artist_name": d.artist.name,
        "artist_image_link": d.artist.image_link,
        "start_time": d.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
    
  return render_template('pages/shows.html', shows=data)

# Done
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


# Done
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  err = False
  try:

    venue_id = request.form['venue_id']
    artist_id = request.form['artist_id']
    start_time = request.form['start_time']
    show = Show(venue_id=venue_id, artist_id=artist_id,
                start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except:
    err = True
    db.session.rollback()
  finally:
      db.session.close()
  # on successful db insert, flash success
  flash('An error occurred. Show could not be listed.') if err else flash('Show was successfully listed!')
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
  app.run(debug=True)
  app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
