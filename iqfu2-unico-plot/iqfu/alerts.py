"""
alerts
------
"""
import json
import os
from twilio.rest import TwilioRestClient

TWILIO_CREDS = {}

with open(os.path.expanduser("~/.twilio.json")) as twilio_file:
    TWILIO_CREDS = json.load(twilio_file)

def sms(to, body):
    client = TwilioRestClient(TWILIO_CREDS["account_sid"],
                              TWILIO_CREDS["auth_token"])
    message = client.messages.create(body=body, to=to,
                                     from_=TWILIO_CREDS["phone_number"])
