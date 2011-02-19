import cgi
import os
import sys
import urllib2
import datetime

from datetime import timedelta
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class UrlItem(db.Model):
	owner = db.UserProperty()
	url = db.StringProperty()
	date = db.DateTimeProperty(auto_now_add=True)
	next_run = db.DateTimeProperty()

class MainPage(webapp.RequestHandler):
	def get(self):
		if not users.get_current_user():
			self.redirect(users.create_login_url(self.request.uri))
		
		query = UrlItem.all()
		query.filter("owner =", users.get_current_user())
		query.order("-date")
		url_items = query.fetch(10)

		if users.get_current_user():
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'

		template_values = {
			'current_user': users.get_current_user(),
			'url_items': url_items,
			'url': url,
			'url_linktext': url_linktext,
		}

		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, template_values))

class NewController(webapp.RequestHandler):
	def post(self):
		url_item = UrlItem()

		if users.get_current_user():
			url_item.owner = users.get_current_user()
		else:
			return

		url_item.url = self.request.get('url')
		url_item.put()
		self.redirect('/')

class PingController(webapp.RequestHandler):
	def get(self):
		query = UrlItem.all()
		url_items = query.fetch(10)
		
		self.response.out.write('<ul>')
		
		for url_item in url_items:
			try:
				if url_item.next_run > datetime.datetime.now():
					self.response.out.write('<li>{0}, Scheduled.</li>'.format(url_item.url))
					continue

				result = urlfetch.fetch(url_item.url)
				url_item.next_run = datetime.datetime.now() + timedelta(minutes=10)
				url_item.put()
				self.response.out.write('<li>{0}, Response status: {1}</li>'.format(url_item.url, result.status_code))
			except:
				self.response.out.write('<li>{0}, Error: {1}</li>'.format(url_item.url, sys.exc_info()))

		self.response.out.write('</ul>')

application = webapp.WSGIApplication(
									[
										('/', MainPage),
										('/new', NewController),
										('/admin/ping', PingController),
									],
									debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()