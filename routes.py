from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from app.models import db, User, Book, Listing, Review, Favorite, Transaction, Reservation, Photo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
import secrets

main = Blueprint('main', __name__)

# Homepage
@main.route('/')
def index():
    listings = Listing.query.all()  # Alle listings ophalen
    return render_template('index.html', listings=listings)

# Registreren
@main.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone_number = request.form.get('phone_number')

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        new_user = User(name=name, email=email, password=hashed_password, phone_number=phone_number)
        db.session.add(new_user)
        db.session.commit()

        flash("Registratie succesvol!", "success")
        return redirect(url_for('main.index'))
    return render_template('register.html')  # Vergeet niet dat je in register.html {{ csrf_token() }} moet toevoegen in je form

# Inloggen
@main.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Inloggen succesvol!", "success")
            return redirect(url_for('main.index'))
        else:
            flash("Foutieve inloggegevens", "danger")
    return render_template('login.html')  # Vergeet niet dat je in login.html {{ csrf_token() }} moet toevoegen in je form

# Uitloggen
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Succesvol uitgelogd!", "info")
    return redirect(url_for('main.index'))

# Listing toevoegen
@main.route('/add_listing', methods=['POST', 'GET'])
@login_required
def add_listing():
    if request.method == 'POST':
        price = request.form['price']
        condition = request.form['condition']
        status = request.form.get('status', 'Available')
        user_id = current_user.user_id
        book_id = request.form['book_id']
        image_url = request.form.get('image_url')

        new_listing = Listing(price=price, condition=condition, status=status, user_id=user_id, book_id=book_id)
        db.session.add(new_listing)
        db.session.commit()

        # Add photo if provided
        if image_url:
            photo = Photo(image_url=image_url, book_id=book_id)
            db.session.add(photo)
            db.session.commit()

        flash("Listing succesvol toegevoegd!", "success")
        return redirect(url_for('main.index'))
    return render_template('add_listing.html')  # Vergeet niet dat je in add_listing.html {{ csrf_token() }} moet toevoegen in je form

# Mijn Listings
@main.route('/my_listings')
@login_required
def my_listings():
    listings = Listing.query.filter_by(user_id=current_user.user_id).all()
    return render_template('my_listings.html', listings=listings)

# Listing bewerken
@main.route('/edit_listing/<int:listing_id>', methods=['POST', 'GET'])
@login_required
def edit_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    if listing.user_id != current_user.user_id:
        flash("Je hebt geen toestemming om deze listing te bewerken.", "danger")
        return redirect(url_for('main.my_listings'))

    if request.method == 'POST':
        listing.price = request.form['price']
        listing.condition = request.form['condition']
        listing.status = request.form.get('status', listing.status)
        db.session.commit()

        flash("Listing succesvol bijgewerkt!", "success")
        return redirect(url_for('main.my_listings'))
    return render_template('edit_listing.html', listing=listing)  # Vergeet niet dat je in edit_listing.html {{ csrf_token() }} moet toevoegen in je form

# Listing verwijderen
@main.route('/delete_listing/<int:listing_id>', methods=['POST'])
@login_required
def delete_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    if listing.user_id != current_user.user_id:
        flash("Je hebt geen toestemming om deze listing te verwijderen.", "danger")
        return redirect(url_for('main.my_listings'))

    db.session.delete(listing)
    db.session.commit()

    flash("Listing succesvol verwijderd!", "success")
    return redirect(url_for('main.my_listings'))

# Wachtwoord reset
@main.route('/reset_password', methods=['POST', 'GET'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()

        if user:
            new_password = secrets.token_hex(8)  # Generate a secure random temporary password
            user.password = generate_password_hash(new_password, method='sha256')
            db.session.commit()
            flash(f"Je tijdelijke wachtwoord is: {new_password}", "success")
        else:
            flash("E-mailadres niet gevonden.", "danger")

        return redirect(url_for('main.login'))
    return render_template('reset_password.html')  # Vergeet niet dat je in reset_password.html {{ csrf_token() }} moet toevoegen in je form

# Favorieten
@main.route('/favorite/<int:listing_id>', methods=['POST'])
@login_required
def favorite(listing_id):
    existing_favorite = Favorite.query.filter_by(user_id=current_user.user_id, listing_id=listing_id).first()
    if existing_favorite:
        flash('Listing is al toegevoegd aan favorieten!', 'warning')
    else:
        favorite = Favorite(user_id=current_user.user_id, listing_id=listing_id)
        db.session.add(favorite)
        db.session.commit()
        flash('Listing toegevoegd aan favorieten!', 'success')
    return redirect(url_for('main.index'))

# Mijn Favorieten
@main.route('/my_favorites')
@login_required
def my_favorites():
    favorites = Favorite.query.filter_by(user_id=current_user.user_id).all()
    return render_template('my_favorites.html', favorites=favorites)

# Recensie toevoegen
@main.route('/add_review/<int:listing_id>', methods=['POST', 'GET'])
@login_required
def add_review(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    if request.method == 'POST':
        comment = request.form['comment']
        rating = request.form['rating']

        review = Review(comment=comment, rating=rating, user_id=current_user.user_id, listing_id=listing_id)
        db.session.add(review)
        db.session.commit()

        flash("Recensie succesvol toegevoegd!", "success")
        return redirect(url_for('main.listing_detail', listing_id=listing_id))
    return render_template('add_review.html', listing=listing)  # Vergeet niet dat je in add_review.html {{ csrf_token() }} moet toevoegen in je form

# Listing details
@main.route('/listing_detail/<int:listing_id>')
def listing_detail(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    reviews = Review.query.filter_by(listing_id=listing_id).all()
    return render_template('listing_detail.html', listing=listing, reviews=reviews)

# Zoekfunctie
@main.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query:
        flash("Voer een geldige zoekterm in.", "warning")
        return redirect(url_for('main.index'))
    
    results = Listing.query.join(Book).filter(
        (Book.title.ilike(f"%{query}%")) | (Book.author.ilike(f"%{query}%"))
    ).all()

    if not results:
        flash("Geen resultaten gevonden voor je zoekopdracht.", "info")

    return render_template('search_results.html', results=results, query=query)
