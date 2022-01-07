# noinspection PyUnresolvedReferences
from app import app, proxy
from flask import render_template, request, flash


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST' and request.form.get('update_button'):
        if proxy.update_database():
            flash("Database updated successfully")
        else:
            flash("Can not update database!")

    count = proxy.get_items_count()
    return render_template('index.html',
                           people_count=count['people'],
                           planet_count=count['planets'])


@app.route('/people')
def people():
    return render_template('people.html',
                           people=proxy.get_people())


@app.route('/planets')
def planets():
    return render_template('planets.html',
                           planets=proxy.get_planets())


@app.route('/allresidents')
def allresidents():
    return render_template('allresidents.html',
                           data=proxy.get_allresidents())


@app.route('/residents/<planet_name>')
def residents(planet_name: str):
    return render_template('residents.html',
                           planet=proxy.get_planet(planet_name) )
