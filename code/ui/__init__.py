import click

import flask

# Flask Docs - http://flask.palletsprojects.com/en/1.1.x/
app = flask.Flask(__name__)

LOG = app.logger

# Import views after app definition to avoid circular import errors
import code.ui.modules.portfolio.views


@click.group()
def flask_app():
    """Subcommand for UI commands"""


@flask_app.command()
def run():
    """Run the Flask application"""
    app.run(host='0.0.0.0')


@app.route('/')
def index():
    """Landing page route"""
    return flask.render_template('default/home.html')


@app.route('/about', methods=['POST', 'GET'])
def contact():
    """About page route"""
    if flask.request.method == 'POST':
        # TODO - Send email
        pass

    return flask.render_template('contact.html')
