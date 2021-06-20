import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
import sys
from werkzeug.exceptions import abort
import logging

connection_count = 0

def set_hits_counter():
    global connection_count
    connection_count = connection_count + 1



# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    set_hits_counter()
    return connection


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    connection.close()
    return post


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_is_here'


# Define the main route of the web application
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    app.logger.info("From @app.route('/'): All artices displayed!")

    return render_template('index.html', posts=posts)


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.error("From @app.route('/<int:post_id>'): Artice with id: "+str(post_id)+" cannot be retrieved!")
        return render_template('404.html'), 404
    else:
        post = get_post(post_id)
        app.logger.info("From @app.route('/<int:post_id>'): Artice "+post[2]+" retrieved!")
        return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About page successfully retrieved!')
    return render_template('about.html')


# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            app.logger.error(" From @app.route('/create', methods=('GET', 'POST')): No title specified for new article!")
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            connection.close()
            app.logger.info(" From @app.route('/create', methods=('GET', 'POST')): Article with title "+title+" added to database")
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/healthz')
def healthcheck():
    response = app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
        mimetype='application/json'
    )

    app.logger.info('Health check successful')
    return response


@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT COUNT(*) FROM posts AS CNT').fetchone()
    
    connection.close()
    
    data = {"db_connection_count": str(connection_count), "post_count": posts[0]}
    return jsonify(data), 200	
    app.logger.info('Metrics request successful')
    return response


@app.errorhandler(404)
def page_not_found(e):
    app.logger.error('Page could not be found')
    return 'This page does not exist', 404


# start the application on port 3111
if __name__ == "__main__":
    stdout_handler = logging.StreamHandler(sys.stdout)
    stderr_handler = logging.StreamHandler(sys.stderr)
    handlers = [stderr_handler, stdout_handler]
    # format output
    format_output = '%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
    logging.basicConfig(level=logging.DEBUG, handlers=handlers, format=format_output)
    app.run(host='0.0.0.0', port='3111')
