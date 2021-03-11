import logging
import sys
from slixmpp import ClientXMPP
import requests
import json

class Client(ClientXMPP):

    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

    def message(self, msg):
        print("#######################################")
        print(msg['body'])
        if msg['type'] in ('chat', 'normal'):
            obj = msg['body']
            r = requests.post("http://web/get_event", json = obj)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')

    #Arguments : utilisateur et le mdp
    xmpp = Client("serv@iot.com", "test")
    xmpp.connect(address=("openfire", 5222))
    xmpp.process()