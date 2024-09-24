import json
import time
from flask import Flask, jsonify, request, g, render_template
import sqlite3
from main_1 import Run_Crawler
app = Flask(__name__)

DATABASE = 'tours.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.route('/update_database')
def update_database():
      # Example total number of items
    Run_Crawler()
    return jsonify({'status': 'done'})

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    column_names = [description[0] for description in cur.description]
    rv = cur.fetchall()
    cur.close()
    data = [dict(zip(column_names, row)) for row in rv]

    return (rv[0] if rv else None) if one else data


@app.route('/')
def index():
    return render_template('simple.html')


@app.route('/get-categories', methods=['GET'])
def get_categories():
    categories = query_db('SELECT DISTINCT category FROM tours')
    return jsonify(categories)


@app.route('/get-main-collections/<string:category>', methods=['GET'])
def get_main_collections(category):
    main_collections = query_db('SELECT DISTINCT main_collection FROM tours WHERE category = ?', [category])
    return jsonify(main_collections)


@app.route('/get-names/<string:main_collection>', methods=['GET'])
def get_names(main_collection):
    names = query_db('SELECT * FROM tours WHERE main_collection = ?', [main_collection])

    return jsonify(names)


@app.route('/get-tour/<string:tourId>', methods=['GET'])
def get_1_tourData(tourId):
    names = query_db('SELECT * FROM tours WHERE base_tour_id = ?', [tourId])

    return jsonify(names)


def findPrices(maximum: False, name, names):
    if not maximum:
        for i in names:
            if i == name:
                print(names[1])


if __name__ == '__main__':
    # Initialize the database with some data if it doesn't exist
    with app.app_context():
        db = get_db()

    app.run(debug=True)
