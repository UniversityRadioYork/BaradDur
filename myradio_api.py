import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()
dev_mode = os.environ.get('DEV_MODE', "True")
should_verify = not dev_mode == "True"

BASE_URL = os.environ.get('MYRADIO_URL', "https://www.ury.org.uk/api/v2")
# These are for pointing to a local server
# BASE_URL = "https://localhost:4443/api/v2"

API_KEY = os.environ.get('MYRADIO_API_KEY', "CHANGE_ME")
# Uncomment the line below to use a local API key
# API_KEY = "mykey"

HEADERS = {"Authorization": f"Bearer {API_KEY}"}
KEY_STRING = f"&api_key={API_KEY}"

'''
Some learnings on the MyRadio API:
- The documentaion is very unclear often wrong
- it uses Swagger to expose a bunch of functions in the ServiceAPI folder of MyRadio. 
- each endpoint has a class and a method so urls are always /class/method
- the API picks GET PUT POST etc based on the NAME OF THE FUNCTION IN MYRADIO?!!?
- If the method name starts with get it's get, if it's set its post, otherwise its always put - yes this is weird
- Getting data into the API is a pain and requires a lot of trial and error see check_for_conflicts for a really cursed example
'''

def get_all_terms(current_only=False):
    params = "currentOnly=false"
    if current_only:
        params = "currentOnly=true"
    response = requests.get(f"{BASE_URL}/term/allterms?" + params + KEY_STRING, verify=should_verify)
    print(response.text)
    return response.json()

def get_current_term_id():
    term = get_all_terms(current_only=False)
    current_term_id = term["payload"][-1]["term_id"]
    return current_term_id

def get_show_application(season_id):
    curr_allocations = pending_allocations()["payload"]
    for allocation in curr_allocations:
        if str(allocation["season_id"]) == str(season_id):
            return allocation
    return None

def get_season_applied_weeks(season_id):
    response = requests.get(f"{BASE_URL}/season/{season_id}/requestedweeks?" + KEY_STRING, verify=should_verify)
    print(response.text)
    weeks_applied_index = response.json()["payload"]
    term = get_all_terms(current_only=False)["payload"][-1]
    week_names = term["week_names"]
    if len(week_names) == 0:
        week_names = [f"Week {str(i)}" for i in range(1, term["num_weeks"] + 1)]
    start = term["start"]
    for i in range(len(week_names)):
        formatted_date = datetime.fromtimestamp(start).strftime('%Y-%m-%d')
        week_names[i] = week_names[i] + " ( w/c " + formatted_date + ")"
        start += (86400 * 7) #one week
    applied_weeks = [(True, name, i+1) if i+1 in weeks_applied_index else (False, name, i+1) for i, name in enumerate(week_names)]
    return applied_weeks

def get_season_applied_times(season_id):
    response = requests.get(f"{BASE_URL}/season/{season_id}/requestedtimesavail?" + KEY_STRING, verify=should_verify)
    print(response.text)
    times = response.json()["payload"]
    return times

def count_pending_allocations():
    response = requests.get(f"{BASE_URL}/scheduler/countpendingallocations?" + KEY_STRING, verify=should_verify)
    print(response.text)
    return response.json()

def pending_allocations():
    req_url = f"{BASE_URL}/scheduler/pendingallocations?" + KEY_STRING
    response = requests.get(req_url, verify=should_verify)
    print(response.text)
    return response.json()

def get_schedule(year, week):
    response = requests.get(f"{BASE_URL}/timeslot/weekschedule/{week}?year={year}" + KEY_STRING, verify=should_verify)
    print(response.text)
    return response.json()

def get_timeslot_info(timeslot_id):
    response = requests.get(f"{BASE_URL}/timeslot/{timeslot_id}?" + KEY_STRING, verify=should_verify)
    print(response.text)
    return response.json()

def check_for_conflicts(day, start, duration, term_id = None):
    '''
    Lets talk about those url params
    the PHP method exapects term_id as one param, thats fine. The other param is $time. This is an assoc array. Turns out to get this into php you just write every key out as a param.
    Again this is a FEATURE OF PHP. So... okay thanks i guess? oh yeah and no one wrote this down anywhere so it was a total pain in the ass to find.
    '''
    if term_id == None:
        term_id = get_current_term_id()
    time = json.dumps({
        "day": int(day),
        "start": int(start),
        "duration": int(duration)
    })
    response = requests.get(f"{BASE_URL}/scheduler/scheduleconflicts?term_id={term_id}&time[day]={day}&time[start]={start}&time[duration]={duration}" + KEY_STRING, verify=should_verify)
    print(response.text)
    return response.json()

# -------- put --------

def schedule_season(season_id, data, headers):
    num_weeks = len(data['weeks'])
    data_to_send = json.dumps({
        'num_weeks': num_weeks,
        'params': {
            'weeks': data['weeks'],
            'time': data['time'],
            'timecustom_day': data['timecustom_day'],
            'timecustom_stime': data['timecustom_stime'],
            'timecustom_etime': data['timecustom_etime']
        }
    })
    response = requests.put(f"{BASE_URL}/season/{season_id}/schedule?" + KEY_STRING, data=data_to_send, headers=headers, verify=should_verify)
    print(response.text)
    return response.json()

def reject_season(season_id, reason, notify_user, headers):
    data = {
        "reason": reason,
        "notify_user": notify_user
    }
    data_to_send = json.dumps(data)
    response = requests.put(f"{BASE_URL}/season/{season_id}/reject?" + KEY_STRING, data=data_to_send, headers=headers, verify=should_verify)
    print(response.text)
    return response.json()

def cancel_timeslot(timeslot_id, reason, headers):
    data = {
        "reason": reason
    }
    data_to_send = json.dumps(data) 
    response = requests.put(f"{BASE_URL}/timeslot/{timeslot_id}/canceltimeslot?" + KEY_STRING, data=data_to_send, headers=headers, verify=should_verify)
    print(response.text)
    return response.json()

def move_timeslot(timeslot_id, new_start, new_end, headers):
    data = {
        "newStart": new_start,
        "newEnd": new_end
    }
    data_to_send = json.dumps(data)
    response = requests.put(f"{BASE_URL}/timeslot/{timeslot_id}/movetimeslot?" + KEY_STRING, data=data_to_send, headers=headers, verify=should_verify)
    print(response.text)
    return response.json()