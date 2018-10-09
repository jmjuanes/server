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
def render_error(self, code, template):
    template_path = os.path.join(os.path.dirname(__file__), "templates/error.html")
    template_values = {
        "site": config["site"], 
        "content": config["templates"][template]
    }
    # Update the response
    self.response.set_status(code)
    self.response.content_type = "text/html"
    # Send the error page
    return self.response.write(template(template_path, template_values))

# Get the subdomain of the request host
def get_subdomain(hostname):
    return ".".join(hostname.split(".")[:-2])

# Get the extname from a path
def get_extname(path):
    return os.path.splitext(path)[1]

# Get the mimetype from a path
# Extracted from: https://stackoverflow.com/a/45459425
def get_mimetype(path):
    return mimetypes.guess_type(path)[0] or "application/octet-stream"

# Main web handler
class MainHandler(webapp2.RequestHandler):
    def get(self, *args, **kwargs):
        # Check for redirection domain
        if self.request.host in config["host"]["redirects"]:
            return self.redirect(config["host"]["redirects"][sef.request.host])
        # Check for ignored path
        if self.request.path in config["ignorePaths"]:
            return self.abort(404)
        # Get the GCS file path
        file_path = "/" + config["storage"]["bucket"] + config["storage"]["directoryRoot"]
        # Check for subdomain mapping
        if config["host"]["subdomains"]["mapToFolder"] == True:
            subdomain = get_subdomain(self.request.host)
            # Check for empty subdomain
            if subdomain == "":
                subdomain = config["host"]["subdomains"]["default"]
            # Check for special subdomain mapping
            # if subdomain in config["host"]["subdomain"]["mappings"]:
            #     subdomain = config["host"]["subdomain"]["mappings"]
            # Append the subdomain folder to the file path
            file_path = file_path + subdomain + "/"
        # Add the requested path
        file_path = file_path + self.request.path
        # Check the extension of the file
        file_extname = get_extname(file_path)
        if file_extname == "":
            file_path = file_path + config["storage"]["directoryIndex"]
            file_extname = get_extname(file_path)
        # Normalize the generated path
        file_path = os.path.normpath(file_path)
        try:
            # Open the file from cloud storage
            # logging.warning("Reading file " + file_object["storage_path"])
            gcs_file = gcs.open(file_path, mode="r")
            file_content = gcs_file.read()
            gcs_file.close()
            # Check if cache is enabled
            if config["cache"]["enabled"] == True:
                # Check if this file should be cached
                # https://cloud.google.com/appengine/docs/standard/python/config/appref#static_cache_expiration
                # https://developers.google.com/web/fundamentals/performance/optimizing-content-efficiency/http-caching
                if file_extname not in config["cache"]["ignore"]:
                    self.response.headers["Cache-Control"] = config["cache"]["default"]
                else:
                    self.response.headers["Cache-Control"] = "no-cache"
            # Write the file content and finish the request
            self.response.content_type = get_mimetype(file_path)
            return self.response.write(file_content)
        except:
            logging.error("Error reading file from " + file_path)
            logging.error("Requested path: " + self.request.path)
            # Render the 404 error page
            return render_error(self, 404, "not-found")
        # Something went wrong
        logging.critical("Internal error reading file from " + file_path)
        return self.abort(500)

# Create the app
app = webapp2.WSGIApplication([
        webapp2.Route('/<:.*>', handler=MainHandler)
    ], debug=True)

