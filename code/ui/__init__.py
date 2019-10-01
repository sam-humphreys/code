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
def ui():
    """Subcommand for UI commands"""


@ui.command()
@click.option('--ui-creds', type=click.File(), default='gitops/k8s/secrets/ui-creds.yaml')
def run(ui_creds):
    """Run the Flask application"""
    # Load secrets for dev purposes - ENVVARS set in deployment yaml using gunicorn
    yml = yaml.safe_load(ui_creds.read())
    os.environ['USERNAME'] = yml['data']['username']
    os.environ['PASSWORD'] = yml['data']['password']
    os.environ['RECIPIENT'] = yml['data']['recipient']
    app.config['SECRET_KEY'] = yml['data']['secret_key']

    app.run(host='0.0.0.0')


@app.route('/healthcheck')
def healthcheck():
    """LivenessProb set to hit every 12 seconds to check site"""
    return 'OK', 200


@app.route('/')
def home():
    """Landing page route"""
    return flask.render_template('default/home.html')
