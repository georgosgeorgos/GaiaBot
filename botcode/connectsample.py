import requests
import json
import sys
import uuid
import sqliteshelve
import requests
from flask import Flask, redirect, url_for, session, request, render_template
from flask_oauthlib.client import OAuth

# read private credentials from text file
client_id, client_secret, *_ = open('_PRIVATE.txt').read().split('\n')
if (client_id.startswith('*') and client_id.endswith('*')) or \
        (client_secret.startswith('*') and client_secret.endswith('*')):
    print('MISSING CONFIGURATION: the _PRIVATE.txt file needs to be edited ' + \
          'to add client ID and secret.')
    sys.exit(1)

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

# since this sample runs locally without HTTPS, disable InsecureRequestWarning
requests.packages.urllib3.disable_warnings()
msgraphapi = oauth.remote_app(
    'microsoft',
    consumer_key=client_id,
    consumer_secret=client_secret,
    request_token_params={'scope': 'Calendars.Read Mail.Read'},
    base_url='https://graph.microsoft.com/v1.0/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://login.microsoftonline.com/common/oauth2/v2.0/token',
    authorize_url='https://login.microsoftonline.com/common/oauth2/v2.0/authorize'
)


@app.route('/')
def index():
    """Handler for home page."""
    return render_template('connect.html')


@app.route('/login')
def login():
    """Handler for login route."""
    guid = uuid.uuid4()  # guid used to only accept initiated logins
    session['state'] = guid
    return msgraphapi.authorize(callback=url_for('authorized', _external=True), state=guid)


@app.route('/logout')
def logout():
    """Handler for logout route."""
    session.pop('microsoft_token', None)
    session.pop('state', None)
    return redirect(url_for('index'))


@app.route('/login/authorized')
def authorized():
    """Handler for login/authorized route."""
    response = msgraphapi.authorized_response()

    if response is None:
        return "Access Denied: Reason={0}\nError={1}".format(
            request.args['error'], request.args['error_description'])

    # Check response for state
    if str(session['state']) != str(request.args['state']):
        raise Exception('State has been messed with, end authentication')
    session['state'] = ''  # reset session state to prevent re-use

    # Okay to store this in a local variable, encrypt if it's going to client
    # machine or database. Treat as a password.
    session['microsoft_token'] = (response['access_token'], '')
    # Store the token in another session variable for easy access
    session['access_token'] = response['access_token']
    me_response = msgraphapi.get('me')
    me_data = json.loads(json.dumps(me_response.data))
    username = me_data['displayName']
    email_address = me_data['userPrincipalName']
    session['alias'] = username
    session['userEmailAddress'] = email_address
    return redirect('main')


@app.route('/main')
def main():
    """Handler for main route."""
    if session['alias']:
        username = session['alias']
        email_address = session['userEmailAddress']
        return render_template('main.html', name=username, emailAddress=email_address)
    else:
        return render_template('main.html')


def send_data_to_server(events, emails, email_address):
    emailsToSend = getMailToSend(emails)
    calenderToSend = getCalendarToSend(events)

    doc = sqliteshelve.open('./db.sqliteshelve')
    user_data = {
        'emails': emailsToSend,
        'calendar': calenderToSend,
    }
    doc[email_address] = user_data
    doc.close()
    doc = sqliteshelve.open('./db.sqliteshelve')
    doc.close()
    print(doc[email_address])


def getMailToSend(emails):
    emailsToSend = []
    for e in emails['value']:
        emailsToSend.append(str(e))
    return emailsToSend


def getCalendarToSend(events):
    calenderToSend = []
    for e in events:
        calenderToSend.append(e['body'])
    return calenderToSend


@app.route('/send_mail')
def profile_user():
    events = fetch_events()
    emails = fetch_emails()
    email_address = request.args.get('emailAddress')  # get email address from the form
    send_data_to_server(events, emails, email_address)

    # session['pageRefresh'] = 'false'
    return render_template('main.html', name=session['alias'])


def fetch_emails():
    try:
        query_parameters = {
            # '$top': '10',
            # '$select': "subject,body,bodyPreview,organizer,attendees,start,end,location",
            # '$orderby': 'Start/DateTime ASC'
        }
        emails = query_calendar_informations(session['access_token'], query_parameters, "messages", ).json()
    except json.JSONDecodeError as e:
        print("FUUUCK")
        raise e
        # else:
        # for e in emails['value']:
        # print(e)
    return emails


def fetch_events():
    try:
        query_parameters = {
            # '$top': '10',
            '$select': "subject,body,bodyPreview,organizer,attendees,start,end,location",
            # '$orderby': 'Start/DateTime ASC'
        }
        events = query_calendar_informations(session['access_token'], query_parameters, "events").json()
    except json.JSONDecodeError as e:
        print("FUUUCK")
        raise e
    else:
        return events['value']


@msgraphapi.tokengetter
def get_token():
    """Return the Oauth token."""
    return session.get('microsoft_token')


def query_calendar_informations(access_token, query_parameters, path):
    """Call the resource URL for the sendMail action."""
    outlook_api_endpoint = 'https://graph.microsoft.com/v1.0/me/{}'.format(path)

    headers = {
        'User-Agent': 'secretairy/1.0',
        'Authorization': 'Bearer {0}'.format(access_token),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    response = requests.get(outlook_api_endpoint, headers=headers, params=query_parameters)
    return response
