import json

from flask import Flask, jsonify, request, g, render_template
import sqlite3

app = Flask(__name__)

DATABASE = 'tours.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-categories', methods=['GET'])
def get_categories():
    categories = query_db('SELECT DISTINCT category FROM tours')
    return jsonify([{"category": category[0]} for category in categories])

@app.route('/get-main-collections/<string:category>', methods=['GET'])
def get_main_collections(category):
    main_collections = query_db('SELECT DISTINCT main_collection FROM tours WHERE category = ?', [category])
    return jsonify([{"main_collection": mc[0]} for mc in main_collections])

@app.route('/get-names/<string:main_collection>', methods=['GET'])
def get_names(main_collection):
    names = query_db('SELECT name, price FROM tours WHERE main_collection = ?', [main_collection])

    return jsonify([{"name": name[0], "prices":name[1] , "change_7d": 0, "change_30d": 0} for name in names])
def findPrices(maximum:False,name,names):
    if not maximum:
        for i in names:
            if i == name:
                print(names[1])


if __name__ == '__main__':
    # Initialize the database with some data if it doesn't exist
    with app.app_context():
        db = get_db()

    app.run(debug=True)
