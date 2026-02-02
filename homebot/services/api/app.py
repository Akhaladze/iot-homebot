import sys, dotenv, os, requests, json
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


load_dotenv()
token = os.getenv('AUTH_TOKEN')
baseUrl = 'api.mbit-consultants.com'
UpdatesUrl = 'https://api.telegram.org/bot' + token + '/getUpdates'

SQLALCHEMY_DATABASE_URI=os.getenv('SQLALCHEMY_DATABASE_URI')
SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

#db = SQLAlchemy(app) 



@app.route('/')
def hello_world():
    return 'Hello, Docker!'

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST' and request.headers['content-type'] == 'application/json':
        command = request.json['message']['text']
        chat_id = request.json['message']['chat']['id']
        type = request.json['message']['chat']['type']
        
        if type == 'private':
            #first_name = request.json['message']['from']['first_name']
            #last_name = request.json['message']['from']['last_name']
            #username = request.json['message']['from']['username']
            reply_text = 'Use follow commands: /status, /events, /help to manage the bot. '
            requests.post('https://api.telegram.org/bot' + token + '/sendMessage', data={'chat_id': chat_id, 'text': reply_text})          
        
            if command == '/start':
                reply_text = 'Hello, I am SDS Scrapper Bot. Use follow commands: /connectors, /status, /about, /help to manage the bot. '
                requests.post('https://api.telegram.org/bot' + token + '/sendMessage', data={'chat_id': chat_id, 'text': reply_text})

            if command == '/events':
                
                reply_text = 'Backend - no events, Frontend - no events, Parser - no events'
                #result = db.query.select('name').from_table('connectors').execute()
                #result = db.session.execute('SELECT name FROM connectors')
                #result_json = json.dumps(result)
                #while result:  
                #    result_json = json.dumps(result)
                #    result = result.next()
                #    print(result_json)
                #reply_text = result_json
                requests.post('https://api.telegram.org/bot' + token + '/sendMessage', data={'chat_id': chat_id, 'text': reply_text})
            
            if command == '/status':
                reply_text = 'Statuses: OK, ERROR, WARNING...'
                requests.post('https://api.telegram.org/bot' + token + '/sendMessage', data={'chat_id': chat_id, 'text': reply_text})
                
            if command == '/about':
                reply_text = 'SDS Scrapper Bot v0.1'
                requests.post('https://api.telegram.org/bot' + token + '/sendMessage', data={'chat_id': chat_id, 'text': reply_text}) 
            
            if command == '/help':
                reply_text = 'Use telegramm commands: /connectors, /about, /help to manage the bot.'
                requests.post('https://api.telegram.org/bot' + token + '/sendMessage', data={'chat_id': chat_id, 'text': reply_text})
            
            elif command != '/start' and command != '/connectors' and command != '/status' and command != '/about' and command != '/help':
                reply_text = 'Unrecognized command...\n Use follow commands: /connectors, /status, /about, /help to manage the bot.'
                requests.post('https://api.telegram.org/bot' + token + '/sendMessage', data={'chat_id': chat_id, 'text': reply_text})
        
        return jsonify(request.json)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0:5030')