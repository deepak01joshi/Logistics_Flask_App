from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = os.urandom(12)


# Build the SQLAlchemy URI using env variables
db_user = os.getenv('MYSQL_USER')
db_password = os.getenv('MYSQL_PASSWORD')
db_host = os.getenv('MYSQL_HOST')
db_port = os.getenv('MYSQL_PORT')
db_name = os.getenv('MYSQL_DB')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

bcrypt = Bcrypt(app)

# ------------------------------------------------------------
# MODELS
# ------------------------------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    mobile = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(200))
    user_type = db.Column(db.String(20))  # 'individual' or 'business'
    business_doc = db.Column(db.String(200), nullable=True)

class Shipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tracking_id = db.Column(db.String(20), unique=True)
    sender = db.Column(db.String(100))
    receiver = db.Column(db.String(100))
    origin = db.Column(db.String(100))
    receiver_mobile = db.Column(db.String(20))
    address_line1= db.Column(db.String(225))
    address_line2 = db.Column(db.String(225))
    pincode = db.Column(db.String(20))
    state = db.Column(db.String(255))
    country = db.Column(db.String(255))
    d_address_line1= db.Column(db.String(225))
    d_address_line2 = db.Column(db.String(225))
    d_pincode = db.Column(db.String(20))
    d_state = db.Column(db.String(255))
    d_country = db.Column(db.String(255))

    destination = db.Column(db.String(100))
    weight = db.Column(db.Float)
    status = db.Column(db.String(50), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# ------------------------------------------------------------
# ROUTES
# ------------------------------------------------------------
@app.route('/')
def home():
    return render_template('login.html')

# ---------------- Register ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        password = request.form['password']
        user_type = request.form['user_type']
        business_doc = request.form.get('business_doc')

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(
            name=name, email=email, mobile=mobile,
            password=hashed_password, user_type=user_type,
            business_doc=business_doc
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('home'))
    return render_template('register.html')

# ---------------- Login ----------------
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    user = User.query.filter(
        (User.email == email) | (User.mobile == email)
    ).first()

    if user and bcrypt.check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['user_name'] = user.name
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid credentials!', 'danger')
        return redirect(url_for('register'))

# ---------------- Dashboard ----------------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    return render_template('dashboard.html', user_name=session['user_name'])

# ---------------- Generate Shipment ----------------
@app.route('/generate_shipment', methods=['GET', 'POST'])
def generate_shipment():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        sender = request.form['sender']
        receiver = request.form['receiver']
        origin = request.form['origin']
        destination = request.form['destination']
        weight = float(request.form['weight'])
        receiver_mobile = request.form['receiver_mobile']
        address_line1 = request.form['address_line_1']
        address_line2 = request.form.get('address_line_2') 
        pincode = request.form.get('pincode')
        state = request.form.get('state')
        country = request.form.get('country')
        tracking_id = uuid.uuid4().hex[:8].upper()
        d_address_line1 = request.form['d_address_line_1']
        d_address_line2 = request.form.get('d_address_line_2')  
        d_pincode = request.form.get('d_pincode')
        d_state = request.form.get('d_state')
        d_country = request.form.get('d_country')

        shipment = Shipment(
            tracking_id=tracking_id, sender=sender, receiver=receiver,
            origin=origin, destination=destination, weight=weight,
            user_id=session['user_id'], receiver_mobile=receiver_mobile,
            address_line1=address_line1, address_line2=address_line2,pincode=pincode,
            state=state,country=country,
            d_address_line2=d_address_line2,d_address_line1=d_address_line1,
            d_pincode=d_pincode,d_state=d_state,d_country=d_country,created_at=datetime.utcnow()
        )
        db.session.add(shipment)
        db.session.commit()

        flash(f'Shipment Generated Successfully! Tracking ID: {tracking_id}', 'success')
        return redirect(url_for('shipments'))

    return render_template('generate_shipment.html')

# ---------------- View All Shipments ----------------
@app.route('/shipments')
def shipments():
    
    if 'user_id' not in session:
        return redirect(url_for('home'))
    user_shipments = Shipment.query.filter_by(user_id=session['user_id']).all()
    return render_template('view_shipment.html', shipments=user_shipments)

# -------------------------------- View Single Shipment ----------------
@app.route('/view_shipments', methods=['GET', 'POST'])
def view_shipments():
    search_query = request.args.get('tracking_id', '')  # read search parameter from URL query

    if search_query:
        # Filter shipments by tracking ID (case-insensitive)
        shipments = Shipment.query.filter(Shipment.tracking_id.like(f"%{search_query}%")).all()
    else:
        # Show all shipments
        shipments = Shipment.query.all()

    return render_template('view_shipment.html', shipments=shipments, search_query=search_query)

# ---------------- Track Shipment (Public) ----------------
@app.route('/track_shipment', methods=['GET', 'POST'])
def track_shipment():
    shipment = None
    if request.method == 'POST':
        tracking_id = request.form['tracking_id'].strip().upper()
        shipment = Shipment.query.filter_by(tracking_id=tracking_id).first()
        if not shipment:
            flash('No shipment found for this Tracking ID.', 'danger')  
    return render_template('view_shipment.html', shipment=shipment)
        
# ---------------- Logout ----------------
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))

# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
