import string
import random
from datetime import datetime
from flask import Flask, request, jsonify, redirect

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
from flask import send_from_directory

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://urluser:urlpass@db:5432/urlshortener'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# --- Database model ---
class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    long_url = db.Column(db.String(2048), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    click_count = db.Column(db.Integer, default=0)


# Create the table(s) if they don't exist yet
with app.app_context():
    db.create_all()


# --- Helper: generate a random short code ---
def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


# --- Route 1: shorten a URL ---
@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()

    if not data or 'url' not in data:
        return jsonify({'error': 'Missing "url" in request body'}), 400

    long_url = data['url']

    # Generate a unique short code (retry if collision, rare but possible)
    short_code = generate_short_code()
    while URLMap.query.filter_by(short_code=short_code).first():
        short_code = generate_short_code()

    new_entry = URLMap(short_code=short_code, long_url=long_url)
    db.session.add(new_entry)
    db.session.commit()

    short_url = f"{request.host_url}{short_code}"
    return jsonify({'short_url': short_url, 'short_code': short_code}), 201


# --- Route 2: redirect from short code to original URL ---
@app.route('/<short_code>', methods=['GET'])
def redirect_to_url(short_code):
    entry = URLMap.query.filter_by(short_code=short_code).first()

    if not entry:
        return jsonify({'error': 'Short code not found'}), 404

    entry.click_count += 1
    db.session.commit()

    return redirect(entry.long_url)


# --- Route 3: basic health check (useful later for monitoring/CI-CD) ---
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
