import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from secrets import secrets

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def log(msg):
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    out = f'{time} - {msg}\n'
    log_path = os.path.join(BASE_DIR, "log.txt")
    with open(log_path, 'a+') as f:
        f.write(out)
        print(out.strip("\n"))


def get_seen_properties():
    seen_path = os.path.join(BASE_DIR, "seen_ids.txt")
    ids = None
    with open(seen_path, 'r') as f:
        ids = [i.strip("\n") for i in f.readlines()]
    return set(ids)


def update_seen_properties(new_ids):
    seen_path = os.path.join(BASE_DIR, "seen_ids.txt")
    with open(seen_path, 'a+') as f:
        for id_ in new_ids:
            f.write(id_.strip() + "\n")


def fetch_properties():
    content = requests.get(secrets["url"]).content
    soup = BeautifulSoup(content, "html.parser")
    property_cards = soup.find_all(class_=["PropertyCard_propertyCardContainerWrapper__mcK1Z", "propertyCard-details"])

    # The first property card is a "featured property" chosen randomly from the backlog. Since we are only interested in
    # new properties, this can be removed.
    #
    # This assert ensures that we don't miss properties if the design ever changes and they stop featuring properties
    assert property_cards[0].find(class_="PropertyCard_featuredBannerTopOfCard__cYuPM")
    del property_cards[0]

    ids = [i.find()['id'].strip("prop") for i in property_cards]
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
