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
    seen_path = os.path.join(BASE_DIR, "seen_identifiers.txt")

    if not os.path.exists(seen_path):
        open(seen_path, 'w').close()

    with open(seen_path, 'r') as f:
        identifiers = [i.strip("\n") for i in f.readlines()]
    return set(identifiers)


def update_seen_properties(new_identifiers):
    seen_path = os.path.join(BASE_DIR, "seen_identifiers.txt")
    with open(seen_path, 'a+') as f:
        for id_ in new_identifiers:
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

    identifiers = set()
    for i in property_cards:
        rightmove_id = i.find()['id'].strip("prop")
        price = i.find(class_="PropertyPrice_price__VL65t")
        identifier = rightmove_id + "|" + price.text
        identifiers.add(identifier)
    return set(identifiers)


def notify(property_identifiers):
    title = "New properties on your search!"
    msg = "New properties on your search:\n"
    for pid in property_identifiers:
        rightmove_id, price = pid.split("|")
        msg += f' - www.rightmove.co.uk/properties/{rightmove_id} ({price})\n'
        log(msg.replace("\n", "|"))
    url = 'https://api.pushover.net/1/messages.json'
    post_data = {'user': secrets["user_token"], 'token': secrets["api_token"], 'title': title, 'message': msg}
    response = requests.post(url, data=post_data)
    log(f'Response: {response.status_code}')


log("running")
requests.get(secrets["healthchecks_io_uri"] + "/start")

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

requests.get(secrets["healthchecks_io_uri"])
