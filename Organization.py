#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
Organization.py - a Github APIv4 object

Organization:  "An account on GitHub, with one or more owners, that has repositories,
members and teams."

TODO: This class is still a Work in Progress

"""

import json
import os

import requests

from GithubObject import GithubObject
from Repositories import Repositories
from decorators import connection

GRAPHQL_DIR = ''.join([os.path.dirname(os.path.realpath(__file__)), '/graphql/Organization/'])


class Organization(GithubObject):
    """This class represents Organizations.  Upstream reference is at
    https://developer.github.com/v4/object/organization/"""

    def __init__(self, login):
        """Initialize an instance or the Organization object. This will
        query the remote endpoint using the provided login name and populate
        the object with data.

        Arguments:
            login (str) - the organization's login name
        """
        super(Organization, self).__init__()
        self._login = None
        self.update(login)

    def __repr__(self):
        return 'Organization(name={!r}, url={!r})'.format(self.login, self.url)

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (self.login, self.url) == (other.login, other.url)

    def __ne__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (self.login, self.url) != (other.login, other.url)

    def update(self, login):
        """Updates the Organization object with new data by querying the
        Github endpoint.

        Arguments:
            login (str) - the organization's login name

        Returns:
            boolean - False if errors exist, True otherwise
        """
        self._login = login
        query = {"query" : open(GRAPHQL_DIR+'organization.graphql', 'r').read() % (login)}
        r = requests.post(url=self.endpoint, json=query, headers=self.headers)
        self.response = json.loads(r.text)
        if self._errors_exist(self.response):
            return False

        return True

    @connection
    def membersWithRole(self, **kwargs):
        """A list of users who are members of this organization.

        Keyword Arguments:
            after (str) - Returns the elements in the list that come after the specified cursor.
            before (str) - Returns the elements in the list that come before the specified cursor.
            first (int) - Returns the first n elements from the list.
            last (int) - Returns the last n elements from the list.

        Returns:
            json object where each node contains a login of a member
        """
        filters = []
        for key, value in kwargs.items():
            filters.append("{}: {}, ".format(key, value))
        filters = ''.join(filters)
        filters = filters.rstrip(', ')
        query = {"query" : open(GRAPHQL_DIR+'organization_membersWithRole.graphql', 'r').read() % (self.login, filters)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        members_with_role = json.loads(resp.text)
        if self._errors_exist('GithubOrgMembersWithRole', self.login, members_with_role):
            return False

        return members_with_role

    @connection
    def pendingMembers(self, **kwargs):
        """A list of users who have been invited to join this organization.

        Keyword Arguments:
            after (str) - Returns the elements in the list that come after the specified cursor.
            before (str) - Returns the elements in the list that come before the specified cursor.
            first (int) - Returns the first n elements from the list.
            last (int) - Returns the last n elements from the list.

        Returns:
            json object where each node contains a login of a pending member
        """
        filters = []
        for key, value in kwargs.items():
            filters.append("{}: {}, ".format(key, value))
        filters = ''.join(filters)
        filters = filters.rstrip(', ')
        query = {"query" : open(GRAPHQL_DIR+'organization_pendingMembers.graphql', 'r').read() % (self.login, filters)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        pending_members = json.loads(resp.text)
        if self._errors_exist('GithubOrgPendingMembers', self.login, pending_members):
            return False

        return pending_members

    @connection
    def pinnedRepositories(self, **kwargs):
        """A list of repositories this user has pinned to their profile.

        Keyword Arguments:
            affiliations ([RepositoryAffiliation]) - List of viewer's affiliation options for
                    repositories returned from the connection.  For example, OWNER will include only
                    repositories that the current viewer owns.

                    The default value is
                    ["OWNER", "COLLABORATOR"].
            after (str) - Returns the elements in the list that come after the specified cursor.
            before (str) - Returns the elements in the list that come before the specified cursor.
            first (int) - Returns the first n elements from the list.
            isLocked (Boolean) - If non-null, filters repositories according to whether they have
                    been locked.
            last (int) - Returns the last n elements from the list.
            orderBy (RepositoryOrder) - Ordering options for repositories returned from the
                    connection.
            ownerAffiliations ([RepositoryAffiliation]) - List of owner's affiliation options for
                    repositories returned from the connection.  For example, OWNER will include only
                    repositories that the organization or user being viewed owns.

                    The default value is
                    ["OWNER", "COLLABORATOR"].
            privacy (RepositoryPrivacy) - If non-null, filters repositories according to privacy.

        Returns:
            json object where each node contains a nameWithOwner of a pinned respository
        """
        filters = []
        for key, value in kwargs.items():
            filters.append("{}: {}, ".format(key, value))
        filters = ''.join(filters)
        filters = filters.rstrip(', ')
        query = {"query" : open(GRAPHQL_DIR+'organization_pinnedRepositories.graphql', 'r').read() % (self.login, filters)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        pinned_repositories = json.loads(resp.text)
        if self._errors_exist('GithubOrgPinnedRepositories', self.login, pinned_repositories):
            return False

        return pinned_repositories

    @connection
    def projects(self, **kwargs):
        """A list of projects under the owner.

        Keyword Arguments:
            after (str) - Returns the elements in the list that come after the specified cursor.
            before (str) - Returns the elements in the list that come before the specified cursor.
            first (int) - Returns the first n elements from the list.
            last (int) - Returns the last n elements from the list.
            orderBy (ProjectOrder) - Ordering options for projects returned from the connection
            search (str) - Query to search projects by, currently only searching by name.
            states ([ProjectState]) - A list of states to filter the projects by.

        Returns:
            json object where each node contains a project under this organization
        """
        filters = []
        for key, value in kwargs.items():
            filters.append("{}: {}, ".format(key, value))
        filters = ''.join(filters)
        filters = filters.rstrip(', ')
        query = {"query" : open(GRAPHQL_DIR+'organization_projects.graphql', 'r').read() % (self.login, filters)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        projects = json.loads(resp.text)
        if self._errors_exist('GithubOrgProjects', self.login, projects):
            return False

        return projects

    @connection
    def repositories(self, **kwargs):
        """A list of repositories that the organization owns.

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

        Returns:
            json object where each node contains a repository under this organization
        """
        filters = []
        for key, value in kwargs.items():
            filters.append("{}: {}, ".format(key, value))
        filters = ''.join(filters)
        filters = filters.rstrip(', ')
        query = {"query" : open(GRAPHQL_DIR+'organization_repositories.graphql', 'r').read() % (self.login, filters)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        repositories = json.loads(resp.text)
        if self._errors_exist('GithubOrgRepositories', self.login, repositories):
            return False

        return repositories

    @connection
    def teams(self, **kwargs):
        """A list of teams in this organization.

        Keyword Arguments:
            after (str) - Returns the elements in the list that come after the specified cursor.
            before (str) - Returns the elements in the list that come before the specified cursor.
            first (int) - Returns the first n elements from the list.
            last (int) - Returns the last n elements from the list.
            ldapMapped (Boolean) - If true, filters teams that are mapped to an LDAP Group
                    (Enterprise only)
            orderBy (TeamOrder) - Ordering options for teams returnef rom the connection
            privacy (TeamPrivacy) - If non-null, filters teams according to privacy
            query (str) - If non-null, filters teams with query on team name and team slug
            role (TeamRole) - If non-null, filters teams according to whether the viewer is an admin
                    or member on team
            rootTeamsOnly (Boolean) - If true, restrict to only root teams.  The default value is
                    false.
            userLogins ([str]) - User logins to filter by


        Returns:
            json object where each node contains a team under this organization
        """
        filters = []
        for key, value in kwargs.items():
            filters.append("{}: {}, ".format(key, value))
        filters = ''.join(filters)
        filters = filters.rstrip(', ')
        query = {"query" : open(GRAPHQL_DIR+'organization_teams.graphql', 'r').read() % (self.login, filters)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        teams = json.loads(resp.text)
        if self._errors_exist('GithubOrgTeams', self.login, teams):
            return False

        return teams

    @property
    def avatarUrl(self, size=None):
        """
        :type string
        """
        return self.response['data']['organization']['avatarUrl']

    @property
    def databaseId(self):
        """
        :type: int
        """
        return self.response['data']['organization']['databaseId']

    @property
    def description(self):
        """
        :type: string
        """
        return self.response['data']['organization']['description']

    @property
    def email(self):
        """
        :type: string
        """
        return self.response['data']['organization']['email']

    @property
    def id(self):
        """
        :type: string
        """
        return self.response['data']['organization']['id']

    @property
    def isVerified(self):
        """
        :type: Boolean
        """
        return self.response['data']['organization']['isVerified']

    @property
    def location(self):
        """
        :type: String
        """
        return self.response['data']['organization']['location']

    @property
    def login(self):
        """
        :type: String
        """
        return self.response['data']['organization']['login']

    @property
    def name(self):
        """
        :type: String
        """
        return self.response['data']['organization']['name']

    @property
    def newTeamResourcePath(self):
        """
        :type: String
        """
        return self.response['data']['organization']['newTeamResourcePath']

    @property
    def newTeamUrl(self):
        """
        :type: String
        """
        return self.response['data']['organization']['newTeamUrl']

    @property
    def organizationBillingEmail(self):
        """
        :type: String
        """
        return self.response['data']['organization']['organizationBillingEmail']

    @property
    def project(self):
        """Find project by number.
        :type: dict

        TODO: Need a setter for this property that calls update on a given project number.
        """
        return self.response['data']['organization']['project']

    @property
    def projectsResourcePath(self):
        """
        :type: String
        """
        return self.response['data']['organization']['projectsResourcePath']

    @property
    def projectsUrl(self):
        """
        :type: String
        """
        return self.response['data']['organization']['projectsUrl']

    @property
    def repository(self):
        """
        :type: dict

        TODO: Need a setter for this property that calls update on a given repo name.
        """
        return self.response['data']['organization']['repository']

    @property
    def requiresTwoFactorAuthentication(self):
        """
        :type: Boolean
        """
        return self.response['data']['organization']['requiresTwoFactorAuthentication']

    @property
    def resourcePath(self):
        """
        :type: String
        """
        return self.response['data']['organization']['resourcePath']

    @property
    def samlIdentityProvider(self):
        """
        :type: dict

        TODO: this may eventually just return an object initiated by the dict
        """
        return self.response['data']['organization']['samlIdentityProvider']

    @property
    def team(self):
        """
        :type: dict

        TODO: this may eventually just return an object initiated by the dict
        TODO: Need a setter for this property that calls update on a given team slug.
        """
        return self.response['data']['organization']['team']

    @property
    def teamsResourcePath(self):
        """
        :type: String
        """
        return self.response['data']['organization']['teamsResourcePath']

    @property
    def teamsUrl(self):
        """
        :type: String
        """
        return self.response['data']['organization']['teamsUrl']

    @property
    def url(self):
        """
        :type: String
        """
        return self.response['data']['organization']['url']

    @property
    def viewerCanAdminister(self):
        """
        :type: Boolean
        """
        return self.response['data']['organization']['viewerCanAdminister']

    @property
    def viewerCanCreateProjects(self):
        """
        :type: Boolean
        """
        return self.response['data']['organization']['viewerCanCreateProjects']

    @property
    def viewerCanCreateRepositories(self):
        """
        :type: Boolean
        """
        return self.response['data']['organization']['viewerCanCreateRepositories']

    @property
    def viewerCanCreateTeams(self):
        """
        :type: Boolean
        """
        return self.response['data']['organization']['viewerCanCreateTeams']

    @property
    def viewerIsAMember(self):
        """
        :type: Boolean
        """
        return self.response['data']['organization']['viewerIsAMember']

    @property
    def websiteUrl(self):
        """
        :type: Boolean
        """
        return self.response['data']['organization']['websiteUrl']
