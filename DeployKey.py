#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
DeployKey.py - a Github APIv4 object

TODO: This class has not been tested for lack of real-world DeployKey data

"""
from .GithubObject import GithubObject

class DeployKey(GithubObject):
    """This class represents a repository deploy key.  Upstream reference is at
    https://developer.github.com/v4/object/deploykey/"""

    def __init__(self, login, data):
        """
        Arguments:
            login (str) - the github login of the owner of this key
            data (str) - a json-formatted public key from github's api
        """
        super(DeployKey, self).__init__()
        self._owner = login
        self.data = data

    def __repr__(self):
        return 'DeployKey(id={!r}, owner={!r})'.format(self.id, self._owner)

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return self.id == other.id

    def __ne__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return self.id != other.id

    @property
    def createdAt(self):
        """Identifies the date and time when the object was created.
        :type str
        """
        return self.data['node']['createdAt']

    @property
    def id(self):
        """
        :type str
        """
        return self.data['node']['id']

    @property
    def key(self):
        """The deploy key
        :type str
        """
        return self.data['node']['key']

    @property
    def readOnly(self):
        """Whether or not the deploy key is read only
        :type Boolean
        """
        return self.data['node']['readOnly']

    @property
    def title(self):
        """The deploy key title
        :type str
        """
        return self.data['node']['title']

    @property
    def verified(self):
        """Whether or not the deploy key has been verified
        :type Boolean
        """
        return self.data['node']['verified']
