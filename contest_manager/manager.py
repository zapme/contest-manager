# !/usr/bin/env python3
import re
import os
from datetime import datetime

from flask import Blueprint, render_template, request, current_app, abort, \
    flash, redirect
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from itsdangerous import TimestampSigner
from cabrillo.parser import parse_log_text
from cabrillo.data import VALID_CATEGORIES_MAP
from cabrillo.errors import CabrilloParserException

import json

# from contest_manager.auth import login_required
from contest_manager import emails
from contest_manager.contests import ALL_CONTESTS
from contest_manager.db import get_db

CALLSIGN_REGEX = r'^\d?[a-zA-Z]{1,2}\d{1,4}[a-zA-Z]{1,4}$'

bp = Blueprint('contest', __name__)


@bp.route('/')
def index():
    db = get_db()
    contests = db.execute(
        'SELECT * FROM contest ORDER BY start_date DESC').fetchall()

    return render_template('index.html', contests=contests)


@bp.route('/<int:id>/contest')
def rules(id):
    db = get_db()
    contest = db.execute('SELECT * FROM contest WHERE contest.id = ?',
                         (id,)).fetchone()
    make_contest_404(contest)
    categories = json.loads(contest['categories'])
    return render_template('contest/rules.html', contest=contest,
                           categories=categories)


@bp.route('/<int:id>/submit', methods=('GET', 'POST'))
def submit_log(id):
    db = get_db()
    contest = db.execute('SELECT * FROM contest WHERE contest.id = ?',
                         (id,)).fetchone()
    make_contest_404(contest)

    # Preemptively reject overdue submissions.
    if datetime.utcnow() > contest['log_due_date']:
        return render_template('contest/submit_overdue.html', contest=contest)

    if request.method == 'POST':
        form = request.form
        has_error = False
        mail = Mail(current_app)
        form = request.form

        if 'log' not in request.files:
            flash('Log file not found.')
            return redirect(request.url)

        # Attempt to parse the Cabrillo file.
        f = request.files['log']
        f.seek(0)
        try:
            cab = parse_log_text(f.read().decode('utf-8'),
                                 ignore_unknown_key=False,
                                 check_categories=False)
        except CabrilloParserException as e:
            has_error = True
            flash('Improperly formatted Cabrillo: {}'.format(str(e)))
            return redirect(request.url)
        except UnicodeDecodeError:
            has_error = True
            flash(
                'Improperly encoded file: If you have non-ASCII charac'
                'ters (eg Des Vœux Road Central, 皇后大道東), ensure '
                'the file is saved as UTF-8.')
            return redirect(request.url)
        f.seek(0)  # Recover file position

        # Verify callsigns.
        for call in [request.form['callsign'],
                     request.form['stn-call']] + [x for x in request.form[
            'op-call'].strip().split(' ')]:
            if not is_call(call):
                has_error = True
                flash('{} is not a valid call sign.'.format(call))

        # Verify claimed score is valid number.
        try:
            int(request.form['claimed'])
        except ValueError:
            has_error = True
            flash('{} must be an integer.'.format(request.form['claimed']))

        # Verify that the user hasn't messed with our categories.
        for category in VALID_CATEGORIES_MAP.keys():
            user_value = request.form.get(category, None)
            # Exempt blank overlay, which may actually be empty.
            if category != 'category_overlay' and user_value != '':
                if user_value not in \
                        VALID_CATEGORIES_MAP[category]:
                    has_error = True
                    flash('`{}` is not one of {}.'.format(user_value,
                                                          VALID_CATEGORIES_MAP[
                                                              category]))

        # Contest-specific verification
        contest_class = ALL_CONTESTS[contest['alias']][0]
        submission = contest_class(callsign=form['callsign'].upper(),
                                   name=form['name'],
                                   claimed_score=form['claimed'],
                                   operator_callsigns=form['op-call'].upper(),
                                   station_callsign=form['stn-call'],
                                   club_name=form['club'],
                                   category_assisted=form['category_assisted'],
                                   category_power=form['category_power'],
                                   category_band=form['category_band'],
                                   category_mode=form['category_mode'],
                                   category_operator=form['category_operator'],
                                   category_transmitter=form[
                                       'category_transmitter'],
                                   category_station=form['category_station'],
                                   category_time=form['category_time'],
                                   category_overlay=form['category_overlay'],
                                   log=cab
                                   )
        err_message = submission.verify()
        if err_message:
            has_error = True
            flash(err_message)

        if not has_error:
            time = datetime.utcnow()
            filename = secure_filename(
                '{}-{}.log'.format(request.form['callsign'].upper(),
                                   time.strftime('%Y%m%d%H%M%S%f')))
            request.files['log'].save(
                os.path.join(current_app.config['LOGS_DIR'], filename))

            # Sign a receipt number for the user.
            s = TimestampSigner(current_app.config['SIGN_SECRET'])
            receipt = s.sign(str(filename))

            # Send emails.
            with mail.connect() as conn:
                conn.send(
                    Message(body=emails.OK_TEMPLATE.format(
                        name=contest['name'],
                        receipt=receipt.decode(),
                        time=time),
                        recipients=[form['email'].strip()],
                        subject='Contest Log Received')
                )
                # Check for prior submission and notify if so.
                prior = db.execute(
                    'SELECT * FROM uploads WHERE contest_id = ? '
                    'AND callsign = ? ORDER BY time DESC;',
                    (id, form['callsign'].upper())).fetchone()
                if prior:
                    conn.send(
                        Message(body=emails.DUP_TEMPLATE.format(
                            name=contest['name'],
                            receipt=receipt.decode(),
                            time=time),
                            recipients=[prior['email']],
                            subject='Your contest submission was replaced.')
                    )

            db.execute(
                'INSERT INTO uploads (contest_id, time, filename, email, name,'
                'claimed_score, callsign, operator_callsigns,'
                'station_callsign, club_name, soapbox, category_assisted,'
                'category_power, category_band, category_mode,'
                'category_operator, category_transmitter, category_station,'
                'category_time, category_overlay) VALUES'
                '(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (id, time.strftime('%Y-%m-%d %H:%M:%S'), filename,
                 form['email'].strip(), form['name'], form['claimed'],
                 form['callsign'].upper(), form['op-call'].upper(),
                 form['stn-call'].upper(), form['club'],
                 form['soapbox'], form['category_assisted'],
                 form['category_power'], form['category_band'],
                 form['category_mode'], form['category_operator'],
                 form['category_transmitter'], form['category_station'],
                 form['category_time'], form['category_overlay']))
            db.commit()

            return render_template('contest/submit_ok.html', contest=contest,
                                   receipt=receipt.decode())

    return render_template('contest/submit.html', contest=contest,
                           categories=VALID_CATEGORIES_MAP)


def make_contest_404(contest):
    if contest is None:
        abort(404)


def is_call(callsign):
    return re.match(CALLSIGN_REGEX, callsign) is not None


@bp.route('/<int:id>/results')
def results(id):
    pass
