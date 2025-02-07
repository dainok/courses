#!/usr/bin/env python3
# Inspired by https://www.youtube.com/watch?v=BhpkZA9t1HA&list=PLD6FJ8WNiIqUVEA2e5LZhmqNnwFcFhDTZ

from random import randint
from datetime import datetime, timedelta
import json

EVENTS = 1000  # Number of events to generate
PROBABILITY_OF_MALICIOUS_EVENT = 25  # Chances to get a malicious event
EVENT_TYPES = ["url allowed", "url blocked"]  # Dictionary of event types
STARTING_DATE = "2024-05-01T00:00:00"
TIME_DELTA = 7200  # 2 hours
FIRSTNAMES_DICT = "dict-firstnames.txt"
LASTNAMES_DICT = "dict-lastnames.txt"
USER_AGENTS_DICT = "dict-user-agents.txt"
TLDS_DICT = "dict-tlds.txt"
SUBDOMAINS_DICT = "dict-subdomains.txt"
BENIGN_URLCATEGORIES_DICT = "dict-benign-url-categories.txt"
MALICIOUS_URLCATEGORIES_DICT = "dict-malicious-url-categories.txt"

TEMPLATE = {
    "type": None,
    "eventID": None,
    "sourceIP": None,
    "occurred": None,
    "sourceUser": None,
    "url": None,
    "userAgent": None,
    "name": None,
}


def pick(items):
    pos = randint(0, len(items) - 1)
    return items[pos].strip()


def main():
    # Loading dictionaries
    with open(FIRSTNAMES_DICT, "r") as fh:
        firstnames = fh.readlines()
    with open(LASTNAMES_DICT, "r") as fh:
        lastnames = fh.readlines()
    with open(USER_AGENTS_DICT, "r") as fh:
        user_agents = fh.readlines()
    with open(TLDS_DICT, "r") as fh:
        tlds = fh.readlines()
    with open(SUBDOMAINS_DICT, "r") as fh:
        subdomains = fh.readlines()
    with open(BENIGN_URLCATEGORIES_DICT, "r") as fh:
        benign_url_categories = fh.readlines()
    with open(MALICIOUS_URLCATEGORIES_DICT, "r") as fh:
        malicious_url_categories = fh.readlines()

    output = []
    event_timestamp = datetime.strptime(STARTING_DATE, "%Y-%m-%dT%H:%M:%S")

    # Generate events
    for event_id in range(1, EVENTS + 1):
        event_timestamp = event_timestamp + timedelta(seconds=randint(0, TIME_DELTA))
        event = TEMPLATE.copy()
        event["type"] = pick(EVENT_TYPES)
        event["eventID"] = event_id
        event["sourceIP"] = f"10.{randint(1, 254)}.{randint(1, 254)}.{randint(1, 254)}"
        event["occurred"] = f"{event_timestamp.isoformat()}.000Z"
        event["sourceUser"] = f"{pick(firstnames)}.{pick(lastnames)}@example.corp"
        event[
            "url"
        ] = f"https://{pick(subdomains)}.{pick(lastnames)}.{pick(tlds)}/{pick(lastnames)}"
        if randint(0, 100) <= PROBABILITY_OF_MALICIOUS_EVENT:
            event["urlCategory"] = pick(malicious_url_categories)
        else:
            event["urlCategory"] = pick(benign_url_categories)
        event["userAgent"] = pick(user_agents)
        event["name"] = f"Alert {event['type'].capitalize()} - {event['sourceUser']}"
        output.append(event)

    # Print events
    print(json.dumps(output, indent=2))

    # "type": None,
    # "eventID": None,
    # "sourceIP": None,
    # "occurred": None,
    # "sourceUser": None,
    # "url": None,
    # "userAgent": None,

    # with_open = ""
    # user_agents = "https://gist.githubusercontent.com/pzb/b4b6f57144aea7827ae4/raw/cf847b76a142955b1410c8bcef3aabe221a63db1/user-agents.txt"
    # first_names = ""
    # last_names = ""
    # ENGLISH_WORDS_DICT = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
    # FIRST_NAME_DICTS = ""

    # pass


if __name__ == "__main__":
    main()
