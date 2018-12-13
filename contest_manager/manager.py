 #!/usr/bin/env python3
from flask import (
        Blueprint, flash, g, redirect, render_template, request, url_for,
        Markup
)
from werkzeug.exceptions import abort

# from contest_manager.auth import login_required
from contest_manager.db import get_db

bp = Blueprint('contest', __name__)

@bp.route('/contest/<int:id>/rules')
def rules(id):
    db = get_db()
    contest = db.execute('SELECT * FROM contest WHERE contest.id = ?', (id,)).fetchone()
    rules = '''# skfsjkdfkd

**AJKLSDFKLASLDASDKKSk** ja *ksdfjksdfjs* kfkk
sdfjklkt test rules
'''
    return render_template('contest/rules.html', contest=contest, rules=rules)

