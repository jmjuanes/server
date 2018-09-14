import os
import logging
import mimetypes
import json

import webapp2
import cloudstorage as gcs

# Import configuration
with open("config.json") as f:
    config = json.load(f)

# Render an error message
def render_error(self, code, message):
    self.response.set_status(code)
    return self.response.write(message)

# Render a static fil
def render_static(self, code, file_name):
    file_path = os.path.join(os.path.dirname(__file__), "static/" + file_name)
    with open(file_path, "r") as f:
        file_content = f.read()
    self.response.content_type = "text/html"
    self.response.set_status(code)
    return self.response.write(file_content)

# Parse a path and get the file object information
def parse_file(request):
    file_object = {}
    file_object["content"] = ""
    file_object["storage_path"] = ""
    file_object["extname"] = os.path.splitext(request.path)[1]
    # Get the real file pathname
    if file_object["extname"] == "":
        file_object["pathname"] = os.path.join(request.path, config["entry_file"])
    else:
        file_object["pathname"] = request.path
    # Get the file mime type
    file_object["mime_type"] = get_mimetype(file_object["pathname"])
    return file_object

# Get the subdomain of the request host
def get_subdomain(request):
    subdomain = ".".join(request.host.split(".")[:-2])
    return config["root_subdomain"] if subdomain == "" else subdomain

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
        if self.request.path in config["ignore_paths"]:
            return render_error(self, 404, "Not found")
        # Get the file object
        file_object = parse_file(self.request)
        try:
            # Get the GCS file path
            subdomain = get_subdomain(self.request)
            file_object["storage_path"] = "/" + config["bucket_name"] + "/" + subdomain + file_object["pathname"]
            # logging.warning("Reading file " + file_object["storage_path"])
            # Open the file from cloud storage
            gcs_file = gcs.open(file_object["storage_path"], mode="r")
            file_object["content"] = gcs_file.read()
            gcs_file.close()
            # Check for not HTML filei to add the cache header
            # https://cloud.google.com/appengine/docs/standard/python/config/appref#static_cache_expiration
            # https://developers.google.com/web/fundamentals/performance/optimizing-content-efficiency/http-caching
            if file_object["extname"] != ".html":
                # Save on cache for 1 hour
                self.response.headers["Cache-Control"] = "private, max-age=3600"
            else:
                # Do not save on cache
                self.response.headers["Cache-Control"] = "no-cache"
            # Set the mime-type
            self.response.content_type = file_object["mime_type"]
            # Write the file content and finish the request
            return self.response.write(file_object["content"])
        except:
            # Render the 404 error page
            logging.error("Error reading file from " + file_object["storage_path"])
            logging.error("Requested path: " + file_object["pathname"])
            return render_static(self, 404, "error.html")
        # Something went wrong
        logging.critical("Internal error reading file from " + file_object["storage_path"])
        return render_error(self, 500, "Internal server error")

# Create the app
app = webapp2.WSGIApplication([
        webapp2.Route('/<:.*>', handler=MainHandler)
    ], debug=True)

