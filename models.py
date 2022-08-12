from app import db


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String()) #Array
    # genres = db.Column(ARRAY(db.String), default=[]) #Array
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    website = db.Column(db.String(500))
    seeking_description = db.Column(db.String(200))
    seeking_talent = db.Column(db.Boolean(), default=False)
    shows = db.relationship("Show", backref="venue", lazy=True)
    


    def __repr__(self) -> str:
      return f"<Venue: {self.name} ...>"

  


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    # genres = db.Column(ARRAY(db.String), default=[]) #array 
    genres = db.Column(db.String())
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    website = db.Column(db.String(500), nullable=True)
    seeking_description = db.Column(db.String())
    seeking_venue = db.Column(db.Boolean(), default=False)
    shows = db.relationship('Show', backref='artist', lazy=True)

    
    def __repr__(self) -> str:
      return f"<Artist: {self.name} ...>"


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = "Show"
  id = db.Column(db.Integer, primary_key=True)
  artist_id= db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id= db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)

