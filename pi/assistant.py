#!/usr/bin/env python3

# Copyright (C) 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import print_function

import argparse
import os.path
import json
import os

import logging
import platform
import subprocess
import sys
import requests

from google.assistant.library.event import EventType

from aiy.assistant import auth_helpers
from aiy.assistant.library import Assistant
from aiy.board import Board, Led
from aiy.voice import tts

'''
import google.oauth2.credentials
#import RPi.GPIO as GPIO
from google.assistant.library import Assistant
from google.assistant.library.event import EventType
from google.assistant.library.file_helpers import existing_file
'''

from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.enums import PNReconnectionPolicy
from pubnub.pubnub import PubNub

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(25, GPIO.OUT)

global pubnub

#Pubnub Communication
def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        pass  # Message successfully published to specified channel.
    else:
        pass  # Handle message publish error. Check 'category' property to find out possible issue
        # because of which request did fail.
        # Request can be resent using: [status retry];

class MySubscribeCallback(SubscribeCallback):
    def presence(self, pubnub, presence):
        pass  # handle incoming presence data

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            pass  # This event happens when radio / connectivity is lost

        elif status.category == PNStatusCategory.PNConnectedCategory:
            # Connect event. You can do stuff like publish, and know you'll get it.
            # Or just use the connected event to confirm you are subscribed for
            # UI / internal notifications, etc
            # pubnub.publish().channel("magicmirror").message("hello from python!!").async(my_publish_callback)
            pubnub.publish().channel('magicmirror').message({"text": "hello from python"}).pn_async(my_publish_callback)
        elif status.category == PNStatusCategory.PNReconnectedCategory:
            pass
            # Happens as part of our regular operation. This event happens when
            # radio / connectivity is lost, then regained.
        elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
            pass
            # Handle message decryption error. Probably client configured to
            # encrypt messages and on live data feed it received plain text.

    def message(self, pubnub, message):
        print (message.message)
        # pass  # Handle new message stored in message.message

def init_pubnub():
    global pubnub
    pnconfig = PNConfiguration()
    pnconfig.subscribe_key = 'SUBSCRIBE_KEY'
    pnconfig.publish_key = 'PUBLISH_KEY'
    pnconfig.reconnect_policy = PNReconnectionPolicy.LINEAR
    pubnub = PubNub(pnconfig)
    pubnub.add_listener(MySubscribeCallback())
    #pubnub.subscribe().channels('magicmirror').execute()
    pubnub.subscribe().channels('magicmirror').with_presence().execute()
    print ('pubnub subscription completed')


#googleassistant events processing
def process_event(assistant, led, event):
    """Pretty prints events.
    Prints all events that occur with two spaces between each new
    conversation and a single space between turns of a conversation.
    Args:
        event(event.Event): The current event to process.
    """
    if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        os.system("aplay start.wav")
        #pubnub.publish().channel("magicmirror").message("ON_CONVERSATION_TURN_STARTED").async(my_publish_callback)
        pubnub.publish().channel('magicmirror').message({"text": "ON_CONVERSATION_TURN_STARTED"}).pn_async(my_publish_callback)
        print('done')
        #GPIO.output(25,True)
    elif (event.type == EventType.ON_CONVERSATION_TURN_FINISHED and
            event.args and not event.args['with_follow_on_turn']):
        pubnub.publish().channel('magicmirror').message({"text": "ON_CONVERSATION_TURN_FINISHED"}).pn_async(my_publish_callback)
        #pubnub.publish().channel("magicmirror").message("ON_CONVERSATION_TURN_FINISHED").async(my_publish_callback)
        print('done')
        print()
        #GPIO.output(25,False)
    elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED:
        text = event.args['text'].lower()
        print('You said: ', event.args['text'])
        #pubnub.publish().channel("magicmirror").message("ON_RECOGNIZING_SPEECH_FINISHED : "+event.args['text']).async(my_publish_callback)
        pubnub.publish().channel('magicmirror').message({"text": "ON_RECOGNIZING_SPEECH_FINISHED: " + text}).pn_async(my_publish_callback)
        print('done')
        print()

def init_googleAssistant():
    logging.basicConfig(level=logging.INFO)

    credentials = auth_helpers.get_assistant_credentials()
    with Board() as board, Assistant(credentials) as assistant:
        for event in assistant.start():
            process_event(assistant, board.led, event)


def main():
    init_pubnub()
    init_googleAssistant()

if __name__ == '__main__':
    main()
