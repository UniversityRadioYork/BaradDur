from waitress import serve
from flask import Flask, render_template, redirect, session, request
import os, requests, json, sys, secrets, re, jwt
from datetime import datetime
from myradio_api import *
import urllib3

#Imports ENV variables

port = os.environ.get('PORT', 6339)

#url to redirect to when using jwt auth
scheduler_url = os.environ.get('SCHEDULER_URL', f"http://127.0.0.1:{port}/")

#key used for myradio jwt auth
myradio_key = os.environ.get('MYRADIO_SIGNING_KEY', "dev")

#key used to validate myradio api requests. This is the only thing you will need to edit for development.
myradio_api = os.environ.get('MYRADIO_API_KEY', "change_me")

#I'm not sure if this does anything but i'm scared to delete it
log_location = os.environ.get('LOG_LOCATION', "/logs/")

#url of the myradio api, change this if you want to test with the myradio dev instance (you don't)
myradio_url = os.environ.get('MYRADIO_URL', "https://www.ury.org.uk/api/v2/")

dev_mode = os.environ.get('DEV_MODE', "True")

#creates an app
class Config:
    PREFERRED_URL_SCHEME = 'https'

app = Flask(__name__)
app.config.from_object(Config())

#just logs some stuff
unix_timestamp = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
print("Starting at " + str(unix_timestamp) , file=sys.stderr)
print("live on " + scheduler_url, file=sys.stderr)

#important for session stuff
app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)

#formats api key a little
myradio_apikey = "api_key="+myradio_api

def auth_route():
    return redirect("https://ury.org.uk/myradio/MyRadio/jwt?redirectto="+scheduler_url+"auth/", code=302)

def verifyKey(key):
    pattern = re.compile('^[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789]+$')
    return re.search(pattern, key)

#lets you in if you are comp officer or have "edit banner" permission or if the app is in dev mode
def verifySession(session):
    if myradio_key == "dev":
        return True
    if ('name' in session and 'uid' in session):
        api_url = myradio_url + "user/"+str(session["uid"])+"/permissions?" + myradio_apikey
        response = requests.get(api_url)
        officer = json.loads(response.text)
        if 221 in officer["payload"] or 234 in officer["payload"]:
            return True
    return False

#either redirects the user to myradio to signing (see auth) or renders a flask-wtf form or stores the values from a submitted form
@app.route("/", methods=['GET'])
def index():
    if verifySession(session):
        get_all_terms()
        pending = pending_allocations()
        return render_template('/index.html', title='Scheduler', pending_allocations=pending)
    else:
        return auth_route()

@app.route('/calendar/', methods=['GET'])
def calendar():
    if verifySession(session):
        return render_template('/calendar.html', title='Calendar')
    else:
        return auth_route()

#uses a jwt to authenticate the user then redirects them back to index
@app.route('/auth/', methods=['GET'])
def auth( ):
    args = request.args
    userinfo = jwt.decode(args['jwt'], myradio_key, algorithms=["HS256"])
    session['name'] = userinfo['name']
    session['uid'] = userinfo['uid']
    return redirect(scheduler_url, code=302)

@app.route('/logout/', methods=['GET'])
def logout():
    session.pop('name', None)
    session.pop('uid', None)
    return render_template('/loggedout.html', title='Logged Out')

@app.route('/allocate/<season_id>', methods=['GET'])
def allocate(season_id):
    if verifySession(session):
        page_data = {}
        page_data['show_data'] = get_show_application(season_id)
        page_data['applied_weeks'] = get_season_applied_weeks(season_id)
        page_data['applied_times'] = get_season_applied_times(season_id)
        return render_template('/allocate.html', title='Allocate', page_data=page_data)
    else:
        return auth_route()
    
@app.route('/reject', methods=['GET'])
def reject():
    if verifySession(session):
        return render_template('/reject.html', title='Reject')
    else:
        return auth_route()
    
@app.route('/timeslot/<timeslot_id>', methods=['GET'])
def timeslot(timeslot_id):
    if verifySession(session):
        timeslot = get_timeslot_info(timeslot_id)['payload']
        return render_template('/timeslot.html', title='Timeslot', timeslot=timeslot)
    else:
        return auth_route()
    
@app.route('/api/allocate/<season_id>', methods=['POST'])
def api_allocate(season_id):
    if verifySession(session):
        data = request.get_json()
        res = schedule_season(season_id, data, request.headers)
        return res
    else:
        return auth_route()
    
@app.route('/api/reject/<season_id>', methods=['POST'])
def api_reject(season_id):
    if verifySession(session):
        req = request.get_json()
        reason = req['reason']
        notify_user = req['notify_user']
        res = reject_season(season_id, reason, notify_user, request.headers)
        return res
    else:
        return auth_route()
    
@app.route('/api/schedule', methods=['GET'])
def api_get_schedule():
    if verifySession(session):
        year = request.args.get('year')
        if year == None:
            year = datetime.now().year
        week = request.args.get('week')
        return get_schedule(year, week)
    else:
        return auth_route()
    
@app.route('/api/conflict', methods=['GET'])
def api_check_for_conflict():
    if verifySession(session):
        start = request.args.get('start')
        duration = request.args.get('duration')
        day = request.args.get('day')
        return check_for_conflicts(day, start, duration)
    else:
        return auth_route()
    
@app.route('/api/cancel/<timeslot_id>', methods=['POST'])
def api_cancel(timeslot_id):
    if verifySession(session):
        data = request.get_json()
        reason = data['reason']
        # Check if reason is empty
        if reason == "":
            return "Reason cannot be empty", 400
        res = cancel_timeslot(timeslot_id, reason, request.headers)
        return res
    else:
        return auth_route()
    
@app.route('/api/move/<timeslot_id>', methods=['POST'])
def api_move(timeslot_id):
    if verifySession(session):
        data = request.get_json()
        new_start = data['start_time']
        new_end = data['end_time']
        res = move_timeslot(timeslot_id, new_start, new_end, request.headers)
        return res
    else:
        return auth_route()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 6339))
    print("Starting server on port " + str(port), file=sys.stderr)
    if dev_mode == "True":
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        print("Running in dev mode", file=sys.stderr)
        app.run(debug=True, host='0.0.0.0', port=port)
    else:
        serve(app, host='0.0.0.0',port=port)
