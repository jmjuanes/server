# Import dependencies
import os
import mimetypes
import json

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


