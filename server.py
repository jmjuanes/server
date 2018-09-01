import os
import webapp2
import logging
import mimetypes
import cloudstorage as gcs

from google.appengine.api import app_identity

# Send an error
def send_error(self, code, message):
    self.response.set_status(code)
    return self.response.write(message)

# Parse the filename of a path
def parse_filename(path):
    file_name, file_ext = os.path.splitext(path)
    if file_ext == "":
        path = os.path.join(path, "index.html")
    return path

# Extract the subdoman
def parse_subdomain(host):
    subdomain = ".".join(host.split(".")[:-2])
    if subdomain == "":
        return "www"
    else:
        return subdomain

# Get the mimetype from an extension
# Extracted from: https://stackoverflow.com/a/45459425
def get_mimetype(filename):
    file_type, file_encoding = mimetypes.guess_type(filename)
    return file_type or "application/octet-stream"

# Main web handler
class MainHandler(webapp2.RequestHandler):
    def get(self, *args, **kwargs):
        # Check for siimple.juanes.xyz domain
        if self.request.host == "siimple.juanes.xyz":
            return self.redirect("https://www.siimple.xyz")
        # Ignore favicon path
        if self.request.path == "/favicon.ico":
            return send_error(self, 404, "Not found")
        # Get the service
        service_name = parse_subdomain(self.request.host)
        # Get the bucket name
        bucket_name = os.environ.get("BUCKET_NAME", app_identity.get_default_gcs_bucket_name())
        try:
            # Get the file path to open
            file_name = parse_filename(self.request.path)
            file_path = "/" + bucket_name + "/" + service_name + file_name
            # Write the mimetype
            self.response.content_type = get_mimetype(file_name)
            # Open the file from cloud storage
            gcs_file = gcs.open(file_path)
            file_content = gcs_file.read()
            gcs_file.close()
            # Send the file content and finishe the request
            return self.response.write(file_content)
        except:
            return send_error(self, 404, "Not found")
        return send_error(self, 500, "Internal server error")

# Create the app
app = webapp2.WSGIApplication([
    webapp2.Route('/<:.*>', handler=MainHandler)
    ], debug=True)

