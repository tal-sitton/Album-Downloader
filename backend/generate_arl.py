import json
import random
import re
import uuid

import requests
from pymailtm import pymailtm


def __send_verification_email(email: str):
    url = "https://www.deezer.com/ajax/gw-light.php?method=user_requestVerifyEmailRegistrationEmail&api_version=1.0&api_token=asf"

    payload = json.dumps({
        "EMAIL": email,
        "PASSWORD": email,
        "BLOG_NAME": email.split("@")[0],
        "SEX": random.choice(["M", "F"]),
        "BIRTHDAY": f"{random.randint(1960, 2009)}-01-01",
        "LANG": "en-US",
        "EXPLICIT_ALLOW_TRANSFER_DATA_TO_FRANCE": False,
        "EXPLICIT_ALLOW_PRIVACY_POLICY": False,
        "APP_NAME": "Deezer",
        "APPLICATION_ID": {
            "isLoading": False,
            "appId": 632384
        },
        "DEVICE_TOKEN": uuid.uuid4().hex,
        "REDIRECT": "https%3A%2F%2Fwww.deezer.com%2F"
    })

    requests.request("POST", url, data=payload)


def generate_deezer_account() -> str:
    mailtm = pymailtm.MailTm()
    try:
        mail = mailtm.get_account()
    except Exception:
        mail = mailtm.get_account()
    print(mail.address, mail.password)
    __send_verification_email(mail.address)
    msg: pymailtm.Message = mail.wait_for_message()
    verify_url = re.search(re.escape(r"https://account.deezer.com/validate-registration?token=") + '.+?"',
                           msg.html[0]).group(0).strip('"')
    return verify_url
