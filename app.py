import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import load_dotenv
from flask import Flask, abort, redirect, render_template, request, session, url_for

load_dotenv()
ROOT = Path(__file__).resolve().parent


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY'),
        INVITATION_PASSWORD=os.getenv('INVITATION_PASSWORD'),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=os.getenv('RENDER') == 'true',
        PERMANENT_SESSION_LIFETIME=timedelta(hours=12),
        MAX_CONTENT_LENGTH=8192,
    )
    if test_config:
        app.config.update(test_config)
    if not app.config['SECRET_KEY'] or not app.config['INVITATION_PASSWORD']:
        raise RuntimeError('Set SECRET_KEY and INVITATION_PASSWORD in your environment or .env file.')
    with (ROOT / 'invitation.json').open(encoding='utf-8') as file:
        wedding = json.load(file)
    date = os.getenv('WEDDING_DATE', wedding.get('date', '')).strip()
    if date:
        parsed = datetime.fromisoformat(date.replace('Z', '+00:00'))
        if parsed.tzinfo is None:
            raise ValueError('WEDDING_DATE must include a timezone, for example +05:30.')
        date = parsed.isoformat()
        wedding['date_label'] = parsed.strftime('%d %B %Y')
        wedding['time_label'] = parsed.strftime('%I:%M %p') + ' · ' + wedding['timezone_label']
    wedding['date'] = date
    for key, value in wedding['photos'].items():
        if value and not (value.startswith('/static/photos/') or (urlsplit(value).scheme == 'https' and urlsplit(value).netloc)):
            raise ValueError(f'Photo {key}: use /static/photos/filename or an HTTPS URL.')
    if wedding['map_url'] and not (urlsplit(wedding['map_url']).scheme == 'https' and urlsplit(wedding['map_url']).netloc):
        raise ValueError('map_url must be an HTTPS URL.')

    def credential_tag():
        return hmac.new(app.secret_key.encode(), app.config['INVITATION_PASSWORD'].encode(), hashlib.sha256).hexdigest()

    @app.before_request
    def protect():
        if request.endpoint in ('login', 'health'):
            return
        if request.endpoint == 'static' and not request.path.startswith('/static/photos/'):
            return
        if not hmac.compare_digest(session.get('access', ''), credential_tag()):
            return redirect(url_for('login'))

    @app.after_request
    def headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'no-referrer'
        if request.endpoint != 'static' or request.path.startswith('/static/photos/'):
            response.headers['Cache-Control'] = 'no-store'
        return response

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':
            if not hmac.compare_digest(request.form.get('csrf', ''), session.get('csrf', '') or secrets.token_hex()):
                abort(400)
            if hmac.compare_digest(request.form.get('password', '').encode(), app.config['INVITATION_PASSWORD'].encode()):
                session.clear()
                session['access'] = credential_tag()
                session['csrf'] = secrets.token_hex(32)
                session.permanent = True
                return redirect(url_for('index'))
            error = 'That password doesn’t match. Please try the password shared with your invitation.'
        session.setdefault('csrf', secrets.token_hex(32))
        return render_template('login.html', error=error)

    @app.post('/logout')
    def logout():
        if not hmac.compare_digest(request.form.get('csrf', ''), session.get('csrf', '') or secrets.token_hex()):
            abort(400)
        session.clear()
        return redirect(url_for('login'))

    @app.get('/')
    def index():
        return render_template('index.html', w=wedding)

    @app.get('/health')
    def health():
        return {'status': 'ok'}

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
