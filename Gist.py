#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
Gist.py - a Github APIv4 object

TODO: This class is still a Work in Progress

"""

import json
import os

import requests

from .GithubObject import GithubObject
from .decorators import connection

GRAPHQL_DIR = ''.join([os.path.dirname(os.path.realpath(__file__)), '/graphql/Gist/'])


class Gist(GithubObject):
    """This class represents a Gist.  Upstream reference is at
    https://developer.github.com/v4/object/gist/"""

    def __init__(self, name, owner):
        """
        Arguments:
            name (str) - the name of the gist
            owner (str) - the owner of the gist, i.e. their login name
        """
        super(Gist, self).__init__()
        self._name = None
        self._owner = None
        self.response = None
        self.update(name, owner)

    def __repr__(self):
        return 'Gist(name={!r}, owner={!r})'.format(self.name, self.owner)

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (self.name, self.owner) == (other.name, other.owner)

    def __ne__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (self.name, self.owner) != (other.name, other.owner)

    def update(self, name, owner):
        """Updates the Gist object with new data by querying the Github endpoint.
        Arguments:
            name (str) - the name of the gist
            owner (str) - the owner of the gist, i.e. their login name
        """
        self._name = name
        self._owner = owner
        query = {"query" : open(GRAPHQL_DIR+'gist.graphql', 'r').read() % (owner, name)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        self.response = json.loads(resp.text)
        if self._errors_exist(self.response):
            return False

        return True

    @connection
    def comments(self, **kwargs):
        """A list of comments associated with the gist.

        Keyword Arguments:
            after (str) - Returns the elements in the list that come after the specified cursor.
            before (str) - Returns the elements in the list that come before the specified cursor.
            first (int) - Returns the first n elements from the list.
            last (int) - Returns the last n elements from the list.

        Returns:
            a json string containing the comments made on this gist

        TODO: This function should return a GithubObject, GistComment instead of json eventually.
                see https://developer.github.com/v4/object/gistcomment/
        """
        filters = []
        for key, value in kwargs.items():
            filters.append("{}: {}, ".format(key, value))
        filters = ''.join(filters)
        filters = filters.rstrip(', ')
        query = {"query" : open(GRAPHQL_DIR+'gist_comments.graphql', 'r').read() % (self.owner, self.name, filters)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        comments = json.loads(resp.text)
        if self._errors_exist('GithubGistComments', self.owner, comments):
            return False

        return comments

    @connection
    def stargazers(self, **kwargs):
        """A list of users who have starred this starrable.

        Keyword Arguments:
            after (str) - Returns the elements in the list that come after the specified cursor.
            before (str) - Returns the elements in the list that come before the specified cursor.
            first (int) - Returns the first n elements from the list.
            last (int) - Returns the last n elements from the list.

        Returns:
            a json string containing the login names of users who starred this gist.

        TODO: Eventually this query should return a list of GithubUser objects.
        """
        filters = []
        for key, value in kwargs.items():
            filters.append("{}: {}, ".format(key, value))
        filters = ''.join(filters)
        filters = filters.rstrip(', ')
        query = {"query" : open(GRAPHQL_DIR+'gist_stargazers.graphql', 'r').read() % (self.owner, self.name, filters)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        stargazers = json.loads(resp.text)
        if self._errors_exist('GithubGistStargazers', self.owner, stargazers):
            return False

        return stargazers

    @property
    def createdAt(self):
        """Identifies the date and time when the object was created.
        :type: string  (An ISO-8601 encoded UTC date string)
        """
        return self.response['data']['user']['gist']['createdAt']

    @property
    def description(self):
        """The gist description
        :type str
        """
        return self.response['data']['user']['gist']['description']

    @property
    def id(self):
        """
        :type str
        """
        return self.response['data']['user']['gist']['id']

    @property
    def isPublic(self):
        """Whether the gist is public or not
        :type boolean
        """
        return self.response['data']['user']['gist']['isPublic']

    @property
    def name(self):
        """The gist name
        :type str
        """
        return self.response['data']['user']['gist']['name']

    @property
    def owner(self):
        """The gist owner
        :type str
        """
        return self.response['data']['user']['gist']['owner']['login']

    @property
    def pushedAt(self):
        """Identifies when the gist was last pushed to
        :type: str  (An ISO-8601 encoded UTC date string)
        """
        return self.response['data']['user']['gist']['pushedAt']

    @property
    def updatedAt(self):
        """Identifies the date and time when the object was last created
        :type: str  (An ISO-8601 encoded UTC date string)
        """
        return self.response['data']['user']['gist']['updatedAt']

    @property
    def viewerHasStarred(self):
        """Indicates whether the viewing user has starred this starrable
        :type: boolean
        """
        return self.response['data']['user']['gist']['viewerHasStarred']
