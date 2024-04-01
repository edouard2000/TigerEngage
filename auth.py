#!/usr/bin/env python

#-----------------------------------------------------------------------
# auth.py
# Authors: Alex Halderman, Scott Karlin, Brian Kernighan, Bob Dondero
#-----------------------------------------------------------------------

import urllib.request
import urllib.parse
import re
import flask
from flask import Flask
import json  # Assuming JSON response for demonstration

#-----------------------------------------------------------------------

_CAS_URL = 'https://fed.princeton.edu/cas/'

app = Flask(__name__)  # Flask app initialization
app.secret_key = 'your_secret_key'  # Set a secret key for session management

#-----------------------------------------------------------------------

# Return url after stripping out the "ticket" parameter that was
# added by the CAS server.

def strip_ticket(url):
    if url is None:
        return "something is badly wrong"
    url = re.sub(r'ticket=[^&]*&?', '', url)
    url = re.sub(r'\?&?$|&$', '', url)
    return url

#-----------------------------------------------------------------------

# Validate a login ticket by contacting the CAS server. If
# valid, return the user's attributes; otherwise, return None.

def validate(ticket):
    val_url = (_CAS_URL + "validate" + '?service='
        + urllib.parse.quote(strip_ticket(flask.request.url))
        + '&ticket=' + urllib.parse.quote(ticket))
    with urllib.request.urlopen(val_url) as flo:
        response = flo.read().decode('utf-8')

    # For demonstration, let's assume the CAS server returns JSON.
    # Adjust parsing according to your CAS server's response format.
    print("CAS Response:", response)  # Print the whole response for review.
    data = json.loads(response)  # Parse the JSON response
    
    if data["auth"]:  # Assuming 'auth' key indicates success. Adjust based on actual response.
        return data["attributes"]  # Assuming user attributes are returned under 'attributes'.
    return None

#-----------------------------------------------------------------------

# Authenticate the remote user, and store or update their data.

def authenticate():
    if 'username' in flask.session:
        return flask.session.get('username')

    ticket = flask.request.args.get('ticket')
    if ticket is None:
        login_url = (_CAS_URL + 'login?service=' +
            urllib.parse.quote(flask.request.url))
        flask.abort(flask.redirect(login_url))

    user_attributes = validate(ticket)
    if user_attributes is None:
        login_url = (_CAS_URL + 'login?service='
            + urllib.parse.quote(strip_ticket(flask.request.url)))
        flask.abort(flask.redirect(login_url))

    # Here, you would insert/update the user in your database.
    # This should be replaced with your database code.
    # Example: insert_user_to_database(user_attributes)

    username = user_attributes["username"]  # Adjust based on actual attribute name
    flask.session['username'] = username  # Store in session
    
    # Return or redirect to your application's main page.
    return username

#-----------------------------------------------------------------------

# # Example database interaction function (pseudocode)
# def insert_user_to_database(attributes):
#     # Connect to your database and insert/update the user record.
#     # This might involve SQLAlchemy, psycopg2, etc., depending on your setup.
#     pass

#-----------------------------------------------------------------------

def logoutapp():
    flask.session.clear()
    html_code = flask.render_template('loggedout.html')
    response = flask.make_response(html_code)
    return response

#-----------------------------------------------------------------------

def logoutcas():
    logout_url = (_CAS_URL + 'logout?service='
        + urllib.parse.quote(
            re.sub('logoutcas', 'logoutapp', flask.request.url)))
    flask.abort(flask.redirect(logout_url))

#-----------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
