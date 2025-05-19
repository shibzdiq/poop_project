from flask import Blueprint, render_template

maintenance = Blueprint('maintenance', __name__)

@maintenance.route('/maintenance')
def maintenance_page():
    return render_template('maintenance.html') 