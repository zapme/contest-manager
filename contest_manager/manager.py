 #!/usr/bin/env python3
from flask import (
        Blueprint, flash, g, redirect, render_template, request, url_for,
        Markup
)
from werkzeug.exceptions import abort
import json

# from contest_manager.auth import login_required
from contest_manager.db import get_db

bp = Blueprint('contest', __name__)

@bp.route('/<int:id>/contest')
def rules(id):
    db = get_db()
    contest = db.execute('SELECT * FROM contest WHERE contest.id = ?', (id,)).fetchone()
    categories = json.loads(contest['categories'])
    return render_template('contest/rules.html', contest=contest,
            categories=categories)

@bp.route('/<int:id>/submit', methods=('GET', 'POST'))
def submit_log(id):
    pass

@bp.route('/<int:id>/results')
def results(id):
    pass

