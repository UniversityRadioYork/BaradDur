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

def get_all_terms(current_only=False):
    params = "currentOnly=false"
    if current_only:
        params = "currentOnly=true"
    response = requests.get(f"{BASE_URL}/term/allterms?" + params + KEY_STRING, verify=should_verify)
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
    times = response.json()["payload"]
    return times

def count_pending_allocations():
    response = requests.get(f"{BASE_URL}/scheduler/countpendingallocations?" + KEY_STRING, verify=should_verify)
    return response.json()

def pending_allocations():
    req_url = f"{BASE_URL}/scheduler/pendingallocations?" + KEY_STRING
    response = requests.get(req_url, verify=should_verify)
    return response.json()

def get_schedule(year, week):
    response = requests.get(f"{BASE_URL}/timeslot/weekschedule/{week}?year={year}" + KEY_STRING, verify=should_verify)
    return response.json()

def get_timeslot_info(timeslot_id):
    response = requests.get(f"{BASE_URL}/timeslot/{timeslot_id}?" + KEY_STRING, verify=should_verify)
    return response.json()

def check_for_conflicts(day, start, duration, term_id = None):
    if term_id == None:
        term_id = get_current_term_id()
    time = json.dumps({
        "day": int(day),
        "start": int(start),
        "duration": int(duration)
    })
    response = requests.get(f"{BASE_URL}/scheduler/scheduleconflicts?term_id={term_id}&time[day]={day}&time[start]={start}&time[duration]={duration}" + KEY_STRING, verify=should_verify)
    print(f"{BASE_URL}/scheduler/scheduleconflicts?term_id={term_id}&time[day]={day}&time[start]={start}&time[duration]={duration}" + KEY_STRING)
    print("HAVE CHECKED: ", response.text)
    return response.json()

# -------- put --------

def schedule_season(season_id, data, headers):
    #num_weeks = sum([1 for week in data['weeks'] if data['weeks'][week] == 1])
    data["timecustom_etime"] = 3600
    num_weeks = len(data['weeks'])
    data_to_send = json.dumps({
        'num_weeks': num_weeks,
        'params': data
    })
    print(data_to_send, season_id)
    response = requests.put(f"{BASE_URL}/season/{season_id}/schedule?" + KEY_STRING, data=data_to_send, headers=headers, verify=should_verify)
    print("HAVE ALLOCATED: ", response.text)
    return response.json()

def reject_season(season_id, reason, headers):
    data = {
        "reason": reason
    }
    data_to_send = json.dumps(data)
    response = requests.put(f"{BASE_URL}/season/{season_id}/reject?" + KEY_STRING, data=data_to_send, headers=headers, verify=should_verify)
    print("HAVE REJECTED: ", response.text)
    return response.json()

def cancel_timeslot(timeslot_id, reason, headers):
    data = {
        "reason": reason
    }
    data_to_send = json.dumps(data) 
    response = requests.put(f"{BASE_URL}/timeslot/{timeslot_id}/canceltimeslot?" + KEY_STRING, data=data_to_send, headers=headers, verify=should_verify)
    return response.json()

def move_timeslot(timeslot_id, new_start, new_end, headers):
    data = {
        "newStart": new_start,
        "newEnd": new_end
    }
    data_to_send = json.dumps(data)
    response = requests.put(f"{BASE_URL}/timeslot/{timeslot_id}/movetimeslot?" + KEY_STRING, data=data_to_send, headers=headers, verify=should_verify)
    return response.json()