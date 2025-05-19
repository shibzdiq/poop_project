from flask import Blueprint, render_template

events = Blueprint('events', __name__)

@events.route('/events')
def list_events():
    return render_template('events.html') 