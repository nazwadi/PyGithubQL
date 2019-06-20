#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
GistComment.py - a Github APIv4 object

TODO: This class is still a Work in Progress

"""

import json
import os

import requests

from .GithubObject import GithubObject
from .decorators import connection

GRAPHQL_DIR = ''.join([os.path.dirname(os.path.realpath(__file__)), '/graphql/'])


class GistComment(GithubObject):
    """This class represents a comment on a Gist.  Upstream reference is at
    https://developer.github.com/v4/object/gistcomment/"""

    def __init__(self, data):
        """
        Arguments:
            data (str) - a json-formatted gist comment node from a user.gistComments query
        """
        super(Gist, self).__init__()
        self.data = data

    def __repr__(self):
        return 'GistComment(id={!r}, createdAt={!r})'.format(self.id, self.createdAt)

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return self.id == other.id

    def __ne__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return self.id != other.id

    @connection
    def userContentEdits(self, **kwargs):
        """A list of edits to this content

        Keyword Arguments:
            after (str) - Returns the elements in the list that come after the specified cursor.
            before (str) - Returns the elements in the list that come before the specified cursor.
            first (int) - Returns the first n elements from the list.
            last (int) - Returns the last n elements from the list.

        WIP: This function is a work in progress.
        TODO: This function should return a GithubObject, GistComment instead of json eventually.
                see https://developer.github.com/v4/object/gistcomment/
        """
        filters = []
        for key, value in kwargs.items():
            filters.append("{}: {}, ".format(key, value))
        filters = ''.join(filters)
        filters = filters.rstrip(', ')
        try:
            gist_owner = self.gist['owner']['login']
            gist_name = self.gist['name']
        except KeyError:
            return False # the gist property of the query MUST return an owner and a gist name
        query = {"query" : '{ user(login: "%s") { gist(name: "%s") { comments(%s) { totalCount,
                 edges { cursor, node { userContentEdits(%s){}}}, pageInfo { startCursor, endCursor, hasNextPage,
                 hasPreviousPage } } } } }' }
        query = {"query" : open(GRAPHQL_DIR+'gh_gist_comment_user_content_edits.graphql', 'r').read() % (gist_owner, gist_name, filters)}
        user_content_edits = requests.post(url=self.endpoint, json=query, headers=self.headers)
        if self._errors_exist(user_content_edits):
            return False
        return user_content_edits

    @property
    def author(self):
        """The actor who authored the comment.
        :type dict
        """
        return self.data['node']['author']

    @property
    def authorAssociation(self):
        """Author's association with the gist.
        :type str
        """
        return self.data['node']['authorAssocation']

    @property
    def body(self):
        """Identifies the comment body.
        :type str
        """
        return self.data['node']['body']

    @property
    def bodyHTML(self):
        """The comment body rendered to HTML.
        :type str
        """
        return self.data['node']['bodyHTML']

    @property
    def bodyText(self):
        """The body rendered to text.
        :type str
        """
        return self.data['node']['bodyText']

    @property
    def createdAt(self):
        """Identifies the date and time when the object was created.
        :type: string  (An ISO-8601 encoded UTC date string)
        """
        return self.data['node']['createdAt']

    @property
    def createdViaEmail(self):
        """Check if this comment was created via an email reply.
        :type: Boolean
        """
        return self.data['node']['createdViaEmail']

    @property
    def databaseId(self):
        """Identifies the primary key from the database.
        :type str
        """
        return self.data['node']['databaseId']

    @property
    def editor(self):
        """The actor who edited the comment.
        :type dict
        """
        return self.data['node']['editor']

    @property
    def gist(self):
        """The associated gist
        :type dict
        """
        return self.data['node']['gist']

    @property
    def id(self):
        """
        :type str
        """
        return self.data['node']['id']

    @property
    def includesCreatedEdit(self):
        """
        Check if this comment was edited and includes an edit with the creation data
        :type: Boolean
        """
        return self.data['node']['includesCreatedEdit']

    @property
    def isMinimized(self):
        """Returns whether or not a comment has been minimized.
        :type: Boolean
        """
        return self.data['node']['isMinimized']

    @property
    def lastEditedAt(self):
        """The moment the editor made the last edit
        :type: string  (An ISO-8601 encoded UTC date string)
        """
        return self.data['node']['lastEditedAt']

    @property
    def minimizedReason(self):
        """Returns why the comment was minimized.
        :type: str
        """
        return self.data['node']['minimizedReason']

    @property
    def publishedAt(self):
        """Identifies when the comment was published at.
        :type: str  (An ISO-8601 encoded UTC date string)
        """
        return self.data['node']['publishedAt']

    @property
    def updatedAt(self):
        """Identifies the date and time when the object was last updated
        :type: str  (An ISO-8601 encoded UTC date string)
        """
        return self.data['node']['updatedAt']

    @property
    def viewerCanDelete(self):
        """Check if the current viewer can delete this object.
        :type: boolean
        """
        return self.data['node']['viewerCanDelete']

    @property
    def viewerCanMinimize(self):
        """Check if the current viewer can minimize this object.
        :type: boolean
        """
        return self.data['node']['viewerCanDelete']

    @property
    def viewerCanUpdate(self):
        """Check if the current viewer can update this object.
        :type: boolean
        """
        return self.data['node']['viewerCanUpdate']

    @property
    def viewerCannotUpdateReasons(self):
        """Reasons why the current viewer can not update this comment.
        :type: str
        """
        return self.data['node']['viewerCannotUpdateReasons']

    @property
    def viewerDidAuthor(self):
        """Did the viewer author this comment.
        :type: Boolean
        """
        return self.data['node']['viewerDidAuthor']
