import typing
import logging
import os

import flask

from code.ui import app
import code.alerts.smtp

LOG = logging.getLogger(__name__)


@app.route('/contact', methods=['POST', 'GET'])
def contact():
    """Contact page - handles form submission for emailing"""
    if flask.request.method == 'POST':
        send_mail(form=flask.request.form.to_dict())

    return flask.render_template('contact/contact.html')


def send_mail(form: typing.Dict[str, str]) -> None:
    """Abstracted send email function"""
    message = f"{form['message']}\n\
        \nName - {form['name']}\
        \nEmail - {form['email']}"

    with code.alerts.smtp.Client(username=os.environ['USERNAME'], password=os.environ['PASSWORD']) as client:
        client.send(
            receiver_email=os.environ['RECIPIENT'],
            subject=form['subject'],
            text_and_type=[(message, 'plain')],
        )

    LOG.info(f'Sent email from - {form["name"]}')
