#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
Repository.py - a Github APIv4 object

"""

import json
import os

import requests

from .GithubObject import GithubObject

GRAPHQL_DIR = ''.join([os.path.dirname(os.path.realpath(__file__)), '/graphql/Repository/'])


class Repository(GithubObject):
    """This class represents a Repository.  Upstream reference is at
    https://developer.github.com/v4/object/repository/"""

    def __init__(self, name, owner):
        """
        Arguments:
            name (str) - the name of the repository
            owner (str) - the owner of the repository, i.e. their login name
        """
        super(Repository, self).__init__()
        self._name = None
        self._owner = None
        self.response = None
        self.update(name, owner)

    def __len__(self):
        """Returns the size of the repository in kilobytes

        Uses the 'diskUsage' attribute from the query response.
        """
        return self.response['data']['repository']['diskUsage']

    def __repr__(self):
        return 'Repository(name={!r}, owner={!r})'.format(self.name, self.owner)

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (self.name, self.owner) == (other.name, other.owner)

    def __ne__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (self.name, self.owner) != (other.name, other.owner)

    def as_cypher_create_query(self):
        """Returns Repository object in a Cypher CREATE Query format"""
        query = "CREATE (n:GithubRepository { codeOfConduct: '%s', \
                                              createdAt: '%s', \
                                              databaseId: '%s', \
                                              defaultBranchRef: '%s', \
                                              description: '%s', \
                                              descriptionHTML: '%s', \
                                              diskUsage: '%s', \
                                              forkCount: '%s', \
                                              hasIssuesEnabled: %s, \
                                              hasWikiEnabled: %s, \
                                              homepageUrl: '%s', \
                                              id: '%s', \
                                              isArchived: %s, \
                                              isFork: %s, \
                                              isLocked: %s, \
                                              isMirror: %s, \
                                              isPrivate: %s, \
                                              licenseInfo: %s, \
                                              lockReason: '%s', \
                                              mergeCommitAllowed: %s, \
                                              mirrorUrl: %s, \
                                              name: '%s', \
                                              nameWithOwner: '%s', \
                                              owner: '%s', \
                                              parent: '%s', \
                                              primaryLanguage: '%s', \
                                              projectsResourcePath: '%s', \
                                              projectsUrl: '%s', \
                                              pushedAt: '%s', \
                                              rebaseMergeAllowed: '%s', \
                                              resourcePath: '%s', \
                                              shortDescriptionHTML: '%s', \
                                              squashMergeAllowed: '%s', \
                                              sshUrl: '%s', \
                                              updatedAt: '%s', \
                                              url: '%s', \
                                              viewerCanAdminister: '%s', \
                                              viewerCanCreateProjects: '%s', \
                                              viewerCanSubscribe: '%s', \
                                              viewerCanUpdateTopics: '%s', \
                                              viewerHasStarred: '%s', \
                                              viewerPermission: '%s', \
                                              viewerSubscription: '%s' })" \
                % (self.codeOfConduct, self.createdAt, self.databaseId,
                   self.defaultBranchRef, self.description,
                   self.descriptionHTML, self.diskUsage, self.forkCount,
                   self.hasIssuesEnabled, self.hasWikiEnabled,
                   self.homepageUrl, self.id, self.isArchived, self.isFork,
                   self.isLocked, self.isMirror, self.isPrivate,
                   self.licenseInfo, self.lockReason, self.mergeCommitAllowed,
                   self.mirrorUrl, self.name, self.nameWithOwner, self.owner,
                   self.parent, self.primaryLanguage,
                   self.projectsResourcePath, self.projectsUrl, self.pushedAt,
                   self.rebaseMergeAllowed, self.resourcePath,
                   self.shortDescriptionHTML, self.squashMergeAllowed,
                   self.sshUrl, self.updatedAt, self.url,
                   self.viewerCanAdminister, self.viewerCanCreateProjects,
                   self.viewerCanSubscribe, self.viewerCanUpdateTopics,
                   self.viewerHasStarred, self.viewerPermission,
                   self.viewerSubscription)

        return ' '.join(query.split())

    def update(self, name, owner):
        """Updates the Repository object with new data by querying the Github endpoint.
        Arguments:
            name (str) - the name of the repository
            owner (str) - the owner of the repository, i.e. their login name
        """
        self._name = name
        self._owner = owner
        query = {"query" : open(GRAPHQL_DIR+'repository.graphql', 'r').read() % (owner, name)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        self.response = json.loads(resp.text)
        if self._errors_exist(self.response):
            return False

        return True

    @property
    def codeOfConduct(self):
        """
        :type: dict
        """
        return self.response['data']['repository']['codeOfConduct']

    @property
    def createdAt(self):
        """Identifies the date and time when the object was created.
        :type: string  (An ISO-8601 encoded UTC date string)
        """
        return self.response['data']['repository']['createdAt']

    @property
    def databaseId(self):
        """Identifies the primary key from the database.
        :type: int
        """
        return self.response['data']['repository']['databaseId']

    @property
    def defaultBranchRef(self):
        """
        :type: dict
        """
        return self.response['data']['repository']['defaultBranchRef']

    @property
    def description(self):
        """
        :type: string
        """
        return self.response['data']['repository']['description']

    @property
    def descriptionHTML(self):
        """
        :type: string
        """
        return self.response['data']['repository']['descriptionHTML']

    @property
    def diskUsage(self):
        """
        :type: int
        """
        return self.response['data']['repository']['diskUsage']

    @property
    def forkCount(self):
        """
        :type: int
        """
        return self.response['data']['repository']['forkCount']

    @property
    def hasIssuesEnabled(self):
        """
        :type: Boolean
        """
        return self.response['data']['repository']['hasIssuesEnabled']

    @property
    def hasWikiEnabled(self):
        """
        :type: Boolean
        """
        return self.response['data']['repository']['hasWikiEnabled']

    @property
    def homepageUrl(self):
        """
        :type: string
        """
        return self.response['data']['repository']['homepageUrl']

    @property
    def id(self):
        """
        :type: string
        """
        return self.response['data']['repository']['id']

    @property
    def isArchived(self):
        """
        :type: Boolean
        """
        return self.response['data']['repository']['isArchived']

    @property
    def isFork(self):
        """
        :type: Boolean
        """
        return self.response['data']['repository']['isFork']

    @property
    def isLocked(self):
        """
        :type: Boolean
        """
        return self.response['data']['repository']['isLocked']

    @property
    def isMirror(self):
        """
        :type: Boolean
        """
        return self.response['data']['repository']['isMirror']

    @property
    def isPrivate(self):
        """
        :type: Boolean
        """
        return self.response['data']['repository']['isPrivate']

    @property
    def licenseInfo(self):
        """
        :type: dict
        """
        return self.response['data']['repository']['licenseInfo']

    @property
    def lockReason(self):
        """
        :type: string
        """
        return self.response['data']['repository']['lockReason']

    @property
    def mergeCommitAllowed(self):
        """
        :type: Boolean
        """
        return self.response['data']['repository']['mergeCommitAllowed']

    @property
    def mirrorUrl(self):
        """
        :type: string
        """
        return self.response['data']['repository']['mirrorUrl']

    @property
    def name(self):
        """
        :type: string
        """
        return self.response['data']['repository']['name']

    @property
    def nameWithOwner(self):
        """
        :type: string
        """
        return self.response['data']['repository']['nameWithOwner']

    @property
    def owner(self):
        """
        :type: dict
        """
        return self.response['data']['repository']['owner']

    @property
    def parent(self):
        """
        :type: dict
        """
        return self.response['data']['repository']['parent']

    @property
    def primaryLanguage(self):
        """
        :type: dict
        """
        return self.response['data']['repository']['primaryLanguage']

    @property
    def projectsResourcePath(self):
        """
        :type: string
        """
        return self.response['data']['repository']['projectsResourcePath']

    @property
    def projectsUrl(self):
        """
        :type: string
        """
        return self.response['data']['repository']['projectsUrl']

    @property
    def pushedAt(self):
        """
        :type: string  (An ISO-8601 encoded UTC date string)
        """
        return self.response['data']['repository']['pushedAt']

    @property
    def rebaseMergeAllowed(self):
        """
        :type: Boolean
        """
        return self.response['data']['repository']['rebaseMergeAllowed']

    @property
    def resourcePath(self):
        """
        :type: string
        """
        return self.response['data']['repository']['resourcePath']

    @property
    def shortDescriptionHTML(self):
        """
        :type string
        """
        return self.response['data']['repository']['shortDescriptionHTML']

    @property
    def squashMergeAllowed(self):
        """
        :type: Boolean
        """
        return self.response['data']['repository']['squashMergeAllowed']

    @property
    def sshUrl(self):
        """
        :type: string
        """
        return self.response['data']['repository']['sshUrl']

    @property
    def updatedAt(self):
        """
        :type: string  (An ISO-8601 encoded UTC date string)
        """
        return self.response['data']['repository']['updatedAt']

    @property
    def url(self):
        """
        :type: string
        """
        return self.response['data']['repository']['url']

    @property
    def viewerCanAdminister(self):
        """
        :type: Boolean
        """
        return self.response['data']['repository']['viewerCanAdminister']

    @property
    def viewerCanCreateProjects(self):
        """
        :type: Boolean
        """
        return self.response['data']['repository']['viewerCanCreateProjects']

    @property
    def viewerCanSubscribe(self):
        """
        :type: Boolean
        """
        return self.response['data']['repository']['viewerCanSubscribe']

    @property
    def viewerCanUpdateTopics(self):
        """
        :type: Boolean
        """
        return self.response['data']['repository']['viewerCanUpdateTopics']

    @property
    def viewerHasStarred(self):
        """
        :type: Boolean
        """
        return self.response['data']['repository']['viewerHasStarred']

    @property
    def viewerPermission(self):
        """
        :type: string
        """
        return self.response['data']['repository']['viewerPermission']

    @property
    def viewerSubscription(self):
        """
        :type: string
        """
        return self.response['data']['repository']['viewerSubscription']
