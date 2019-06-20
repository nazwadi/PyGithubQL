#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
Issues.py - a Github APIv4 object

"""

import json
import os

import requests

from .GithubObject import GithubObject

GRAPHQL_DIR = ''.join([os.path.dirname(os.path.realpath(__file__)), '/graphql/'])


class Issues(GithubObject):
    """An iterable object that represents all issues associated with a user. Upstream
    reference is at https://developer.github.com/v4/object/issues/"""

    def __init__(self, login, limit=100):
        """Queries the remote endpoint using the update function by passing
        the provided GitHub login name. This will populate the object with
        data for that persona."""
        super(Issues, self).__init__()
        self.response = ''
        self.limit = int(limit)
        self.update(login)
        self.initialPage = True

    def __repr__(self):
        return 'Issues(totalCount={!r}, startCursor={!r}, endCursor={!r})'.format(self.totalCount, self.startCursor, self.endCursor)

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (self.startCursor, self.endCursor) == (other.startCursor, other.endCursor)

    def __ne__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (self.startCursor, self.endCursor) != (other.startCursor, other.endCursor)

    def __iter__(self):
        return self

    def __next__(self):
        if self.initialPage:
            self.initialPage = False
            return self
        elif not self.hasNextPage:
            self.reset()
            raise StopIteration
        query = {"query" : open(GRAPHQL_DIR+'gh_issues_by_user_next.graphql', 'r').read() \
                 % (self._login, self.endCursor)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        self.response = json.loads(resp.text)
        if self._errors_exist(self.response):
            query = {"query" : open(GRAPHQL_DIR+'gh_issues_by_organization_next.graphql', 'r').read() \
                    % (self._login, self.endCursor)}
            resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
            self.response = json.loads(resp.text)
            if self._errors_exist(self.response):
                return False

        return self

    def __len__(self):
        """Returns the total count of issues returned by query"""
        return self.response['data']['user']['issues']['totalCount']

    def reset(self):
        """Reset the object's pager to the first page"""
        self.update(self._login)
        self.initialPage = True

    def update(self, login):
        """Updates the Repositories object with new data by querying the
        Github endpoint.
        """
        self._login = login
        query = {"query" : open(GRAPHQL_DIR+'gh_issues_by_user.graphql', 'r').read() % (login)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        self.response = json.loads(resp.text)
        if self._errors_exist(self.response):
            query = {"query" : open(GRAPHQL_DIR+'gh_issues_by_organization.graphql', 'r').read() % (login)}
            r = requests.post(url=self.endpoint, json=query, headers=self.headers)
            self.response = json.loads(r.text)
            if self._errors_exist(self.response):
                return False

        return True

    @property
    def startCursor(self):
        """
        :type: string
        """
        try:
            return self.response['data']['user']['issues']['pageInfo']['startCursor']
        except KeyError:
            return self.response['data']['organization']['issues']['pageInfo']['startCursor']

    @property
    def endCursor(self):
        """
        :type: string
        """
        try:
            return self.response['data']['user']['issues']['pageInfo']['endCursor']
        except AttributeError:
            return ''
        except KeyError:
            return self.response['data']['organization']['issues']['pageInfo']['endCursor']


    @property
    def hasNextPage(self):
        """
        :type: Boolean
        """
        try:
            return self.response['data']['user']['issues']['pageInfo']['hasNextPage']
        except KeyError:
            return self.response['data']['organization']['issues']['pageInfo']['hasNextPage']

    @property
    def hasPreviousPage(self):
        """
        :type: Boolean
        """
        try:
            return self.response['data']['user']['issues']['pageInfo']['hasPreviousPage']
        except KeyError:
            return self.response['data']['organization']['issues']['pageInfo']['hasPreviousPage']

    @property
    def nodes(self):
        """
        :type: dict
        """
        try:
            return self.response['data']['user']['issues']['nodes']
        except KeyError:
            return self.response['data']['organization']['issues']['nodes']

    @property
    def edges(self):
        """
        :type: dict
        """
        try:
            return self.response['data']['user']['issues']['edges']
        except KeyError:
            return self.response['data']['organization']['issues']['edges']

    @property
    def totalCount(self):
        """
        :type: int
        """
        try:
            return self.response['data']['user']['issues']['totalCount']
        except KeyError:
            return self.response['data']['organization']['issues']['totalCount']
