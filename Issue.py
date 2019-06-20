#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
Issue.py - a Github APIv4 object

"""

import json
import os

import requests

from .GithubObject import GithubObject
from .decorators import connection

GRAPHQL_DIR = ''.join([os.path.dirname(os.path.realpath(__file__)), '/graphql/'])


class Issue(GithubObject):
    """This class represents an Issue.  Upstream reference is at
    https://developer.github.com/v4/object/issue/"""

    def __init__(self, login, repository_name, issue_number):
        """
         Arguments:
            login (str) - the Github username
            repository_name (str) - name of the repository the Issue belongs to
            issue_number (int) - the id number of the Issue
        """
        super(Issue, self).__init__()
        self.update(login, repository_name, issue_number)

    def __repr__(self):
        return 'Issue(number={!r}, title={!r}, author={!r})'.format(self.number, self.title, self.author)

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (self.title, self.author, self.number) == (other.title, other.author, other.number)

    def __ne__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (self.title, self.author, self.number) != (other.title, other.author, other.number)

    def update(self, login, repository_name, issue_number):
        """Updates the Issue object with new data by querying the Github endpoint.
        Arguments:
            login (str) - the Github username
            repository_name (str) - name of the repository the Issue belongs to
            issue_number (int) - the id number of the Issue
        """
        self._login = login
        query = {"query" : open(GRAPHQL_DIR+'gh_issue_by_user.graphql', 'r').read() % (login, repository_name, issue_number)}
        r = requests.post(url=self.endpoint, json=query, headers=self.headers)
        self.response = json.loads(r.text)
        if self._errors_exist(self.response):
            query = {"query" : open(GRAPHQL_DIR+'gh_issue_by_organization.graphql', 'r').read() % (login, repository_name, issue_number)}
            r = requests.post(url=self.endpoint, json=query, headers=self.headers)
            self.response = json.loads(r.text)
            if self._errors_exist(self.response):
                return False

        return True

    @connection
    def assignees(self, **kwargs):
        """A list of Users assigned to this object.  This is a connection (edge/relationship)."""
        pass

    @connection
    def comments(self, **kwargs):
        """A list of comments associated with the Issue.  This is a connection (edge/relationship)."""
        pass

    @connection
    def labels(self, **kwargs):
        """A list of labels associated with the object.  This is a connection (edge/relationship)."""
        pass

    @connection
    def participants(self, **kwargs):
        """A list of Users that are participating in the Issue conversation.  This is a connection
        (edge/relationship)."""
        pass

    @connection
    def projectCards(self, **kwargs):
        """List of project cards associated with this issue.  This is a connection
        (edge/relationship)."""
        pass

    @connection
    def reactions(self, **kwargs):
        """A list of Reactions left on the issue.  This is a connection (edge/relationship)."""
        pass

    @connection
    def timeline(self, **kwargs):
        """A list of events, comments, commits, etc. associated with the issue.  This is a
        connection (edge/relationship)."""
        pass

    @connection
    def timelineItems(self, **kwargs):
        """A list of events, comments, commits, etc. associated with the issue.  This is a
        connection (edge/relationship)."""
        pass

    @connection
    def userContentEdits(self, **kwargs):
        """A list of edits to this content.  This is a connection (edge/relationship)."""
        pass

    @property
    def activeLockReason(self):
        """
        :type: str
        """
        try:
            return self.response['data']['user']['repository']['issue']['activeLockReason']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['activeLockReason']

    @property
    def author(self):
        """
        :type dict
        """
        try:
            return self.response['data']['user']['repository']['issue']['author']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['author']

    @property
    def authorAssociation(self):
        """
        :type str
        """
        try:
            return self.response['data']['user']['repository']['issue']['author']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['author']

    @property
    def body(self):
        """
        :type str
        """
        try:
            return self.response['data']['user']['repository']['issue']['body']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['body']

    @property
    def bodyHTML(self):
        """
        :type str
        """
        try:
            return self.response['data']['user']['repository']['issue']['bodyHTML']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['bodyHTML']

    @property
    def bodyText(self):
        """
        :type str
        """
        try:
            return self.response['data']['user']['repository']['issue']['bodyText']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['bodyText']

    @property
    def closed(self):
        """
        :type Boolean
        """
        try:
            return self.response['data']['user']['repository']['issue']['closed']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['closed']

    @property
    def closedAt(self):
        """
        :type str
        """
        try:
            return self.response['data']['user']['repository']['issue']['closedAt']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['closedAt']

    @property
    def createdAt(self):
        """
        :type str
        """
        try:
            return self.response['data']['user']['repository']['issue']['createdAt']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['createdAt']

    @property
    def createdViaEmail(self):
        """
        :type Boolean
        """
        try:
            return self.response['data']['user']['repository']['issue']['createdViaEmail']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['createdViaEmail']

    @property
    def databaseId(self):
        """
        :type int
        """
        try:
            return self.response['data']['user']['repository']['issue']['databaseId']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['databaseId']

    @property
    def editor(self):
        """
        :type dict
        """
        try:
            return self.response['data']['user']['repository']['issue']['editor']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['editor']

    @property
    def id(self):
        """
        :type str
        """
        try:
            return self.response['data']['user']['repository']['issue']['id']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['id']

    @property
    def includesCreatedEdit(self):
        """
        :type Boolean
        """
        try:
            return self.response['data']['user']['repository']['issue']['includesCreatedEdit']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['includesCreatedEdit']

    @property
    def lastEditedAt(self):
        """
        :type str
        """
        try:
            return self.response['data']['user']['repository']['issue']['lastEditedAt']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['lastEditedAt']

    @property
    def locked(self):
        """
        :type Boolean
        """
        try:
            return self.response['data']['user']['repository']['issue']['locked']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['locked']

    @property
    def milestone(self):
        """
        :type dict
        """
        try:
            return self.response['data']['user']['repository']['issue']['milestone']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['milestone']

    @property
    def number(self):
        """
        :type int
        """
        try:
            return self.response['data']['user']['repository']['issue']['number']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['number']

    @property
    def publishedAt(self):
        """
        :type str
        """
        try:
            return self.response['data']['user']['repository']['issue']['publishedAt']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['publishedAt']

    @property
    def reactionGroups(self):
        """
        :type dict
        """
        try:
            return self.response['data']['user']['repository']['issue']['reactionGroups']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['reactionGroups']

    @property
    def repository(self):
        """
        :type dict
        """
        try:
            return self.response['data']['user']['repository']['issue']['repository']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['repository']

    @property
    def resourcePath(self):
        """
        :type str
        """
        try:
            return self.response['data']['user']['repository']['issue']['resourcePath']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['resourcePath']

    @property
    def state(self):
        """
        :type str
        """
        try:
            return self.response['data']['user']['repository']['issue']['state']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['state']

    @property
    def title(self):
        """
        :type str
        """
        try:
            return self.response['data']['user']['repository']['issue']['title']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['title']

    @property
    def updatedAt(self):
        """
        :type str
        """
        try:
            return self.response['data']['user']['repository']['issue']['updatedAt']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['updatedAt']

    @property
    def url(self):
        """
        :type str
        """
        try:
            return self.response['data']['user']['repository']['issue']['url']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['url']

    @property
    def viewerCanReact(self):
        """
        :type Boolean
        """
        try:
            return self.response['data']['user']['repository']['issue']['viewerCanReact']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['viewerCanReact']

    @property
    def viewerCanSubscribe(self):
        """
        :type Boolean
        """
        try:
            return self.response['data']['user']['repository']['issue']['viewerCanSubscribe']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['viewerCanSubscribe']

    @property
    def viewerCanUpdate(self):
        """
        :type Boolean
        """
        try:
            return self.response['data']['user']['repository']['issue']['viewerCanUpdate']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['viewerCanUpdate']

    @property
    def viewerCanUpdateReasons(self):
        """
        :type Boolean
        """
        try:
            return self.response['data']['user']['repository']['issue']['viewerCanUpdateReasons']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['viewerCanUpdateReasons']

    @property
    def viewerDidAuthor(self):
        """
        :type Boolean
        """
        try:
            return self.response['data']['user']['repository']['issue']['viewerDidAuthor']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['viewerDidAuthor']

    @property
    def viewerSubscription(self):
        """
        :type Boolean
        """
        try:
            return self.response['data']['user']['repository']['issue']['viewerSubscription']
        except KeyError:
            return self.response['data']['organization']['repository']['issue']['viewerSubscription']

