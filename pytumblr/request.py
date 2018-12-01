import urllib.parse
from dataclasses import dataclass
from typing import Dict, Union, Tuple, List

import requests
from requests.exceptions import TooManyRedirects, HTTPError
from requests_oauthlib import OAuth1


@dataclass
class Reason:
    title: str
    code: int

@dataclass
class TumblrError:
    # the HTTP status code, e.g. 200
    status: int
    # the HTTP status message, e.g. 'OK'
    msg: str
    # any response data, as a dictionary
    response: Dict = None
    # any errors
    errors: List[Reason] = None


TumblrResponse = Union[TumblrError, Dict]
Status = Tuple[bool, TumblrError]


def ok(response: TumblrResponse) -> Status:
    """
    A predicate determining if the response has a non-200 status code
    :return: True if response.status == 200, False otherwise
    """
    return not isinstance(response, TumblrError), response


def created(response: TumblrError) -> Status:
    return response.status == 201, response


class TumblrRequest:
    """
    A simple request object that lets us query the Tumblr API
    """

    __version = "0.0.8"

    def __init__(self, consumer_key, consumer_secret="", oauth_token="", oauth_secret="",
                 host="https://api.tumblr.com", version=2):
        self.host = '{}/v{}'.format(host, version)
        self.oauth = OAuth1(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=oauth_token,
            resource_owner_secret=oauth_secret
        )
        self.consumer_key = consumer_key

        self.headers = {
            "User-Agent": "pytumblr/" + self.__version,
        }

    def get(self, url, params) -> TumblrResponse:
        """
        Issues a GET request against the API, properly formatting the params

        :param url: a string, the url you are requesting
        :param params: a dict, the key-value of all the paramaters needed
                       in the request
        :returns: either a dict of the returned response or a TumblrError in case of failure
        """
        url = self.host + url
        if params:
            url += "?" + urllib.parse.urlencode(params)

        try:
            resp = requests.get(url, allow_redirects=False, headers=self.headers, auth=self.oauth)
        except TooManyRedirects as e:
            resp = e.response

        return self.json_parse(resp)

    def post(self, url, params={}, files=[]) -> TumblrResponse:
        """
        Issues a POST request against the API, allows for multipart data uploads

        :param url: a string, the url you are requesting
        :param params: a dict, the key-value of all the parameters needed
                       in the request
        :param files: a list, the list of tuples of files

        :returns: a dict parsed of the JSON response
        """
        url = self.host + url
        try:
            if files:
                return self.post_multipart(url, params, files)
            else:
                data = urllib.parse.urlencode(params)
                resp = requests.post(url, data=data, headers=self.headers, auth=self.oauth)
                return self.json_parse(resp)
        except HTTPError as e:
            return self.json_parse(e.response)

    def json_parse(self, response) -> TumblrResponse:
        """
        Wraps and abstracts response validation and JSON parsing
        to make sure the user gets the correct response.

        :param response: The response returned to us from the request

        :returns: a dict of the json response
        """
        try:
            data = response.json()
        except ValueError:
            data = {'meta': {'status': 500, 'msg': 'Server Error'},
                    'response': {"error": "Malformed JSON or HTML was returned."}}

        # We only really care about the response if we succeed
        # and the error if we fail
        if data['meta']['status'] == 200:
            return data['response']
        else:
            return TumblrError(data['meta']['status'],
                               data['meta']['msg'],
                               data['response'])

    def post_multipart(self, url, params, files) -> TumblrResponse:
        """
        Generates and issues a multipart request for data files

        :param url: a string, the url you are requesting
        :param params: a dict, a key-value of all the parameters
        :param files:  a dict, matching the form '{name: file descriptor}'

        :returns: a dict parsed from the JSON response
        """
        resp = requests.post(
            url,
            data=params,
            params=params,
            files=files,
            headers=self.headers,
            allow_redirects=False,
            auth=self.oauth
        )
        return self.json_parse(resp)
