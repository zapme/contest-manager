# !/usr/bin/env python3
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
    Markup
)
from werkzeug.exceptions import abort

# from contest_manager.auth import login_required
from contest_manager.db import get_db

bp = Blueprint('contest', __name__)


@bp.route('/')
def index():
    db = get_db()
    contests = db.execute('SELECT * FROM contest ORDER BY start_date DESC').fetchall()
    return render_template('index.html', contests=contests)


@bp.route('/<int:id>/contest')
def rules(id):
    db = get_db()
    contest = db.execute('SELECT * FROM contest WHERE contest.id = ?', (id,)).fetchone()
    rules = '''# skfsjkdfkd

**AJKLSDFKLASLDASDKKSk** ja *ksdfjksdfjs* kfkk
sdfjklkt test rules
'''
    return render_template('contest/rules.html', contest=contest, rules=rules)


@bp.route('/<int:id>/submit', methods=('GET', 'POST'))
def submit_log(id):
    pass


@bp.route('/<int:id>/results')
def results(id):
    pass
