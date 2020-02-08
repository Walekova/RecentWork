#!/usr/bin/env python
import json
from kafka import KafkaProducer
from flask import Flask, request

app = Flask(__name__)
producer = KafkaProducer(bootstrap_servers='kafka:29092')


def log_to_kafka(topic, event):
    event.update(request.headers)
    producer.send(topic, json.dumps(event).encode())


@app.route("/")
def default_response():
    default_event = {'event_type': 'default'}
    log_to_kafka('game_events', default_event)
    return "This is the default response!\n"

@app.route("/purchase_a_sword")
def purchase_a_sword():
    sword_type = str(request.args.get('sword_type'))
    purchase_sword_event = {'event_type': 'purchase_sword',
                            'description': sword_type,
                             'amount': '-10'}
    log_to_kafka('game_events', purchase_sword_event)
    return "Sword Purchased!\n"

@app.route("/purchase_a_knife")
def purchase_a_knife():
    knife_type = str(request.args.get('knife_type'))
    purchase_knife_event = {'event_type': 'purchase_knife',
                            'description': knife_type ,
                            'amount': '-10'}
    log_to_kafka('game_events', purchase_knife_event)
    return "Knife Purchased!\n"

@app.route("/add_money_to_account")
def add_money_to_account():
    amount = str(request.args.get('amount'))
    add_money_to_account_event = {'event_type': 'add_money',
                                  'description': 'money',
                                  'amount': amount}
    log_to_kafka('game_events', add_money_to_account_event)
    return "Money added to account!\n"

   
@app.route("/join_guild")
def join_guild():
    guild_name = str(request.args.get('guild_name'))    
    join_guild_event = {'event_type': 'join_guild',
                                   'guild_name': guild_name}
    log_to_kafka('game_events', join_guild_event)
    return "Guild Joined"


@app.route("/cancel_membership")
def cancel_membership():
    cancel_reason = str(request.args.get('cancel_reason'))    
    cancel_membership_event = {'event_type': 'cancel_membership',
                                   'cancel_reason': cancel_reason}
    log_to_kafka('game_events', cancel_membership_event)
    return "Membership Cancelled"

@app.route("/message", methods = ['GET', 'POST'])
def message():
    if request.method == 'GET':
        mensaje = str(request.args.get('message_post'))    
        message_event = {'event_type': 'mensaje',
                       'message_post': mensaje}
        log_to_kafka('game_events', message_event)
        return "Message sent"
    elif request.method == 'POST':
        mensaje = str(request.form.get('message_post'))    
        message_event = {'event_type': 'mensaje',
                       'message_post': mensaje}
        log_to_kafka('game_events', message_event)
        return "Message sent"
