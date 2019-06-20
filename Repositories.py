#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
Repositories.py - a Github APIv4 object

"""

import json
import os

import requests

from GithubObject import GithubObject

GRAPHQL_DIR = ''.join([os.path.dirname(os.path.realpath(__file__)), '/graphql/'])


class Repositories(GithubObject):
    """An iterable dataset of repositories
    Upstream reference is at https://developer.github.com/v4/object/repository/"""

    def __init__(self, login, **kwargs):
        """
        Arguments:
            login (str) - the owner of the repositories

        Keyword Arguments:
            affiliations ([RepositoryAffiliation]) - List of viewer's affiliation options for
                    repositories returned from the connection.  For example, OWNER will include only
                    repositories that the current viewer owns.

                    The default value is
                    ["OWNER", "COLLABORATOR"].
            after (str) - Returns the elements in the list that come after the specified cursor.
            before (str) - Returns the elements in the list that come before the specified cursor.
            first (int) - Returns the first n elements from the list.
            isFork (Boolean) - If non-null, filters repositories according to whether they are forks
                    of another repository
            isLocked (Boolean) - If non-null, filters repositories according to whether they have
                    been locked
            last (int) - Returns the last n elements from the list.
            orderBy (RepositoryOrder) - Ordering options for repositories returned from the connection.
            ownerAffiliations ([RepositoryAffiliation]) - List of owner's affiliation options for
                    repositories returned from the connection.  For example, OWNER will include only
                    repositories that the organization or user being viewed owns.

                    The default value is
                    ["OWNER", "COLLABORATOR"].
            privacy (RepositoryPrivacy) - If non-null, filters repositories according to privacy.
        """
        super(Repositories, self).__init__()
        self.response = None
        self.update(login)
        filters = []
        for key, value in kwargs.items():
            filters.append("{}: {},".format(key, value))
        self.filters = ''.join(filters)
        self.initialPage = True

    def __repr__(self):
        return 'Repositories(login={!r}, startCursor={!r}, endCursor={!r})'.format(self._login, self.startCursor, self.endCursor)

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
        query = {"query" : open(GRAPHQL_DIR+'gh_repositories_by_user_next.graphql', 'r').read() \
                 % (self._login, self.endCursor)}
        r = requests.post(url=self.endpoint, json=query, headers=self.headers)
        self.response = json.loads(r.text)
        if self._errors_exist(self.response):
            query = {"query" : open(GRAPHQL_DIR+'gh_repositories_by_organization_next.graphql', 'r').read() \
                    % (self._login, self.endCursor)}
            r = requests.post(url=self.endpoint, json=query, headers=self.headers)
            self.response = json.loads(r.text)
            return False

        return self

    def __len__(self):
        """Returns the total count of repositories belonging to User
        with given login"""
        return self.response['data']['user']['repositories']['totalCount']

    def reset(self):
        """Reset the object's pager to the first page"""
        self.update(self._login)
        self.initialPage = True

    def update(self, login):
        """Updates the Repositories object with new data by querying the
        Github endpoint.
        Arguments:
            login (str)
        """
        self._login = login
        query = { "query" : open(GRAPHQL_DIR+'gh_repositories_by_user.graphql','r').read() \
                 % (login, self.filters)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        self.response = json.loads(resp.text)
        if self._errors_exist(self.response):
            query = { "query" : open(GRAPHQL_DIR+'gh_repositories_by_organization.graphql','r').read() \
                    % (login, self.filters)}
            resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
            self.response = json.loads(resp.text)
            if self._errors_exist(self.response):
                return False

        return True

    @property
    def startCursor(self):
        """
        :type: string
        """
        try:
            return self.response['data']['user']['repositories']['pageInfo']['startCursor']
        except KeyError:
            return self.response['data']['organization']['repositories']['pageInfo']['startCursor']

    @property
    def endCursor(self):
        """
        :type: string
        """
        try:
            return self.response['data']['user']['repositories']['pageInfo']['endCursor']
        except KeyError:
            return self.response['data']['organization']['repositories']['pageInfo']['endCursor']

    @property
    def hasNextPage(self):
        """
        :type: Boolean
        """
        try:
            return self.response['data']['user']['repositories']['pageInfo']['hasNextPage']
        except KeyError:
            return self.response['data']['organization']['repositories']['pageInfo']['hasNextPage']

    @property
    def hasPreviousPage(self):
        """
        :type: Boolean
        """
        try:
            return self.response['data']['user']['repositories']['pageInfo']['hasPreviousPage']
        except KeyError:
            return self.response['data']['organization']['repositories']['pageInfo']['hasPreviousPage']

    @property
    def nodes(self):
        """
        :type: dict
        """
        try:
            return self.response['data']['user']['repositories']['nodes']
        except KeyError:
            return self.response['data']['organization']['repositories']['nodes']

    @property
    def edges(self):
        """
        :type: dict
        """
        try:
            return self.response['data']['user']['repositories']['edges']
        except KeyError:
            return self.response['data']['organization']['repositories']['edges']

    @property
    def totalCount(self):
        """
        :type: int
        """
        try:
            return self.response['data']['user']['repositories']['totalCount']
        except KeyError:
            return self.response['data']['organization']['repositories']['totalCount']

    @property
    def totalDiskUsage(self):
        """Total Disk Usage of all repositories in kilobytes
        :type: int
        """
        try:
            return self.response['data']['user']['repositories']['totalDiskUsage']
        except KeyError:
            return self.response['data']['organization']['repositories']['totalDiskUsage']
