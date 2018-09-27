import os
import logging
import mimetypes
import json

import webapp2
from google.appengine.ext.webapp import template
import cloudstorage as gcs

# Import configuration
with open(os.path.join(os.path.dirname(__file__), "config.json")) as f:
    config = json.load(f)

# Render an error message
def render_error(self, code, message):
    self.response.set_status(code)
    return self.response.write(message)

# Render a template file
def render_template(self, template_name, template_values):
    template_path = os.path.join(os.path.dirname(__file__), "templates/" + template_name)
    self.response.content_type = "text/html"
    return self.response.write(template(template_path, template_values))

# Parse a path and get the file object information
def parse_file(request):
    file_object = {
        "content": "",
        "storage_path": "",
        "extname": ops.path.splitext(request.path)[1],
        "pathname": request.path
    }
    # Check if path is a folder --> if yes, add the entry file path
    if file_object["extname"] == "":
        file_object["pathname"] = os.path.join(request.path, config["paths"]["entry"])
        file_object["extname"] = os.path.splitext(config["path"]["entry"])[1]
    # Get the file mime type
    file_object["mime_type"] = get_mimetype(file_object["pathname"])
    return file_object

# Get the subdomain of the request host
def get_subdomain(request):
    subdomain = ".".join(request.host.split(".")[:-2])
    subdomain = config["subdomain"]["default"] if subdomain == "" else subdomain
    # Check for special subdomain mapping
    if subdomain in config["subdomain"]["mappings"]:
        return config["subdomain"]["mappings"][subdomain]
    else:
        return "/" + subdomain

# Get the mimetype from an extension
# Extracted from: https://stackoverflow.com/a/45459425
def get_mimetype(filename):
    return mimetypes.guess_type(filename)[0] or "application/octet-stream"

# Main web handler
class MainHandler(webapp2.RequestHandler):
    def get(self, *args, **kwargs):
        # Check for redirection domain
        if self.request.host in config["redirects"]:
            return self.redirect(config["redirects"][sef.request.host])
        # Check for ignored path
        if self.request.path in config["paths"]["ignore"]:
            return render_error(self, 404, "Not found")
        # Get the file object
        file_object = parse_file(self.request)
        # Get the GCS file path
        # It has the structure "/<BUCKET>/<SUBDOMAIN>/<FILE_PATH>"
        subdomain = get_subdomain(self.request)
        file_object["storage_path"] = "/" + config["bucket"] + "/" + subdomain + file_object["pathname"]
        try:
            # Open the file from cloud storage
            # logging.warning("Reading file " + file_object["storage_path"])
            gcs_file = gcs.open(file_object["storage_path"], mode="r")
            file_object["content"] = gcs_file.read()
            gcs_file.close()
            # Check for not HTML file to add the cache header
            # https://cloud.google.com/appengine/docs/standard/python/config/appref#static_cache_expiration
            # https://developers.google.com/web/fundamentals/performance/optimizing-content-efficiency/http-caching
            if file_object["extname"] not in config["cache"]["ignore"]:
                self.response.headers["Cache-Control"] = config["cache"]["header"]
            else:
                self.response.headers["Cache-Control"] = "no-cache"
            # Set the mime-type
            self.response.content_type = file_object["mime_type"]
            # Write the file content and finish the request
            return self.response.write(file_object["content"])
        except:
            logging.error("Error reading file from " + file_object["storage_path"])
            logging.error("Requested path: " + file_object["pathname"])
            # Render the 404 error page
            self.response.set_status(404)
            return render_template(self, "not-found.html", {})
        # Something went wrong
        logging.critical("Internal error reading file from " + file_object["storage_path"])
        return render_error(self, 500, "Internal server error")

# Create the app
app = webapp2.WSGIApplication([
        webapp2.Route('/<:.*>', handler=MainHandler)
    ], debug=True)

