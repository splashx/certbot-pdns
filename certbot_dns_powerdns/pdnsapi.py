#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ultimately this file can be
tossed and something like
python-powerdns could be used instead.
"""

import json
import requests


class PdnsApi:

    api_key = None
    base_url = None

    def __init__(self, api_url, api_key):
        self.api_key = api_key
        self.base_path = 'api/v1'
        self.base_url = self.ensure_slash(api_url) + self.base_path

    def set_api_key(self, api_key):
        self.api_key = api_key

    def set_base_url(self, base_url):
        # implement here a V1 appending path thingy
        self.base_url = base_url
        
    def _query(self, uri, method, kwargs=None):
        headers = {
            'X-API-Key': self.api_key,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        data = json.dumps(kwargs)

        if method == "GET":
            request = requests.get(self.base_url + uri, headers=headers)
        elif method == "POST":
            request = requests.post(self.base_url + uri, headers=headers, data=data)
        elif method == "PUT":
            request = requests.put(self.base_url + uri, headers=headers, data=data)
        elif method == "PATCH":
            request = requests.patch(self.base_url + uri, headers=headers, data=data)
        elif method == "DELETE":
            request = requests.delete(self.base_url + uri, headers=headers)
        else:
            raise ValueError("Invalid method '%s'" % method)

        return None if request.status_code == 204 else request.json()

    def list_zones(self):
        return self._query("/servers/localhost/zones", "GET")

    def get_zone(self, zone_name):
        return self._query("/servers/localhost/zones/%s" % self.ensure_dot(zone_name), "GET")

    def update_zone(self, zone_name, data):
        return self._query("/servers/localhost/zones/%s" % self.ensure_dot(zone_name), "PUT", data)

    def replace_record(self, zone_name, name, type, ttl, content, disabled=False, set_ptr=False):
        return self._query("/servers/localhost/zones/%s" % self.ensure_dot(zone_name), "PATCH", {"rrsets": [
            {
                "name": self.ensure_dot(name),
                "type": type,
                "ttl": ttl,
                "changetype": "REPLACE",
                "records": [
                    {
                        "content": self.ensure_quotes(content) if type == 'TXT' else content,
                        "disabled": disabled,
                        "set-ptr": set_ptr
                    }
                ]
            }
        ]})

    def delete_record(self, zone_name, name, type):
        return self._query("/servers/localhost/zones/%s" % self.ensure_dot(zone_name), "PATCH", {"rrsets": [
            {
                "name": self.ensure_dot(name),
                "type": type,
                "changetype": "DELETE",
                "records": []
            }
        ]})

    def notify_zone(self, zone_name):
        return self._query("/servers/localhost/zones/%s/notify" % self.ensure_dot(zone_name), "PUT")

    def flush_zone_cache(self, zone_name):
        return self._query("/servers/localhost/cache/flush?domain=%s" % self.ensure_dot(zone_name), "PUT")

    def ensure_dot(self, text):
        """
        This function makes sure a string contains a dot at the end
        """
        if not text.endswith("."):
            text = text + "."
        return text

    def ensure_slash(self, text):
        """
        This function makes sure a string contains a slash at the end
        """
        if not text.endswith("/"):
            text = text + "/"
        return text

    def ensure_quotes(self, text):
        """
        This function makes sure a string contains a " at the end and beginning
        """
        if not text.endswith('"'):
            text = text + '"'
        if not text.startswith('"'):
            text =  '"' + text
        return text