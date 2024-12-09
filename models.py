from app import db
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import UserMixin
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    phone_number = db.Column(db.String(20))

    reviews = db.relationship('Review', backref='user', lazy=True)
    listings = db.relationship('Listing', backref='user', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        """Return the user_id as expected by Flask-Login"""
        return str(self.user_id)


class Book(db.Model):
    __tablename__ = 'book'
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    author = db.Column(db.String(100))
    year = db.Column(db.Integer)
    isbn = db.Column(db.String(13), unique=True)

    listings = db.relationship('Listing', backref='book', lazy=True)

class Listing(db.Model):
    __tablename__ = 'listing'
    listing_id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    condition = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='Available')
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), nullable=False)
    reviews = db.relationship('Review', backref='listing', lazy=True)
    transactions = db.relationship('Transaction', backref='listing', lazy=True)
    reservations = db.relationship('Reservation', backref='listing', lazy=True)

class Review(db.Model):
    __tablename__ = 'review'
    review_id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date)
    rating = db.Column(db.Integer, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.listing_id'), nullable=False)

class Favorite(db.Model):
    __tablename__ = 'favorite'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.listing_id'), nullable=False)

    user = db.relationship('User', backref='favorites')
    listing = db.relationship('Listing', backref='favorites')

class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.listing_id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())

class Reservation(db.Model):
    __tablename__ = 'reservation'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.listing_id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())

class Photo(db.Model):
    __tablename__ = 'photo'
    photo_id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), nullable=False)
