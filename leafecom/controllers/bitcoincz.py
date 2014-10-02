import datetime
import json
import logging
import requests

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from leafecom.lib.base import BaseController, render

log = logging.getLogger(__name__)

ACCT_URL = {"edleafe": "https://mining.bitcoin.cz/accounts/profile/json/902265-f151074e843f2d8a358ce18a2c035e38",
        "asciipaper": "https://mining.bitcoin.cz/accounts/profile/json/906994-cec6d74649d0908138200b3268b19a72",
        }
BITCOIN_RATE_URL = "https://www.bitstamp.net/api/ticker/"

class BitcoinczController(BaseController):
    def __init__(self, *args, **kwargs):
        super(BitcoinczController, self).__init__(*args, **kwargs)
        if not "bitcoin_exch_rate" in session:
            session["bitcoin_exch_rate"] = 0.00
        if not "last_rate_check" in session:
            session["last_rate_check"] = datetime.datetime.now() - datetime.timedelta(days=1)
        if not "account_check" in session:
            session["account_check"] = datetime.datetime.now() - datetime.timedelta(hours=1)

    def _need_refresh(self, key, minutes):
        now = datetime.datetime.now()
        threshold = session.get(key) + datetime.timedelta(minutes=minutes)
        if now >= threshold:
            session[key] = now
            return True
        return False

    def _update_exchange_rate(self):
        resp = requests.get(BITCOIN_RATE_URL)
        rdict = resp.json()
        session["bitcoin_exch_rate"] = rdict["last"]

    def index(self, id=None):
        which = id or "asciipaper"
        if self._need_refresh("last_rate_check", 15):
            self._update_exchange_rate()
        c.bcrate_link = ACCT_URL.get(which, ACCT_URL["asciipaper"])
        url = ACCT_URL.get(which, ACCT_URL["asciipaper"])
        if self._need_refresh("account_check", 2):
            resp = requests.get(url)
            coin_json = resp.json()
            # Store in session
            session["workers"] = coin_json["workers"]
            session["confirmed_nmc_reward"] = float(coin_json["confirmed_nmc_reward"])
            session["confirmed_reward"] = float(coin_json["confirmed_reward"])
            session["estimated_reward"] = float(coin_json["estimated_reward"])
            session["unconfirmed_nmc_reward"] = float(coin_json["unconfirmed_nmc_reward"])
            session["unconfirmed_reward"] = float(coin_json["unconfirmed_reward"])
            session["hashrate"] = float(coin_json["hashrate"])
        c.workers = session.get("workers")
        c.confirmed_nmc_reward = float(session.get("confirmed_nmc_reward"))
        c.confirmed_reward = float(session.get("confirmed_reward"))
        c.estimated_reward = float(session.get("estimated_reward"))
        c.unconfirmed_nmc_reward = float(session.get("unconfirmed_nmc_reward"))
        c.unconfirmed_reward = float(session.get("unconfirmed_reward"))
        c.hashrate = float(session.get("hashrate"))
        c.exchange_rate = float(session.get("bitcoin_exch_rate", 0))
        c.value = c.exchange_rate * c.confirmed_reward
        c.bcrate_link = BITCOIN_RATE_URL
        session.save()
        return render("/bitcoincz.html")
