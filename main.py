import requests
from bs4 import BeautifulSoup
from datetime import datetime

from secrets import secrets


def log(msg):
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    out = f'{time} - {msg}\n'
    with open("log.txt", 'a+') as f:
        f.write(out)
        print(out.strip("\n"))


def get_seen_properties():
    ids = None
    with open("seen_ids.txt", 'r') as f:
        ids = [i.strip("\n") for i in f.readlines()]
    return set(ids)


def update_seen_properties(new_ids):
    with open("seen_ids.txt", 'a+') as f:
        for id_ in new_ids:
            f.write(id_.strip() + "\n")


def fetch_properties():
    content = requests.get(secrets["url"]).content
    soup = BeautifulSoup(content, "html.parser")
    ids = [i.find()['id'].strip("prop") for i in
           soup.find_all(class_=["PropertyCard_propertyCardContainerWrapper__mcK1Z", "propertyCard-details"])]
    return set(ids)


def notify(property_ids):
    title = "New properties on your search!"
    msg = "New properties on your search:\n"
    for pid in property_ids:
        msg += " - www.rightmove.co.uk/properties/" + pid + "\n"
    url = 'https://api.pushover.net/1/messages.json'
    post_data = {'user': secrets["user_token"], 'token': secrets["api_token"], 'title': title, 'message': msg}
    response = requests.post(url, data=post_data)
    log(f'Response: {response.status_code}')


log("running")
seen_properties = get_seen_properties()
log(f'Seen properties: {len(seen_properties)}')
online_properties = fetch_properties()
log(f'Online properties: {len(online_properties)}')
new_properties = online_properties - seen_properties
log(f'New properties: {len(new_properties)}')

if new_properties:
    notify(new_properties)
else:
    log("No notify")

update_seen_properties(new_properties)

requests.get("https://hc-ping.com/HqZbWLJsQGzCH4JWZbyDSw/rightmove-notifier")