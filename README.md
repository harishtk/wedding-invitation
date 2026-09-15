# Our wedding invitation

A single Flask application with a royal burgundy, gold, and ivory invitation, responsive photo frames, a live countdown, celebration confetti, and rotating blessings. Original design; no template licence or frontend build required.

## Run locally

1. Install Python 3.11 or newer.
2. Run `python -m venv .venv` and activate it (`.venv\Scripts\Activate.ps1` on Windows or `source .venv/bin/activate` on macOS/Linux).
3. Run `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env`. Set your private `INVITATION_PASSWORD` and a random `SECRET_KEY` (generate one with `python -c "import secrets; print(secrets.token_hex(32))"`).
5. Run `python app.py` and visit http://127.0.0.1:5000.

## Make it yours

Edit `invitation.json`: couple names, both sets of parents, venue, address, optional HTTPS map link, and nine photo slots. Empty photo slots show intentional decorative placeholders. Use `/static/photos/couple.jpg` for a file placed in `static/photos/`, or an HTTPS public image URL. Photos gently zoom on hover; the opening fades in. Use portrait photos for the couple and individual portraits, landscape photos for family and venue frames. Adjust `object-position` in CSS if a face needs a different crop.

Leave `WEDDING_DATE` empty until the date is fixed. Then set an ISO date with the actual local time and UTC offset, for example `2027-02-14T09:30:00+05:30`. The environment value takes precedence over `date` in the JSON file. `timezone_label` controls the displayed label (default IST); update it if using a different offset. Restart/redeploy after configuration changes. Guests need to reload an already-open page to receive the new date.

Before the date, the page counts down. At and after the configured time it displays blessings and a short confetti shower, with a button to replay. The transition uses the guest device’s clock. Motion is disabled when the device requests reduced motion. Blessings remain readable without motion; basic invitation content works without JavaScript.

## Deploy as one unit on Render

1. Commit this project to your Git repository, excluding `.env`.
2. In Render, select **New → Blueprint**, connect the repository, and use the included `render.yaml`.
3. Supply `INVITATION_PASSWORD` when prompted. Render generates `SECRET_KEY`.
4. Leave `WEDDING_DATE` blank, or set a timezone-qualified date in the service environment. Deploy.

The blueprint installs requirements and starts Gunicorn with two workers. `/health` is the health check. The service uses secure cookies on Render. No database, Node build, separate frontend, or persistent disk is required. Add local photos to the repository before deployment; runtime uploads are not implemented.

Manual Render setup uses build command `pip install -r requirements.txt` and start command `gunicorn 'app:create_app()' --bind 0.0.0.0:$PORT --workers 2`. Set the same environment variables.

See [Render’s Flask deployment guide](https://render.com/docs/deploy-flask) and [Flask cookie configuration](https://flask.palletsprojects.com/en/stable/config/).

## Privacy and behaviour

The shared password opens a signed, HTTP-only session for 12 hours. The server verifies access on the invitation and local photo requests; local photo URLs cannot bypass the login. Login and logout forms have CSRF protection, and private responses are not cached. Changing the password invalidates existing access. Missing secrets stop startup instead of opening the invitation publicly. This is a simple shared-password gate, with no per-person accounts or server-side login throttling; use a long, unique password. Publicly hosted photo links remain public at their source. CSS, JavaScript, and the favicon are public and contain no names or secrets. Google Fonts is optional and has system font fallbacks.

## Checks

Run `python -m unittest discover -s tests`. These cover login, CSRF, private photos, logout, missing secrets, and date handling. Frontend checks can be run using `node tests/countdown.cjs`.
