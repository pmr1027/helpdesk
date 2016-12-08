from flask import Flask, render_template, render_template_string, make_response, redirect
from flask_restful import Api, Resource, reqparse, abort

import json
import string
import random
from datetime import datetime
import dateutil.parser as dparser
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

def is_updateable_attr(group, attr):
    return app_config['attr'].get(group,{}).get(attr, 0)


# Generate a unique ID for a new help request.
# By default this will consist of six lowercase numbers and letters.
def generate_id(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


# Respond with 404 Not Found if no help request with the specified ID exists.
def error_if_not_found(request_id, data_check):
    if request_id not in data_check:
        message = "No request with ID: {}".format(request_id)
        abort(404, message=message)

# Raises an error if the string x is empty (has zero length).
def nonempty_string(x):
    s = str(x)
    if len(x) == 0:
        raise ValueError('string is empty')
    return s



# pass in a list of differences and a type
# ensure that all the current ids are with their respective relation
def rectify(thisid, old, new, entitytype):
    if entitytype == 'events':
        ref_type_1 = Event
        ref_type_2 = Business
    else:
        ref_type_1 = Business
        ref_type_2 = Event

    rel_from = old
    print(rel_from)
    new = [] if new == None else new
    old = [] if old == None else old.keys()
    new_set = set(new)
    sym_difs = list(set(old).symmetric_difference(new_set))
    print('\nBeginning',rel_from)
    for dif in sym_difs:
        rel_to = data[entitytype][dif]
        if rel_to:
            print(rel_to['relations'])
            if rel_to['relations'] == None:
                rel_to['relations'] = {}
            if dif in new_set:
                if len(rel_to['relations'])==0:
                    rel_from.setdefault(dif,{"@id": api.url_for(ref_type_1, request_id=dif, _external=True)})
                    rel_to['relations'].setdefault(thisid, {"@id": api.url_for(ref_type_2,request_id=thisid,_external=True)})
                    continue
                n_set = set(rel_to['relations'])
                n_set.add(thisid)
                rel_from.setdefault(dif,{"@id": api.url_for(ref_type_1, request_id=dif, _external=True)})
                rel_to['relations'].setdefault(thisid, {"@id": api.url_for(ref_type_2, request_id=thisid, _external=True)})
            else:
                n_set = set(rel_to['relations'])
                n_set.discard(thisid)
                if n_set == None:
                    n_set = {}
                rel_to['relations'].pop(thisid,None)
                rel_from.pop(dif,None)
    print('\nEnding',rel_from)




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

def parserUpdateArgs(parser, elements, expected):
    for idx in range(len(elements)):
        parser.add_argument(elements[idx], type=expected[idx])



# Given the data for a request, generate an HTML representation
# of that help request.
def render_request_as_html(entity, types, html):
    if entity['relations'] == None:
        relations = []
    else:
         relations = entity['relations'].keys()
    if types == TYPES[0]:
        rel = data['events']
    else:
        rel = data['businesses']
    return render_template(
        html+'+microdata+rdfa.html',
        entity=entity,
        appconfig=app_config,
        activeitem=types,
        cities=app_config['addresses']['cities'].keys(),
        states=app_config['addresses']['states'],
        postalcodes=app_config['addresses']['cities']['Chapel Hill'],
        categories=app_config['categories'][types],
        relations= {
        'rels': rel,
        'selected': set(relations)
        },
        #{x:rel[x]['name']} for x in entity['relations']],
        jsonld=json.dumps(entity)
        )


# Given the data for a list of requests, generate an HTML representation
# of that list.
def render_list_as_html(lists, types, html):
    if types == TYPES[0]:
        rel = data['events']
    else:
        rel = data['businesses']
    jsonldbuild = {"@context":{}}
    jsonldbuild['@context'].setdefault(html, data['@context'][html])
    jsonldbuild.setdefault(html, data[html])
    return render_template(
        html+'+microdata+rdfa.html',
        entity=lists,
        appconfig=app_config,
        activeitem=types,
        cities=app_config['addresses']['cities'].keys(),
        states=app_config['addresses']['states'],
        postalcodes=app_config['addresses']['cities']['Chapel Hill'],
        categories=app_config['categories'][types],
        relations=rel,
        jsonld=json.dumps(jsonldbuild)
        )

new_business_parser = reqparse.RequestParser()
parserArgs(new_business_parser, ['name','category','description','streetAddress','postalCode','state','city','openingHours'])
new_business_parser.add_argument('relations', type=str, action='append')
class BusinessList(Resource):
    # Respond with an HTML representation of the help request list, after
    # applying any filtering and sorting parameters.
    def get(self):
        query = query_parser.parse_args()
        return make_response(
            render_list_as_html(
                filter_and_sort(types='businesses'), TYPES[0], 'businesses'), 200)

    # Add a new help request to the list, and respond with an HTML
    # representation of the updated list.
    def post(self):
        reqargs = new_business_parser.parse_args()
        entity = {}
        request_id = generate_id()
        # this is wasteful! was using url but didn't seem to work :{
        entity['@context'] =  app_config['contexts']['business']
        entity['description'] = reqargs['description']
        entity['name'] = reqargs['name']
        entity['openingHours'] = reqargs['openingHours']
        entity['@id'] = 'business/' + request_id
        entity['category'] = reqargs['category']
        entity['@type'] = reqargs['category'].replace(" ", "")
        entity['address'] = {
           "@type": "PostalAddress",
           "addressCountry": "United States",
           "addressLocality": reqargs['city'],
           "addressRegion": reqargs['state'],
           "postalCode": reqargs['postalCode'],
           "streetAddress": reqargs['streetAddress']
        }
        entity['relations'] = {}
        rectify(request_id, entity['relations'], reqargs['relations'], 'events')
        data['businesses'][request_id] = entity

        file_write(DATASE_FILE, data)
        return make_response(
            render_list_as_html(
                filter_and_sort(types='businesses'),  TYPES[0], 'businesses'), 201)

# Define our help request resource.
class Business(Resource):
    business_parser = reqparse.RequestParser();
    parserUpdateArgs(business_parser,
    ['name','openingHours','address.addressRegion','address.addressLocality',
    'address.streetAddress','address.postalCode','description','category','changed'],
    [str,str,str,str,str,str,str,str,str])
    business_parser.add_argument('relations', type=str, action='append')

    # If a help request with the specified ID does not exist,
    # respond with a 404, otherwise respond with an HTML representation.
    def get(self, request_id):
        error_if_not_found(request_id, data['businesses'])
        return make_response(
             render_request_as_html(
                data['businesses'][request_id],TYPES[0], 'business'), 200)

    # If a help request with the specified ID does not exist,
    # respond with a 404, otherwise update the help request and respond
    # with the updated HTML representation.
    def patch(self, request_id):
        error_if_not_found(request_id,data['businesses'])
        request = data['businesses'][request_id]
        update = self.business_parser.parse_args()
        for key in update['changed'].split(','):
            if is_updateable_attr('businesses', key):
                request_deeper = request
                traverse = key.split('.')
                t = key
                for k in traverse:
                    if k == traverse[-1]:
                        t = k
                        break
                    request_deeper = request_deeper[k]
                if key == 'category':
                    request_deeper[t] = update[key]
                    request['@type'] = update[key].replace(" ", "")
                    continue
                elif key == 'relations':
                    print(request_deeper[t])
                    rectify(request_id, request_deeper[t], update[key], 'events')
                    continue
                request_deeper[t] = update[key]

        file_write(DATASE_FILE, data)
        return make_response(
            render_request_as_html(request, TYPES[0],'business'), 200)
    def delete(self, request_id):
        error_if_not_found(request_id,data['businesses'])
        rectify(request_id, data['businesses'][request_id]['relations'], [], 'events')
        data['businesses'].pop(request_id, None)
        file_write(DATASE_FILE, data)
        res =  make_response('', 204)
        res.headers.set('Location', api.url_for(BusinessList))
        return res

# Define a resource for getting a JSON representation of a BusinessList.
class BusinessListAsJSON(Resource):
    def get(self):
        jsonldbuild = {
        "@context": {"businesses": data['@context']['businesses']},
        "businesses": data['businesses']
        }
        return jsonldbuild

# Define a resource for getting a JSON representation of a Business.
class BusinessAsJSON(Resource):
    # If a request with the specified ID does not exist,
    # respond with a 404, otherwise respond with a JSON representation.
    def get(self, request_id):
        error_if_not_found(request_id,data['businesses'])
        return data['businesses'][request_id]






new_event_parser = reqparse.RequestParser()
parserArgs(new_event_parser, ['name','category','description','streetAddress',
'postalCode','state','city','startdate.date','startdate.time','enddate.date','enddate.time'])
class EventList(Resource):
    # Respond with an HTML representation of the help request list, after
    # applying any filtering and sorting parameters.
    def get(self):
        query = query_parser.parse_args()
        return make_response(
            render_list_as_html(
                filter_and_sort(types='events'), TYPES[1], 'events'), 200)

    # Add a new help request to the list, and respond with an HTML
    # representation of the updated list.
    def post(self):
        new_event_parser.add_argument('relations', type=str, action='append')
        reqargs = new_event_parser.parse_args()

        if reqargs['relations'] == None:
            reqargs['relations'] = []
        entity = {}
        request_id = generate_id()
        # I know they don't have to be listed out this way, but hey
        #app.url_for('static', filename='jsonld/context.event.jsonld', _external=True)
        entity['@context'] = app_config['contexts']['event']
        entity['description'] = reqargs['description']
        entity['name'] = reqargs['name']
        entity['startDate'] = dparser.parse(reqargs['startdate.date']+' '+reqargs['startdate.time']).isoformat()
        entity['endDate'] = dparser.parse(reqargs['enddate.date']+' '+reqargs['enddate.time']).isoformat()
        entity['@id'] = 'events/' + request_id
        entity['category'] = reqargs['category']
        entity['@type'] = reqargs['category'].replace(" ", "")
        entity['address'] = {
           "@type": "PostalAddress",
           "addressCountry": "United States",
           "addressLocality": reqargs['city'],
           "addressRegion": reqargs['state'],
           "postalCode": reqargs['postalCode'],
           "streetAddress": reqargs['streetAddress']
        }
        entity['relations'] = {}
        rectify(request_id, entity['relations'], reqargs['relations'], 'businesses')
        data['events'][request_id] = entity

        file_write(DATASE_FILE, data)
        return make_response(
            render_list_as_html(
                filter_and_sort(types='events'),  TYPES[1], 'events'), 201)

# Define our help request resource.
class Event(Resource):
    event_parser = reqparse.RequestParser();
    parserUpdateArgs(event_parser,
    ['name','time','address.addressRegion','address.addressLocality',
    'address.streetAddress','address.postalCode','description','category','changed',
    'startDate.date','startDate.time','endDate.date','endDate.time'],
    [str,str,str,str,str,str,str,str,str,str,str,str,str])
    event_parser.add_argument('relations', type=str, action='append')

    # If a help request with the specified ID does not exist,
    # respond with a 404, otherwise respond with an HTML representation.
    def get(self, request_id):
        error_if_not_found(request_id, data['events'])
        return make_response(
            render_request_as_html(
                data['events'][request_id], TYPES[1], 'event'), 200)

    # If a help request with the specified ID does not exist,
    # respond with a 404, otherwise update the help request and respond
    # with the updated HTML representation.
    def patch(self, request_id):
        error_if_not_found(request_id,data['events'])
        request = data['events'][request_id]
        update = self.event_parser.parse_args()
        for key in update['changed'].split(','):
            if is_updateable_attr('events', key):
                request_deeper = request
                traverse = key.split('.')
                t = key
                if 'startDate' in key or 'endDate' in key:
                    # not the most efficient way, but it seems to work
                    request[traverse[0]] = dparser.parse(update[traverse[0]+'.date']
                    +' '+update[traverse[0]+'.time']).isoformat()
                    continue
                for k in traverse:
                    if k == traverse[-1]:
                        t = k
                        break
                    request_deeper = request_deeper[k]
                if key == 'category':
                    request_deeper[t] = update[key]
                    request['@type'] = update[key].replace(" ", "")
                    continue
                elif key == 'relations':
                    rectify(request_id, request_deeper[t], update[key], 'businesses')
                    continue
                request_deeper[t] = update[key]

        file_write(DATASE_FILE, data)
        return make_response(
            render_request_as_html(request, TYPES[1],'event'), 200)

    def delete(self, request_id):
        error_if_not_found(request_id,data['events'])
        rectify(request_id, data['events'][request_id]['relations'], [], 'businesses')
        data['events'].pop(request_id, None)
        file_write(DATASE_FILE, data)
        res =  make_response('', 204)
        res.headers.set('Location', api.url_for(EventList))
        return res


# Define a resource for getting a JSON representation of a EventList.
class EventListAsJSON(Resource):
    def get(self):
        jsonldbuild = {
        "@context": {"events": data['@context']['events']},
        "events": data['events']
        }
        return jsonldbuild

# Define a resource for getting a JSON representation of a Event.
class EventAsJSON(Resource):
    # If a request with the specified ID does not exist,
    # respond with a 404, otherwise respond with a JSON representation.
    def get(self, request_id):
        error_if_not_found(request_id,data['events'])
        return data['events'][request_id]

#####################################################################

# Assign URL paths to our resources.
app = Flask(__name__)
api = Api(app)

#Businesses
api.add_resource(BusinessList, '/businesses')
api.add_resource(Business, '/business/<string:request_id>')
## JSON
api.add_resource(BusinessListAsJSON, '/businesses.json')
api.add_resource(BusinessAsJSON, '/business/<string:request_id>.json')

# Events
api.add_resource(EventList, '/events')
api.add_resource(Event, '/event/<string:request_id>')
## JSON
api.add_resource(EventListAsJSON, '/events.json')
api.add_resource(EventAsJSON, '/event/<string:request_id>.json')


# Redirect from the index to the list of help requests.
@app.route('/')
def index():
    return redirect(api.url_for(BusinessList), code=303)


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

@app.template_filter('getDate')
def format_getDate(value):
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S").strftime('%Y-%m-%d')
app.jinja_env.filters['getDate'] = format_getDate

@app.template_filter('getTime')
def format_getTime(value):
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S").strftime('%H:%M')
app.jinja_env.filters['getTime'] = format_getTime

# Start the server.
#if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=8888, debug=True)
