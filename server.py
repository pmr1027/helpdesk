from flask import Flask, render_template, render_template_string, make_response, redirect
from flask.ext.restful import Api, Resource, reqparse, abort

import json
import string
import random
from datetime import datetime
# Define our priority levels.
# These are the values that the "priority" property can take on a help request.
PRIORITIES = ('closed', 'low', 'normal', 'high')
TYPES = ('business', 'event')

DATASE_FILE = 'data.jsonld'
CONFIG_FILE = 'app.config.json'

def file_write(path, tdata):
    with open(path, 'w') as outfile:
        json.dump(tdata, outfile)

# Load data from disk.
# This simply loads the data from our "database," which is just a JSON file.
with open('data.jsonld', 'r') as read:
    data = json.load(read)

with open('app.config.json', 'r') as read:
    app_config = json.load(read)

#with open('categories.json', 'r') as read:
#    data_categories = json.load(read)


# Generate a unique ID for a new help request.
# By default this will consist of six lowercase numbers and letters.
def generate_id(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


# Respond with 404 Not Found if no help request with the specified ID exists.
def error_if_not_found(request_id, data_check):
    if request_id not in data_check:
        message = "No help request with ID: {}".format(request_id)
        abort(404, message=message)

# Raises an error if the string x is empty (has zero length).
def nonempty_string(x):
    s = str(x)
    if len(x) == 0:
        raise ValueError('string is empty')
    return s

# Specify the parameters for filtering and sorting help requests.
# See `filter_and_sort_helprequests` above.
query_parser = reqparse.RequestParser()
query_parser.add_argument(
    'query', type=str, default='')
query_parser.add_argument(
    'sort_by', type=str, choices=('name', 'name'), default='name')

# Filter and sort a list of helprequests.
def filter_and_sort(query='', sort_by='name', types=None):

    # Returns True if the query string appears in the help request's
    # title or description.
    def matches_query(item):
        (request_id, helprequest) = item
        text = helprequest['name'] + helprequest['description']
        return query.lower() in text

    # Returns the help request's value for the sort property (which by
    # default is the "time" property).
    def get_sort_value(item):
        (helprequest_id, helprequest) = item
        return helprequest[sort_by]

    filtered_helprequests = filter(matches_query, data[types].items())

    return sorted(filtered_helprequests, key=get_sort_value, reverse=True)

#####################################################################
########################### Utilities ###############################
# Specify the data necessary to create a new help request.
# "from", "title", and "description" are all required values.
def parserArgs(parser, elements):
    for arg in elements:
        parser.add_argument(
            arg, type=nonempty_string, required=True,
            help="'{}' is a required value".format(arg))

# Given the data for a list of help requests, generate an HTML representation
# of that list.
def render_list_as_html(lists, types, html):
    jsonldbuild = {"@context":{}}
    jsonldbuild['@context'].setdefault(html, data['@context'][html])
    jsonldbuild.setdefault(html, data[html])
    print(json.dumps(jsonldbuild))
    return render_template(
        html+'+microdata+rdfa.html',
        entity=lists,
        appconfig=app_config,
        activeitem=types,
        cities=app_config['addresses']['cities'].keys(),
        states=app_config['addresses']['states'],
        postalcodes=app_config['addresses']['cities']['Chapel Hill'],
        categories={
          'len': len(app_config['categories'][types]),
          'list': app_config['categories'][types]
        },
        relations={
          'len': len(app_config['categories'][types]),
          'list': app_config['categories'][types]
        },
        jsonld=json.dumps(jsonldbuild)
        )

new_business_parser = reqparse.RequestParser()
parserArgs(new_business_parser, ['name','cat','description','streetAddress','postalCode','state','city','openingHours'])
class BusinessList(Resource):
    # Respond with an HTML representation of the help request list, after
    # applying any filtering and sorting parameters.
    def get(self):
        query = query_parser.parse_args()
        return make_response(
            render_list_as_html(
                filter_and_sort(**query,types='businesses'), TYPES[0], 'businesses'), 200)

    # Add a new help request to the list, and respond with an HTML
    # representation of the updated list.
    def post(self):
        reqargs = new_business_parser.parse_args()
        entity = {}
        request_id = generate_id()
        entity['@context'] = "http://schema.org"
        entity['description'] = reqargs['description']
        entity['name'] = reqargs['name']
        entity['openingHours'] = reqargs['openingHours']
        entity['@id'] = 'business/' + request_id
        entity['cat'] = int(reqargs['cat'])
        entity['@type'] = app_config['categories'][TYPES[0]][entity['cat']].replace(" ", "")
        entity['address'] = {
           "@type": "PostalAddress",
           "addressCountry": "United States",
           "addressLocality": reqargs['city'],
           "addressRegion": reqargs['state'],
           "postalCode": reqargs['postalCode'],
           "streetAddress": reqargs['streetAddress']
        }
        data['businesses'][request_id] = entity

        file_write(DATASE_FILE, data)
        return make_response(
            render_list_as_html(
                filter_and_sort(types='businesses'),  TYPES[0], 'businesses'), 201)

# Define our help request resource.
class Business(Resource):

    # If a help request with the specified ID does not exist,
    # respond with a 404, otherwise respond with an HTML representation.
    def get(self, request_id):
        error_if_not_found(request_id, data['businesses'])
        return make_response(
            render_business_request_as_html(
                data['businesses'][request_id]), 200)

    # If a help request with the specified ID does not exist,
    # respond with a 404, otherwise update the help request and respond
    # with the updated HTML representation.
    def patch(self, helprequest_id):
        error_if_not_found(helprequest_id)
        helprequest = data['helprequests'][helprequest_id]
        update = update_helprequest_parser.parse_args()
        helprequest['priority'] = update['priority']
        if len(update['comment'].strip()) > 0:
            helprequest.setdefault('comments', []).append(update['comment'])
        return make_response(
            render_helprequest_as_html(helprequest), 200)


#####################################################################

# Assign URL paths to our resources.
app = Flask(__name__)
api = Api(app)
# api.add_resource(HelpRequestList, '/requests')
# api.add_resource(HelpRequestListAsJSON, '/requests.json')
api.add_resource(Business, '/business/<string:request_id>')
# api.add_resource(HelpRequestAsJSON, '/request/<string:helprequest_id>.json')
api.add_resource(BusinessList, '/businesses')
#greeting
#api.add_resource(Greeting, '/greeting/<string:role>')
#api.add_resource(Greetings, '/greetings')

# Redirect from the index to the list of help requests.
@app.route('/')
def index():
    return redirect(api.url_for(HelpRequestList), code=303)


# This is needed to load JSON from Javascript running in the browser.
@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response

@app.template_filter('datetime')
def format_datetime(value):
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S").strftime('%B %d, %Y at %I:%M%p')
app.jinja_env.filters['datetime'] = format_datetime

# Start the server.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)
