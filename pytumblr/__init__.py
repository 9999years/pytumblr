from typing import List, ClassVar, TypeVar, Union, Type, Tuple

from pytumblr.request import TumblrResponse, TumblrError, ok, created, Status
from . import npf
from . import types
from .helpers import validate_params, validate_blogname
from .request import TumblrRequest

T: ClassVar[TypeVar] = TypeVar('T')
Result = Union[T, TumblrError]


def _wrap(return_type: Type[T], response: TumblrResponse) -> Result[T]:
    if isinstance(response, TumblrError):
        return response
    else:
        return return_type(**response)


def _maybe_unwrap_posts(response: TumblrResponse) -> Result[List[types.Post]]:
    if isinstance(response, types.Posts):
        return response.posts
    else:
        return response


class TumblrRestClient:
    """
    A Python Client for the Tumblr API
    """

    def __init__(self, consumer_key, consumer_secret="", oauth_token="", oauth_secret="",
                 host="https://api.tumblr.com"):
        """
        Initializes the TumblrRestClient object, creating the TumblrRequest
        object which deals with all request formatting.

        :param consumer_key: a string, the consumer key of your
                             Tumblr Application
        :param consumer_secret: a string, the consumer secret of
                                your Tumblr Application
        :param oauth_token: a string, the user specific token, received
                            from the /access_token endpoint
        :param oauth_secret: a string, the user specific secret, received
                             from the /access_token endpoint
        :param host: the host that are you trying to send information to,
                     defaults to https://api.tumblr.com

        :returns: None
        """
        self.request = TumblrRequest(consumer_key, consumer_secret, oauth_token, oauth_secret, host)

    def info(self) -> Result[types.BlogInfo]:
        """
        Gets the information about the current given user

        :returns: A dict created from the JSON response
        """
        return self.send_typed_request(types.BlogInfo, "get", "/user/info")

    @validate_blogname
    def avatar(self, blogname, size=64) -> Result[types.Avatar]:
        """
        Retrieves the url of the blog's avatar

        :param blogname: a string, the blog you want the avatar for

        :returns: A dict created from the JSON response
        """
        url = "/blog/{0}/avatar/{1}".format(blogname, size)
        return self.send_typed_request(types.Avatar, "get", url)

    def likes(self, **kwargs) -> Result[types.Likes]:
        """
        Gets the current given user's likes
        :param limit: an int, the number of likes you want returned
        (DEPRECATED) :param offset: an int, the like you want to start at, for pagination.
        :param before: an int, the timestamp for likes you want before.
        :param after: an int, the timestamp for likes you want after.

            # Start at the 20th like and get 20 more likes.
            client.likes({'offset': 20, 'limit': 20})

        :returns: A dict created from the JSON response
        """
        return self.send_typed_request(types.Likes,
                                       "get", "/user/likes", kwargs, ["limit", "offset", "before", "after"])

    def following(self, **kwargs):
        """
        Gets the blogs that the current user is following.
        :param limit: an int, the number of likes you want returned
        :param offset: an int, the blog you want to start at, for pagination.

            # Start at the 20th blog and get 20 more blogs.
            client.following({'offset': 20, 'limit': 20})

        :returns: A dict created from the JSON response
        """
        return self.send_typed_request(types.Following, "get", "/user/following", kwargs, ["limit", "offset"])

    def dashboard(self, **kwargs) -> Result[types.Dashboard]:
        """
        Gets the dashboard of the current user

        :param limit: an int, the number of posts you want returned
        :param offset: an int, the posts you want to start at, for pagination.
        :param type:   the type of post you want to return
        :param since_id:  return only posts that have appeared after this ID
        :param reblog_info: return reblog information about posts
        :param notes_info:  return notes information about the posts

        :returns: A dict created from the JSON response
        """
        response = self.send_typed_request(types.Dashboard,
                                       "get", "/user/dashboard", kwargs,
                                       ["limit", "offset", "type", "since_id", "reblog_info", "notes_info"])
        if isinstance(response, types.Dashboard):
            return response.posts
        else:
            return response

    def tagged(self, tag, **kwargs) -> Result[List[types.Post]]:
        """
        Gets a list of posts tagged with the given tag

        :param tag: a string, the tag you want to look for
        :param before: a unix timestamp, the timestamp you want to start at
                       to look at posts.
        :param limit: the number of results you want
        :param filter: the post format that you want returned: html, text, raw

            client.tagged("gif", limit=10)

        :returns: a dict created from the JSON response
        """
        kwargs.update({'tag': tag})
        return _maybe_unwrap_posts(self.send_typed_request(types.Posts, "get", '/tagged', kwargs,
                                       ['before', 'limit', 'filter', 'tag', 'api_key'], True))

    @validate_blogname
    def posts(self, blogname, type=None, **kwargs) -> Result[types.BlogPosts]:
        """
        Gets a list of posts from a particular blog

        :param blogname: a string, the blogname you want to look up posts
                         for. eg: codingjester.tumblr.com
        :param id: an int, the id of the post you are looking for on the blog
        :param tag: a string, the tag you are looking for on posts
        :param limit: an int, the number of results you want
        :param offset: an int, the offset of the posts you want to start at.
        :param filter: the post format you want returned: HTML, text or raw.
        :param type: the type of posts you want returned, e.g. video. If omitted returns all post types.

        :returns: a dict created from the JSON response
        """
        if type is None:
            url = '/blog/{0}/posts'.format(blogname)
        else:
            url = '/blog/{0}/posts/{1}'.format(blogname, type)
        return self.send_typed_request(types.BlogPosts, "get", url, kwargs,
                                       ['id', 'tag', 'limit', 'offset', 'reblog_info', 'notes_info', 'filter',
                                        'api_key'],
                                       True)

    @validate_blogname
    def blog_info(self, blogname) -> Result[types.BlogInfo]:
        """
        Gets the information of the given blog

        :param blogname: the name of the blog you want to information
                         on. eg: codingjester.tumblr.com

        :returns: a dict created from the JSON response of information
        """
        url = "/blog/{0}/info".format(blogname)
        return self.send_typed_request(types.BlogInfo, "get", url, {}, ['api_key'], True)

    @validate_blogname
    def blog_following(self, blogname, **kwargs) -> Result[types.Following]:
        """
        Gets the publicly exposed list of blogs that a blog follows

        :param blogname: the name of the blog you want to get information on.
                         eg: codingjester.tumblr.com

        :param limit: an int, the number of blogs you want returned
        :param offset: an int, the blog to start at, for pagination.

            # Start at the 20th blog and get 20 more blogs.
            client.blog_following('pytblr', offset=20, limit=20})

        :returns: a dict created from the JSON response
        """
        url = "/blog/{0}/following".format(blogname)
        return self.send_typed_request(types.Following, "get", url, kwargs, ['limit', 'offset'])

    @validate_blogname
    def followers(self, blogname, **kwargs) -> Result[types.Followers]:
        """
        Gets the followers of the given blog
        :param limit: an int, the number of followers you want returned
        :param offset: an int, the follower to start at, for pagination.

            # Start at the 20th blog and get 20 more blogs.
            client.followers({'offset': 20, 'limit': 20})

        :returns: A dict created from the JSON response
        """
        url = "/blog/{0}/followers".format(blogname)
        return self.send_typed_request(types.Followers, "get", url, kwargs, ['limit', 'offset'])

    @validate_blogname
    def blog_likes(self, blogname, **kwargs) -> Result[types.Likes]:
        """
        Gets the current given user's likes
        :param limit: an int, the number of likes you want returned
        (DEPRECATED) :param offset: an int, the like you want to start at, for pagination.
        :param before: an int, the timestamp for likes you want before.
        :param after: an int, the timestamp for likes you want after.

            # Start at the 20th like and get 20 more likes.
            client.blog_likes({'offset': 20, 'limit': 20})

        :returns: A dict created from the JSON response
        """
        url = "/blog/{0}/likes".format(blogname)
        return self.send_typed_request(types.Likes, "get", url, kwargs, ['limit', 'offset', 'before', 'after'], True)

    @validate_blogname
    def queue(self, blogname, **kwargs) -> Result[List[types.Post]]:
        """
        Gets posts that are currently in the blog's queue

        :param limit: an int, the number of posts you want returned
        :param offset: an int, the post you want to start at, for pagination.
        :param filter: the post format that you want returned: HTML, text, raw.

        :returns: a dict created from the JSON response
        """
        url = "/blog/{0}/posts/queue".format(blogname)
        return _maybe_unwrap_posts(
            self.send_typed_request(types.Posts, "get", url, kwargs, ['limit', 'offset', 'filter']))

    @validate_blogname
    def drafts(self, blogname, **kwargs) -> Result[List[types.Post]]:
        """
        Gets posts that are currently in the blog's drafts
        :param filter: the post format that you want returned: HTML, text, raw.

        :returns: a dict created from the JSON response
        """
        url = "/blog/{0}/posts/draft".format(blogname)
        response = self.send_typed_request(types.Posts, "get", url, kwargs, ['filter'])
        if isinstance(response, types.Posts):
            return response.posts
        else:
            # err
            return response

    @validate_blogname
    def submission(self, blogname, **kwargs) -> Result[types.Submission]:
        """
        Gets posts that are currently in the blog's queue

        :param offset: an int, the post you want to start at, for pagination.
        :param filter: the post format that you want returned: HTML, text, raw.

        :returns: a dict created from the JSON response
        """
        url = "/blog/{0}/posts/submission".format(blogname)
        return self.send_typed_request(types.Submission, "get", url, kwargs, ["offset", "filter"])

    @validate_blogname
    def follow(self, blogname) -> Status:
        """
        Follow the url of the given blog

        :param blogname: a string, the blog url you want to follow

        :returns: True if the blog was followed and False otherwise
        """
        url = "/user/follow"
        return ok(self.send_api_request("post", url, {'url': blogname}, ['url']))

    @validate_blogname
    def unfollow(self, blogname) -> Status:
        """
        Unfollow the url of the given blog

        :param blogname: a string, the blog url you want to follow

        :returns: True if the blog was unfollowed and False otherwise
        """
        url = "/user/unfollow"
        return ok(self.send_api_request("post", url, {'url': blogname}, ['url']))

    def like(self, id, reblog_key) -> Status:
        """
        Like the post of the given blog

        :param id: an int, the id of the post you want to like
        :param reblog_key: a string, the reblog key of the post

        :returns: True if the post was liked and False otherwise
        """
        url = "/user/like"
        params = {'id': id, 'reblog_key': reblog_key}
        return ok(self.send_api_request("post", url, params, ['id', 'reblog_key']))

    def unlike(self, id, reblog_key) -> Status:
        """
        Unlike the post of the given blog

        :param id: an int, the id of the post you want to like
        :param reblog_key: a string, the reblog key of the post

        :returns: True if the post was unliked and False otherwise
        """
        url = "/user/unlike"
        params = {'id': id, 'reblog_key': reblog_key}
        return ok(self.send_api_request("post", url, params, ['id', 'reblog_key']))

    @validate_blogname
    def create_photo(self, blogname, **kwargs) -> Status:
        """
        Create a photo post or photoset on a blog

        :param blogname: a string, the url of the blog you want to post to.
        :param state: a string, The state of the post.
        :param tags: a list of tags that you want applied to the post
        :param tweet: a string, the customized tweet that you want
        :param date: a string, the GMT date and time of the post
        :param format: a string, sets the format type of the post. html or markdown
        :param slug: a string, a short text summary to the end of the post url
        :param caption: a string, the caption that you want applied to the photo
        :param link: a string, the 'click-through' url you want on the photo
        :param source: a string, the photo source url
        :param data: a string or a list of the path of photo(s)

        :returns: a dict created from the JSON response
        """
        kwargs.update({"type": "photo"})
        return self._send_post(blogname, kwargs)

    @validate_blogname
    def create_text(self, blogname, **kwargs) -> Status:
        """
        Create a text post on a blog

        :param blogname: a string, the url of the blog you want to post to.
        :param state: a string, The state of the post.
        :param tags: a list of tags that you want applied to the post
        :param tweet: a string, the customized tweet that you want
        :param date: a string, the GMT date and time of the post
        :param format: a string, sets the format type of the post. html or markdown
        :param slug: a string, a short text summary to the end of the post url
        :param title: a string, the optional title of a post
        :param body: a string, the body of the text post

        :returns: a dict created from the JSON response
        """
        kwargs.update({"type": "text"})
        return self._send_post(blogname, kwargs)

    @validate_blogname
    def create_quote(self, blogname, **kwargs) -> Status:
        """
        Create a quote post on a blog

        :param blogname: a string, the url of the blog you want to post to.
        :param state: a string, The state of the post.
        :param tags: a list of tags that you want applied to the post
        :param tweet: a string, the customized tweet that you want
        :param date: a string, the GMT date and time of the post
        :param format: a string, sets the format type of the post. html or markdown
        :param slug: a string, a short text summary to the end of the post url
        :param quote: a string, the full text of the quote
        :param source: a string, the cited source of the quote

        :returns: a dict created from the JSON response
        """
        kwargs.update({"type": "quote"})
        return self._send_post(blogname, kwargs)

    @validate_blogname
    def create_link(self, blogname, **kwargs) -> Status:
        """
        Create a link post on a blog

        :param blogname: a string, the url of the blog you want to post to.
        :param state: a string, The state of the post.
        :param tags: a list of tags that you want applied to the post
        :param tweet: a string, the customized tweet that you want
        :param date: a string, the GMT date and time of the post
        :param format: a string, sets the format type of the post. html or markdown
        :param slug: a string, a short text summary to the end of the post url
        :param title: a string, the title of the link
        :param url: a string, the url of the link you are posting
        :param description: a string, the description of the link you are posting

        :returns: a dict created from the JSON response
        """
        kwargs.update({"type": "link"})
        return self._send_post(blogname, kwargs)

    @validate_blogname
    def create_chat(self, blogname, **kwargs) -> Status:
        """
        Create a chat post on a blog

        :param blogname: a string, the url of the blog you want to post to.
        :param state: a string, The state of the post.
        :param tags: a list of tags that you want applied to the post
        :param tweet: a string, the customized tweet that you want
        :param date: a string, the GMT date and time of the post
        :param format: a string, sets the format type of the post. html or markdown
        :param slug: a string, a short text summary to the end of the post url
        :param title: a string, the title of the conversation
        :param conversation: a string, the conversation you are posting

        :returns: a dict created from the JSON response
        """
        kwargs.update({"type": "chat"})
        return self._send_post(blogname, kwargs)

    @validate_blogname
    def create_audio(self, blogname, **kwargs) -> Status:
        """
        Create a audio post on a blog

        :param blogname: a string, the url of the blog you want to post to.
        :param state: a string, The state of the post.
        :param tags: a list of tags that you want applied to the post
        :param tweet: a string, the customized tweet that you want
        :param date: a string, the GMT date and time of the post
        :param format: a string, sets the format type of the post. html or markdown
        :param slug: a string, a short text summary to the end of the post url
        :param caption: a string, the caption for the post
        :param external_url: a string, the url of the audio you are uploading
        :param data: a string, the local filename path of the audio you are uploading

        :returns: a dict created from the JSON response
        """
        kwargs.update({"type": "audio"})
        return self._send_post(blogname, kwargs)

    @validate_blogname
    def create_video(self, blogname, **kwargs) -> Status:
        """
        Create a audio post on a blog

        :param blogname: a string, the url of the blog you want to post to.
        :param state: a string, The state of the post.
        :param tags: a list of tags that you want applied to the post
        :param tweet: a string, the customized tweet that you want
        :param date: a string, the GMT date and time of the post
        :param format: a string, sets the format type of the post. html or markdown
        :param slug: a string, a short text summary to the end of the post url
        :param caption: a string, the caption for the post
        :param embed: a string, the emebed code that you'd like to upload
        :param data: a string, the local filename path of the video you are uploading

        :returns: a dict created from the JSON response
        """
        kwargs.update({"type": "video"})
        return self._send_post(blogname, kwargs)

    @validate_blogname
    def reblog(self, blogname, **kwargs):
        """
        Creates a reblog on the given blogname

        :param blogname: a string, the url of the blog you want to reblog to
        :param id: an int, the post id that you are reblogging
        :param reblog_key: a string, the reblog key of the post
        :param comment: a string, a comment added to the reblogged post

        :returns: a dict created from the JSON response
        """
        url = "/blog/{0}/post/reblog".format(blogname)

        valid_options = ['id', 'reblog_key', 'comment'] + self._post_valid_options(kwargs.get('type', None))
        if 'tags' in kwargs and kwargs['tags']:
            # Take a list of tags and make them acceptable for upload
            kwargs['tags'] = ",".join(kwargs['tags'])
        return created(self.send_api_request('post', url, kwargs, valid_options))

    @validate_blogname
    def delete_post(self, blogname, id) -> Status:
        """
        Deletes a post with the given id

        :param blogname: a string, the url of the blog you want to delete from
        :param id: an int, the post id that you want to delete

        :returns: a dict created from the JSON response
        """
        url = "/blog/{0}/post/delete".format(blogname)
        return ok(self.send_api_request('post', url, {'id': id}, ['id']))

    @validate_blogname
    def edit_post(self, blogname, **kwargs) -> Status:
        """
        Edits a post with a given id

        :param blogname: a string, the url of the blog you want to edit
        :param state: a string, the state of the post. published, draft, queue, or private.
        :param tags: a list of tags that you want applied to the post
        :param tweet: a string, the customized tweet that you want
        :param date: a string, the GMT date and time of the post
        :param format: a string, sets the format type of the post. html or markdown
        :param slug: a string, a short text summary to the end of the post url
        :param id: an int, the post id that you want to edit

        :returns: True if the post was created successfully and False otherwise
        """
        url = "/blog/{0}/post/edit".format(blogname)

        if 'tags' in kwargs and kwargs['tags']:
            # Take a list of tags and make them acceptable for upload
            kwargs['tags'] = ",".join(kwargs['tags'])

        valid_options = ['id'] + self._post_valid_options(kwargs.get('type', None))
        return ok(self.send_api_request('post', url, kwargs, valid_options))

    # Parameters valid for /post, /post/edit, and /post/reblog.
    def _post_valid_options(self, post_type=None) -> List[str]:
        # These options are always valid
        valid = ['type', 'state', 'tags', 'tweet', 'date', 'format', 'slug']

        # Other options are valid on a per-post-type basis
        if post_type == 'text':
            valid += ['title', 'body']
        elif post_type == 'photo':
            valid += ['caption', 'link', 'source', 'data', 'photoset_layout']
        elif post_type == 'quote':
            valid += ['quote', 'source']
        elif post_type == 'link':
            valid += ['title', 'url', 'description', 'thumbnail']
        elif post_type == 'chat':
            valid += ['title', 'conversation']
        elif post_type == 'audio':
            valid += ['caption', 'external_url', 'data']
        elif post_type == 'video':
            valid += ['caption', 'embed', 'data']

        return valid

    def _send_post(self, blogname, params) -> Tuple[bool, TumblrError]:
        """
        Formats parameters and sends the API request off. Validates
        common and per-post-type parameters and formats your tags for you.

        :param blogname: a string, the blogname of the blog you are posting to
        :param params: a dict, the key-value of the parameters for the api request
        :param valid_options: a list of valid options that the request allows

        :returns: if the post succeeded and any additional information given in the response
        """
        url = "/blog/{0}/post".format(blogname)
        valid_options = self._post_valid_options(params.get('type', None))

        if len(params.get("tags", [])) > 0:
            # Take a list of tags and make them acceptable for upload
            params['tags'] = ",".join(params['tags'])

        return created(self.send_api_request("post", url, params, valid_options))

    def send_typed_request(self, return_type: Type[T], method: str, url,
                           params=None, valid_parameters=None, needs_api_key=False) -> Result[T]:
        return _wrap(return_type, self.send_api_request(url, params, valid_parameters, needs_api_key))

    def send_api_request(self, method: str, url,
                         params=None, valid_parameters=None, needs_api_key=False) -> TumblrResponse:
        """
        Sends the url with parameters to the requested url, validating them
        to make sure that they are what we expect to have passed to us

        :param method: a string, the request method you want to make
        :param params: a dict, the parameters used for the API request
        :param valid_parameters: a list, the list of valid parameters
        :param needs_api_key: a boolean, whether or not your request needs an api key injected

        :returns: a dict parsed from the JSON response
        """
        if valid_parameters is None:
            valid_parameters = []
        if params is None:
            params = {}
        if needs_api_key:
            params.update({'api_key': self.request.consumer_key})
            valid_parameters.append('api_key')

        files = {}
        if 'data' in params:
            if isinstance(params['data'], list):
                for idx, data in enumerate(params['data']):
                    files['data[' + str(idx) + ']'] = open(params['data'][idx], 'rb')
            else:
                files = {'data': open(params['data'], 'rb')}
            del params['data']

        validate_params(valid_parameters, params)
        if method.lower() == "get":
            return self.request.get(url, params)
        elif method.lower() == "post":
            return self.request.post(url, params, files)
        else:
            raise ValueError('`method` must be either "GET" or "POST"')
