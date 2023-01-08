#!/usr/bin/env python3

# ####################################################
# manual authentication hook into a DNS provider
# (in this example strato.com)
# it logs into the Customer Service App
# and adds the ACME challenge into a txt record
# for LetsEncrypt Wildcard Certificates
# Source: https://github.com/Buxdehuda/strato-certbot
# ####################################################

import json
import os
import re
import requests

def main():
    # get authentication
    with open("strato-auth.json") as file:
        auth = json.load(file)
        username = auth["username"]
        password = auth["password"]

    api_url = "https://www.strato.de/apps/CustomerService"
    txt_key = "_acme-challenge"
    txt_value = os.environ["CERTBOT_VALIDATION"]
    domain_name = re.search(r"([^.]+\.\w+)$", os.environ["CERTBOT_DOMAIN"]).group(1)

    # setup session for cookie sharing
    http_session = requests.session()

    # request session id

    request = http_session.get(api_url)
    request = http_session.post(api_url, { "identifier": username, "passwd": password, "action_customer_login.x": "Login" })
    session_id = re.search(r"sessionID=(.*?)\"", request.text).group(1)

    # set txt record
    http_session.post(api_url, { "sessionID": session_id, "cID": "1", "node": "ManageDomains", "vhost": domain_name, "spf_type": "NONE", "prefix": txt_key, "type": "TXT", "value": txt_value, "action_change_txt_records": "Einstellung+übernehmen" })

if __name__ == "__main__":
    main()