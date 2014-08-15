import json
import logging
import requests

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from leafecom.lib.base import BaseController, render

log = logging.getLogger(__name__)

class BitcoinczController(BaseController):

    def index(self):
        resp = requests.get("https://mining.bitcoin.cz/accounts/profile/json/902265-f151074e843f2d8a358ce18a2c035e38")
        coin_json = resp.json()
        c.workers = coin_json["workers"]
        c.confirmed_nmc_reward = float(coin_json["confirmed_nmc_reward"])
        c.confirmed_reward = float(coin_json["confirmed_reward"])
        c.estimated_reward = float(coin_json["estimated_reward"])
        c.unconfirmed_nmc_reward = float(coin_json["unconfirmed_nmc_reward"])
        c.unconfirmed_reward = float(coin_json["unconfirmed_reward"])
        c.hashrate = float(coin_json["hashrate"])
        return render("/bitcoincz.html")
