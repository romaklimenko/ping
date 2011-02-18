import os
import cgi


from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class UrlItem(db.Model):
	owner = db.UserProperty()
	url = db.StringProperty()
	date = db.DateTimeProperty(auto_now_add=True)

class MainPage(webapp.RequestHandler):
	def get(self):
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
			'url_items': url_items,
			'url': url,
			'url_linktext': url_linktext,
		}

		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, template_values))

class UrlItemsController(webapp.RequestHandler):
	def post(self):
		url_item = UrlItem()

		if users.get_current_user():
			url_item.owner = users.get_current_user()

		url_item.url = self.request.get('url')
		url_item.put()
		self.redirect('/')

application = webapp.WSGIApplication(
									[('/', MainPage),
									('/new', UrlItemsController)],
									debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()