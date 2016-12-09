This is an example of a simple web API implemented using
[Flask](http://flask.pocoo.org/) and
[Flask-RESTful](http://flask-restful.readthedocs.org/en/latest/).

To run it:

1. Install required dependencies:
   ```
   $ pip install -r requirements.txt
   ```
   [Flask](http://flask.pocoo.org/docs/0.10/installation/#installation)
   and
   [Flask-RESTful](http://flask-restful.readthedocs.org/en/latest/installation.html) to run `server.py`
   and [RDFLib](http://rdflib.readthedocs.org/en/latest/) and [JSONLD for RDFLib](https://github.com/RDFLib/rdflib-jsonld) to run the `extractdata.py` script or the `another-server.py` service.

2. Run the helpdesk server:
   ```
   $ python server.py
   ```
   Alternatively, you can access the service running here: http://aeshin.org:5555/requests

3. Use the `extractdata.py` script to examine the triples found in various representations of the helpdesk resources.

   RDFa/microdata for the list of help requests:
   ```
   $ python extractdata.py http://aeshin.org:5555/requests
   ```
   JSON-LD for the list of help requests:
   ```
   $ python extractdata.py http://aeshin.org:5555/requests.json
   ```
   RDFa/microdata for an individual help request:
   ```
   $ python extractdata.py http://aeshin.org:5555/request/fhs6jo
   ```
   JSON-LD for an individual help request:
   ```
   $ python extractdata.py http://aeshin.org:5555/request/fhs6jo.json
   ```

4. Run the contacts server for an example of a service calling another service:
   ```
   $ python another-server.py
   ```
   Alternatively, you can access the service running here: http://aeshin.org:5556/contacts.json

---
# Run on GCP
1. App Engine Files
   * appengine_config.py
   * app.yaml
   * vendor.py

2. Create App Engine Project
   [App Engine](https://appengine.google.com/)

3. Clone repository
   ```
   $ git clone <repository url>
   ```

4. Install required dependencies into lib:
   ```
   $ cd <project folder>
   $ pip install -r requirements.txt -t ./lib
   ```

4. Test configuration and preview in browser:
   ```
   $ dev_appserver.py ./app.yaml
   ```

5. Deploy App:
   ```
   $ gcloud app deploy app.yaml --project <project name>
   ```

---

#Part 2

<!-- business -->
##Business(es)
<dl>
  <dt><code>bs</code></dt>
  <dd>May appear to indicate a business.</dd>
  <dt><code>title</code></dt>
  <dd>May appear within <code>bs</code>. Indicates the business's title</dd>
  <dt><code>cat</code></dt>
  <dd>May appear within <code>bs</code>. Indicates the business's type (category)</dd>
  <dt><code>time</code></dt>
  <dd>May appear within <code>bs</code>. Indicates the business's hours of operation (times of operation)</dd>
  <dt><code>location</code></dt>
  <dd>May appear within <code>bs</code>. Indicates the business's location.</dd>
  <dt><code>address</code></dt>
  <dd>May appear within <code>location</code>. Indicates the business's location address.</dd>
  <dt><code>street</code></dt>
  <dd>May appear within <code>address</code>. Indicates the business's location address street.</dd>
  <dt><code>city</code></dt>
  <dd>May appear within <code>address</code>. Indicates the business's location address city.</dd>
  <dt><code>state</code></dt>
  <dd>May appear within <code>address</code>. Indicates the business's location address state.</dd>
  <dt><code>view</code></dt>
  <dd>May appear within <code>bs</code>. Indicates the business's alternate views.</dd>
  <dt><code>url</code></dt>
  <dd>May appear within <code>view</code>. Indicates the business's related url.</dd>
  <dt><code>details</code></dt>
  <dd>May appear on a <code>url</code> within <code>view</code> as a <code>rel</code>
    attribute. Indicates the business's details url.</dd>
  <dt><code>bss-ls-url</code></dt>
  <dd>May appear within <code>view</code>. Indicates a businesses list (collection) URL.</dd>
  <dt><code>collection</code></dt>
  <dd>May appear on a <code>bss-ls-url</code> within <code>view</code> as a <code>rel</code>
    attribute. Indicates a listing (collection) of businesses.</dd>
  <dt><code>update</code></dt>
  <dd>May appear on a form submission control. Sends update information to the server.</dd>
  <dt><code>bss</code></dt>
  <dd>May appear to indicate a list (collection) of businesses.</dd>
  <dt><code>add</code></dt>
  <dd>May appear on a form submission control within <code>bss</code>. Adds a business to the list (collection).</dd>
</dl>
<!-- /business -->
---
<!-- event -->
##Event(s)
<dl>
  <dl>
    <dt><code>ev</code></dt>
    <dd>May appear to indicate a event.</dd>
    <dt><code>title</code></dt>
    <dd>May appear within <code>ev</code>. Indicates the event's title</dd>
    <dt><code>cat</code></dt>
    <dd>May appear within <code>ev</code>. Indicates the event's type (category)</dd>
    <dt><code>time</code></dt>
    <dd>May appear within <code>ev</code>. Indicates the event's hours of operation (times of operation)</dd>
    <dt><code>location</code></dt>
    <dd>May appear within <code>ev</code>. Indicates the event's location.</dd>
    <dt><code>address</code></dt>
    <dd>May appear within <code>location</code>. Indicates the event's location address.</dd>
    <dt><code>street</code></dt>
    <dd>May appear within <code>address</code>. Indicates the event's location address street.</dd>
    <dt><code>city</code></dt>
    <dd>May appear within <code>address</code>. Indicates the event's location address city.</dd>
    <dt><code>state</code></dt>
    <dd>May appear within <code>address</code>. Indicates the event's location address state.</dd>
    <dt><code>view</code></dt>
    <dd>May appear within <code>ev</code>. Indicates the event's alternate views.</dd>
    <dt><code>url</code></dt>
    <dd>May appear within <code>view</code>. Indicates the event's related url.</dd>
    <dt><code>details</code></dt>
    <dd>May appear on a <code>url</code> within <code>view</code> as a <code>rel</code>
      attribute. Indicates the event's details url.</dd>
    <dt><code>evs-ls-url</code></dt>
    <dd>May appear within <code>view</code>. Indicates a events list (collection) URL.</dd>
    <dt><code>collection</code></dt>
    <dd>May appear on a <code>evs-ls-url</code> within <code>view</code> as a <code>rel</code>
      attribute. Indicates a listing (collection) of events.</dd>
    <dt><code>update</code></dt>
    <dd>May appear on a form submission control. Sends update information to the server.</dd>
    <dt><code>evs</code></dt>
    <dd>May appear to indicate a list (collection) of events.</dd>
    <dt><code>add</code></dt>
    <dd>May appear on a form submission control within <code>evs</code>. Adds an event to the list (collection).</dd>
  </dl>
</dl>
