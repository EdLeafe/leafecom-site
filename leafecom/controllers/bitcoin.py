import datetime
import json
import logging
import requests

from pylons import request
from pylons import response
from pylons import session
from pylons import tmpl_context as c
from pylons import url
from pylons.controllers.util import abort, redirect

import leafecom.lib.helpers as h
from leafecom.lib.base import BaseController
from leafecom.lib.base import render

log = logging.getLogger(__name__)

ACCT_URL = {"edleafe": "https://slushpool.com/accounts/profile/json/902265-f151074e843f2d8a358ce18a2c035e38",
        "asciipaper": "https://slushpool.com/accounts/profile/json/906994-cec6d74649d0908138200b3268b19a72",
        }
BITCOIN_RATE_URL = "https://www.bitstamp.net/api/ticker/"
BITCOIN_STASH = 1.8146


class BitcoinController(BaseController):
    def __init__(self, *args, **kwargs):
        super(BitcoinController, self).__init__(*args, **kwargs)
        if not "btc_rate" in session:
            session["btc_rate"] = 0.00
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
        out, err = h.runproc("coinbase BTC")
        if err:
            session["btc_rate"] = "<unknown>"
        else:
            session["btc_rate"] = out
        out, err = h.runproc("coinbase BCH")
        if err:
            session["bch_rate"] = "<unknown>"
        else:
            session["bch_rate"] = out
#        resp = requests.get(BITCOIN_RATE_URL)
#        if 200 <= resp.status_code < 300:
#            rdict = resp.json()
#            session["btc_rate"] = rdict["last"]
#        else:
#            session["btc_rate"] = "<unknown>"

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
        btc_rate = session.get("btc_rate", 0)
        try:
            c.btc_rate = float(btc_rate)
        except ValueError:
            c.btc_rate = -0.0
        bch_rate = session.get("bch_rate", 0)
        try:
            c.bch_rate = float(bch_rate)
        except ValueError:
            c.bch_rate = -0.0

        c.btc_value = c.btc_rate * c.confirmed_reward
        c.bcrate_link = BITCOIN_RATE_URL
        try:
            session["my_value"] = ((c.btc_rate * BITCOIN_STASH) +
                    (c.bch_rate * BITCOIN_STASH))
        except ValueError:
            session["my_value"] = -42.00
        c.my_value = session["my_value"]
        session.save()
        return render("/bitcoin.html")
