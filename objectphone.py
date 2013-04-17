import os
from flask import Flask, request, redirect
from twilio import twiml
import cStringIO
import pycurl
import urllib
import simplejson as json

api_token = os.environ['CH_API_KEY']

app = Flask(__name__)

@app.route('/')
def hello():
  r = twiml.Response()
	r.say("Welcome to object phone!. ") 
	with r.gather(numDigits=1, action="initial-handler", method="POST") as g:
		g.say("Press one on your touchtone phone to search the Cooper-Hewitt collection by object ID. Press 2 to just listen to a random object.")
	return str(r)
	
@app.route('/initial-handler', methods=['GET','POST'])
def handlecall():
	digits = request.values.get('Digits', None)
	r = twiml.Response()
	if (digits == "1"):
		with r.gather(action="object", method="POST") as g:
			g.say("Please enter an object ID followed by the pound key.")
		return str(r)
	
	if (digits == "2"):
		return redirect("/random")

		

@app.route('/object', methods=['GET','POST'])
def obj():
	obj_id = request.values.get('Digits', None)
	r = twiml.Response()
	
	buf = cStringIO.StringIO()
	c = pycurl.Curl()
	c.setopt(c.URL, 'https://api.collection.cooperhewitt.org/rest')
	d = {'method':'cooperhewitt.objects.getInfo','access_token':api_token, 'id':obj_id}
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.setopt(c.POSTFIELDS, urllib.urlencode(d) )
	c.perform()
	
	rsp_obj = json.loads(buf.getvalue())
	buf.reset()
	buf.truncate()
	object_id = rsp_obj.get('object', [])
	medium = object_id.get('medium', [])
	title = object_id.get('title', [])
	
	phrase = "Thanks for dialing an object. "

	if (title):
		phrase = phrase + "Your object is called " + title + ". "
		
	if (medium):
		phrase = phrase + "It's medium is " + medium + ". "
	
	r.say(phrase)
	return str(r)


@app.route('/random')
def random():
	buf = cStringIO.StringIO()
	c = pycurl.Curl()
	c.setopt(c.URL, 'https://api.collection.cooperhewitt.org/rest')
	d = {'method':'cooperhewitt.objects.getRandom','access_token':api_token}
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.setopt(c.POSTFIELDS, urllib.urlencode(d) )
	c.perform()
	
	random = json.loads(buf.getvalue())
	buf.reset()
	buf.truncate()
	object_id = random.get('object', [])
	medium = object_id.get('medium', [])
	title = object_id.get('title', [])
	
	phrase = "Thanks, we are looking up a random object just for you. "
	if (title):
		phrase = phrase + "Your random object is called " + title + ". "
		
	if (medium):
		phrase =  phrase + "It's medium is " + medium + ". "
	
	
	r = twiml.Response()
	r.say(phrase)
	return str(r)
	
@app.route('/sms', methods=['GET','POST'])
def object():
	obj_id = request.values.get('Body', None)
	r = twiml.Response()
	
	buf = cStringIO.StringIO()
	c = pycurl.Curl()
	c.setopt(c.URL, 'https://api.collection.cooperhewitt.org/rest')
	d = {'method':'cooperhewitt.objects.getInfo','access_token':api_token, 'id':obj_id}
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.setopt(c.POSTFIELDS, urllib.urlencode(d) )
	c.perform()
	
	rsp_obj = json.loads(buf.getvalue())
	buf.reset()
	buf.truncate()
	object_id = rsp_obj.get('object', [])
	medium = object_id.get('medium', [])
	title = object_id.get('title', [])
	
	phrase = "Thanks for texting me. "

	if (title):
		phrase = phrase + "Your object is called " + title + ". "
		
	if (medium):
		medium_phrase = "It's medium is " + medium + ". "
	
	r.sms(phrase)
	r.sms(medium_phrase)
	
	return str(r)
