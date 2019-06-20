#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
PublicKey.py - a Github APIv4 object

TODO: This class is still a Work in Progress

"""
from .GithubObject import GithubObject


class PublicKey(GithubObject):
    """This class represents a user's public key.  Upstream reference is at
    https://developer.github.com/v4/object/publickey/"""

    def __init__(self, login, data):
        """
        Arguments:
            login (str) - the github login of the owner of this key
            data (str) - a json-formatted public key from github's api
        """
        super(PublicKey, self).__init__()
        self._owner = login
        self.data = data

    def __repr__(self):
        return 'PublicKey(id={!r}, owner={!r})'.format(self.id, self._owner)

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return self.id == other.id

    def __ne__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return self.id != other.id

    @property
    def id(self):
        """
        :type str
        """
        return self.data['node']['id']

    @property
    def key(self):
        """The public key string
        :type str
        """
        return self.data['node']['key']
