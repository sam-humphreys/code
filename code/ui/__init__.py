import os
import yaml

import click

import flask

# Flask Docs - http://flask.palletsprojects.com/en/1.1.x/
app = flask.Flask(__name__)

LOG = app.logger

# Import views
import code.ui.modules.portfolio.views
import code.ui.modules.contact.views


@click.group()
def flask_app():
    """Subcommand for UI commands"""


@flask_app.command()
@click.option('--ui-creds', type=click.File(), default='gitops/k8s/secrets/ui-creds.yaml')
def run(ui_creds):
    """Run the Flask application"""
    # Load secrets for dev purposes - ENVVARS set in deployment yaml using gunicorn
    yml = yaml.safe_load(ui_creds.read())
    os.environ['USERNAME'] = yml['data']['username']
    os.environ['PASSWORD'] = yml['data']['password']
    os.environ['RECIPIENT'] = yml['data']['recipient']

    app.run(host='0.0.0.0')


@app.route('/')
def index():
    """Landing page route"""
    return flask.render_template('default/home.html')
