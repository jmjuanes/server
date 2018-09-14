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
def render_static(self, file_name):
    file_path = os.path.join(os.path.dirname(__file__), "static/" + file_name)
    with open(file_path, "r") as f:
        file_content = f.read()
    self.response.content_type = "text/html"
    return self.response.write(file_content)

# Parse the filename of a path
def parse_filename(path):
    file_name, file_ext = os.path.splitext(path)
    if file_ext == "":
        path = os.path.join(path, config["entry_file"])
    return path

# Extract the subdoman
def parse_subdomain(host):
    subdomain = ".".join(host.split(".")[:-2])
    if subdomain == "":
        return config["root_subdomain"]
    else:
        return subdomain

# Get the mimetype from an extension
# Extracted from: https://stackoverflow.com/a/45459425
def get_mimetype(filename):
    file_type = mimetypes.guess_type(filename)[0]
    return file_type or "application/octet-stream"

# Main web handler
class MainHandler(webapp2.RequestHandler):
    def get(self, *args, **kwargs):
        # Check for redirection domain
        if self.request.host in config["redirects"]:
            return self.redirect(config["redirects"][sef.request.host])
        # Check for ignored path
        if self.request.path in config["ignore_paths"]:
            return render_error(self, 404, "Not found")
        # Get the service
        service_name = parse_subdomain(self.request.host)
        try:
            # Parse the file name
            file_ext = os.path.splitext(self.request.path)[1]
            if file_ext == "":
                file_name = os.path.join(self.request.path, config["entry_file"])
            else:
                file_name = self.request.path
            # Get the GCS file path
            file_path = "/" + config["bucket_name"] + "/" + service_name + file_name
            # logging.warning("Reading file " + file_path)
            # Open the file from cloud storage
            gcs_file = gcs.open(file_path)
            file_content = gcs_file.read()
            gcs_file.close()
            # Send the file content and finishe the request
            self.response.content_type = get_mimetype(file_name)
            # Check for not HTML filei to add the cache header
            # https://cloud.google.com/appengine/docs/standard/python/config/appref#static_cache_expiration
            # https://developers.google.com/web/fundamentals/performance/optimizing-content-efficiency/http-caching
            if file_ext != ".html":
                # Save on cache for 1 hour
                self.response.headers["Cache-Control"] = "private, max-age=3600"
            else:
                # Do not save on cache
                self.response.headers["Cache-Control"] = "no-cache"
            # Write the file content and finish the request
            return self.response.write(file_content)
        except:
            # Render the 404 error page
            self.response.set_status(404)
            return render_static(self, "error.html")
        return render_error(self, 500, "Internal server error")

# Create the app
app = webapp2.WSGIApplication([
        webapp2.Route('/<:.*>', handler=MainHandler)
    ], debug=True)

