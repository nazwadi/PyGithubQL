#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
User.py - a Github APIv4 object

"""

import json
import os

import requests

from GithubObject import GithubObject
from Repositories import Repositories
from decorators import connection

GRAPHQL_DIR = ''.join([os.path.dirname(os.path.realpath(__file__)), '/graphql/User/'])


class User(GithubObject):
    """This class represents Users.  Upstream reference is at
    https://developer.github.com/v4/object/user/"""

    def __init__(self, login):
        """
        Arguments:
            login (str) - the Github user's username
        """
        super(User, self).__init__()
        self._login = None
        self.update(login)

    def __repr__(self):
        return 'User(login={!r}, url={!r})'.format(self.login, self.url)

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (self.login, self.id) == (other.login, other.id)

    def __ne__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (self.login, self.id) != (other.login, other.id)

    def as_cypher_create_query(self):
        """Returns User object in a Cypher CREATE Query format"""
        query = "CREATE (n:GithubUser { avatarUrl: '%s', \
                                        bio : '%s', \
                                        bioHTML : '%s', \
                                        company: '%s', \
                                        companyHTML: '%s', \
                                        createdAt: '%s', \
                                        email: '%s', \
                                        isBountyHunter: %s, \
                                        isCampusExpert: %s, \
                                        isDeveloperProgramMember: %s, \
                                        isEmployee: %s, \
                                        isHireable: %s, \
                                        isSiteAdmin: %s, \
                                        isViewer: %s, \
                                        location: '%s', \
                                        login: '%s', \
                                        name: '%s', \
                                        resourcePath: '%s', \
                                        updatedAt: '%s', \
                                        url: '%s', \
                                        id: '%s', \
                                        viewerCanFollow: %s, \
                                        viewerIsFollowing: %s, \
                                        websiteUrl: '%s'})" \
                % (self.avatarUrl, self.bio, self.bioHTML, self.company, \
                   self.companyHTML, self.createdAt, self.email, self.isBountyHunter, \
                   self.isCampusExpert, self.isDeveloperProgramMember, \
                   self.isEmployee, self.isHireable, self.isSiteAdmin, \
                   self.isViewer, self.location, self.login, self.name, \
                   self.resourcePath, self.updatedAt, self.url, self.id, \
                   self.viewerCanFollow, self.viewerIsFollowing, \
                   self.websiteUrl)

        return ' '.join(query.split())

    def update(self, login):
        """Updates the User object with new data by querying the
        Github endpoint.

        Arguments:
            login (str) - the Github user's username

        Returns:
            boolean - False if errors exist, True otherwise
        """
        self._login = login
        query = {"query" : open(GRAPHQL_DIR+'user.graphql', 'r').read() % (login)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        self.response = json.loads(resp.text)
        if self._errors_exist('GithubUser', login, self.response):
            return False

        return True

    @connection
    def commitComments(self, **kwargs):
        """A list of commit comments made by this user. This is a connection (edge/relationships).

        Keyword Arguments:
            after (str) - Returns the elements in the list that come after the specified cursor.
            before (str) - Returns the elements in the list that come before the specified cursor.
            first (int) - Returns the first n elements from the list.
            last (int) - Returns the last n elements from the list.

        Returns:
            Comments (GithubObject) - an iterable data object of comments

        Raises:
            None
        """
        filters = []
        for key, value in kwargs.items():
            filters.append("{}: {}, ".format(key, value))
        filters = ''.join(filters)
        filters = filters.rstrip(', ')
        query = {"query" : open(GRAPHQL_DIR+'user_commit_comments.graphql', 'r').read() % (self.login, filters)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        commit_comments = json.loads(resp.text)
        if self._errors_exist('GithubCommitComments', self.login, commit_comments):
            return False

        return commit_comments

    @connection
    def followers(self, **kwargs):
        """A list of users the given user is followed by. This is a connection (edge/relationship).

        Keyword Arguments:
            after (str) - Returns the elements in the list that come after the specified cursor.
            before (str) - Returns the elements in the list that come before the specified cursor.
            first (int) - Returns the first n elements from the list.
            last (int) - Returns the last n elements from the list.

        Returns:
            Users (GithubObject) - an iterable data object of github users

        Raises:
            None
        """
        filters = []
        for key, value in kwargs.items():
            filters.append("{}: {},".format(key, value))
        filters = ''.join(filters)
        query = {"query" : open(GRAPHQL_DIR+'user_followers.graphql', 'r').read() % (self.login, filters)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        followers = json.loads(resp.text)
        if self._errors_exist('GithubFollowers', self.login, followers):
            return False

        return followers

    @connection
    def following(self, **kwargs):
        """A list of users the given user is following. This is a connection (edge/relationship).

        Keyword Arguments:
            after (str) - Returns the elements in the list that come after the specified cursor.
            before (str) - Returns the elements in the list that come before the specified cursor.
            first (int) - Returns the first n elements from the list.
            last (int) - Returns the last n elements from the list.

        Returns:
            Users (GithubObject) - an iterable data object of github users

        Raises:
            None
        """
        filters = []
        for key, value in kwargs.items():
            filters.append("{}: {},".format(key, value))
        filters = ''.join(filters)
        query = {"query" : open(GRAPHQL_DIR+'user_following.graphql', 'r').read() % (self.login, filters)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        following = json.loads(resp.text)
        if self._errors_exist('GithubFollowing', self.login, following):
            return False

        return following

    @connection
    def gistComments(self, **kwargs):
        """A list of gist comments made by this user. This is a connection (edge/relationship).

        Keyword Arguments:
            after (str) - Returns the elements in the list that come after the specified cursor.
            before (str) - Returns the elements in the list that come before the specified cursor.
            first (int) - Returns the first n elements from the list.
            last (int) - Returns the last n elements from the list.

        Returns:
            GistComments (GithubObject) - an iterable data object of github gist comments

        Raises:
            NotImplementedError
        """
        filters = []
        for key, value in kwargs.items():
            filters.append("{}: {},".format(key, value))
        filters = ''.join(filters)
        query = {"query" : open(GRAPHQL_DIR+'user_gist_comments.graphql', 'r').read() % (self.login, filters)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        gist_comments = json.loads(resp.text)
        if self._errors_exist('GithubGistComment', self.login, gist_comments):
            return False

        return gist_comments

    @connection
    def gists(self, **kwargs):
        """A list of the Gists the user has created. This is a connection (edge/relationship).

        Keyword Arguments:
            after (str) - Returns the elements in the list that come after the specified cursor.
            before (str) - Returns the elements in the list that come before the specified cursor.
            first (int) - Returns the first n elements from the list.
            last (int) - Returns the last n elements from the list.
            orderBy (GistOrder) - Ordering options for gists returned from the connection
            privacy (GistPrivacy) - Filters Gists according to privacy

        Returns:
            Comments (GithubObject) - an iterable data object of comments

        Raises:
            NotImplementedError
        """
        filters = []
        for key, value in kwargs.items():
            filters.append("{}: {},".format(key, value))
        filters = ''.join(filters)
        query = {"query" : open(GRAPHQL_DIR+'user_gists.graphql', 'r').read() % (self.login, filters)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        gists = json.loads(resp.text)
        if self._errors_exist('GithubGist', self.login, gists):
            return False

        return gists

    @connection
    def issueComments(self, **kwargs):
        """A list of issue comments made by this user. This is a connection (edge/relationship).

        Keyword Arguments:
            after (str) - Returns the elements in the list that come after the specified cursor.
            before (str) - Returns the elements in the list that come before the specified cursor.
            first (int) - Returns the first n elements from the list.
            last (int) - Returns the last n elements from the list.

        Returns:
            Comments (GithubObject) - an iterable data object of comments

        Raises:
            NotImplementedError
        """
        filters = []
        # kwargs contains the Optional Arguments: after, before, first, last
        for key, value in kwargs.items():
            filters.append("{}: {},".format(key, value))
        filters = ''.join(filters)
        query = {"query" : open(GRAPHQL_DIR+'user_issue_comments.graphql', 'r').read() % (self.login, filters)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        issue_comments = json.loads(resp.text)
        if self._errors_exist('GithubIssueComment', self.login, issue_comments):
            return False

        return issue_comments

    @connection
    def issues(self, **kwargs):
        """A list of issues associated with this user. This is a connection (edge/relationship).

        Keyword Arguments:
            after (str) - Returns the elements in the list that come after the specified cursor.
            before (str) - Returns the elements in the list that come before the specified cursor.
            filterBy (IssueFilters) - Filtering options for issues returned from the connection.
            first (int) - Returns the first n elements from the list.
            labels ([str,]) - A list of label names to filter the pull requests by.
            last (int) - Returns the last n elements from the list.
            orderBy (IssueOrder) - Ordering options for issues returned from the connection.
            states ([IssueState]) - A list of states to filter the issue by.

        Returns:
            Issues (GithubObject) - an iterable data object of issues

        Raises:
            None
        """
        filters = []
        for key, value in kwargs.items():
            filters.append("{}: {},".format(key, value))
        filters = ''.join(filters)
        query = {"query" : open(GRAPHQL_DIR+'user_issues.graphql', 'r').read() % (self.login, filters)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        issues = json.loads(resp.text)
        if self._errors_exist('GithubIssues', self.login, issues):
            return False

        return issues

    @connection
    def organizations(self, **kwargs):
        """A list of organizations the user belongs to. This is a connection (edge/relationship).

        Keyword Arguments:
            after (str) - Returns the elements in the list that come after the specified cursor.
            before (str) - Returns the elements in the list that come before the specified cursor.
            first (int) - Returns the first n elements from the list.
            last (int) - Returns the last n elements from the list.

        Returns:
            Organizations (GithubObject) - an iterable data object of organizations

        Raises:
            NotImplementedError
        """
        filters = []
        for key, value in kwargs.items():
            filters.append("{}: {},".format(key, value))
        filters = ''.join(filters)
        query = {"query" : open(GRAPHQL_DIR+'user_organizations.graphql', 'r').read() % (self.login, filters)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        organizations = json.loads(resp.text)
        if self._errors_exist('GithubOrganization', self.login, organizations):
            return False

        return organizations

    @connection
    def pinnedRepositories(self, **kwargs):
        """A list of repositories this user has pinned to their profile. This is a connection
        (edge/relationship).

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
            Repositories (GithubObject) - an iterable data object of Repositories

        Raises:
            NotImplementedError
        """
        filters = []
        for key, value in kwargs.items():
            filters.append("{}: {},".format(key, value))
        filters = ''.join(filters)
        query = {"query" : open(GRAPHQL_DIR+'user_pinned_repositories.graphql', 'r').read() % (self.login, filters)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        pinned_repositories = json.loads(resp.text)
        if self._errors_exist('GithubPinnedRepositories', self.login, pinned_repositories):
            return False

        return pinned_repositories

    @connection
    def publicKeys(self, **kwargs):
        """A list of public keys associated with this user. This is a connection
        (edge/relationship).

        Keyword Arguments:
            after (str) - Returns the elements in the list that come after the specified cursor.
            before (str) - Returns the elements in the list that come before the specified cursor.
            first (int) - Returns the first n elements from the list.
            last (int) - Returns the last n elements from the list.

        Returns:
            PublicKeys (GithubObject) - an iterable data object of public keys

        Raises:
            NotImplementedError
        """
        filters = []
        for key, value in kwargs.items():
            filters.append("{}: {},".format(key, value))
        filters = ''.join(filters)
        query = {"query" : open(GRAPHQL_DIR+'user_public_keys.graphql', 'r').read() % (self.login, filters)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        public_keys = json.loads(resp.text)
        if self._errors_exist('GithubPublicKeys', self.login, public_keys):
            return False

        return public_keys

    @connection
    def pullRequests(self, **kwargs):
        """A list of pull requests associated with this user. This is a connection
        (edge/relationship).

        Keyword Arguments:
            after (str) - Returns the elements in the list that come after the specified cursor.
            baseRefName (str) - The base ref name to filter the pull requests by.
            before (str) - Returns the elements in the list that come before the specified cursor.
            first (int) - Returns the first n elements from the list.
            headRefName (str) - The head ref name to filter the pull requests by.
            labels ([String]) - A list of label names to filter the pull requests by.
            last (int) - Returns the last n elements from the list.
            orderBy (IssueOrder) - Ordering options for pull requests returned from the connection.
            states ([PullRequestState]) - A list of states to filter the pull requests by.

        Returns:
            PullRequest (GithubObject) - an iterable data object of pull requests

        Raises:
            NotImplementedError
        """
        filters = []
        for key, value in kwargs.items():
            filters.append("{}: {},".format(key, value))
        filters = ''.join(filters)
        query = {"query" : open(GRAPHQL_DIR+'user_pull_requests.graphql', 'r').read() % (self.login, filters)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        pull_requests = json.loads(resp.text)
        if self._errors_exist('GithubPullRequests', self.login, pull_requests):
            return False

        return pull_requests

    @connection
    def repositories(self, **kwargs):
        """A list of repositories that the user owns. This is a connection (edge/relationship).

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
            Repositories (GithubObject) - an iterable data object of pull requests

        Raises:
            NotImplementedError
        """
        filters = []
        for key, value in kwargs.items():
            filters.append("{}: {},".format(key, value))
        filters = ''.join(filters)
        query = {"query" : open(GRAPHQL_DIR+'user_repositories.graphql', 'r').read() % (self.login, filters)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        repositories = json.loads(resp.text)
        if self._errors_exist('GithubRepositories', self.login, repositories):
            return False

        return repositories

    @connection
    def repositoriesContributedTo(self, **kwargs):
        """A list of repositories that the user recently contributed to. This is a connection
        (edge/relationship).

        Keyword Arguments:
            after (str) - Returns the elements in the list that come after the specified cursor.
            before (str) - Returns the elements in the list that come before the specified cursor.
            contributionTypes ([RepositoryContributionType]) - If non-null, include only the
                    specified types of contributions.  The GitHub.com UI uses [COMMIT, ISSUE, PULL_REQUEST,
                    REPOSITORY]
            first (int) - Returns the first n elements from the list.
            includeUserRepositories (Boolean) - If true, include user repositories
            isLocked (Boolean) - If non-null, filters repositories according to whether they have
                    been locked
            last (int) - Returns the last n elements from the list.
            orderBy (RepositoryOrder) - Ordering options for repositories returned from the
                    connection
            privacy (RepositoryPrivacy) - If non-null, filters repositories according to privacy

        Returns:
            Repositories (GithubObject) - an iterable data object of repositories

        Raises:
            None
        """
        filters = []
        for key, value in kwargs.items():
            filters.append("{}: {},".format(key, value))
        filters = ''.join(filters)
        query = {"query" : open(GRAPHQL_DIR+'user_repositories_contributed_to.graphql', 'r').read() % (self.login, filters)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        repositories_contributed_to = json.loads(resp.text)
        if self._errors_exist('GithubRepositoriesContributedTo', self.login, repositories_contributed_to):
            return False

        return repositories_contributed_to

    @connection
    def starredRepositories(self, **kwargs):
        """Repositories the user has starred. This is a connection (edge/relationship).

        Keyword Arguments:
            after (str) - Returns the elements in the list that come after the specified cursor.
            before (str) - Returns the elements in the list that come before the specified cursor.
            first (int) - Returns the first n elements from the list.
            last (int) - Returns the last n elements from the list.
            orderBy (StarOrder) - Order for connection
            ownedByViewer (Boolean) - Filters starred repositories to only return repositories owned
                    by the viewer.

        Returns:
            Repositories (GithubObject) - an iterable data object of repositories

        Raises:
            None
        """
        filters = []
        for key, value in kwargs.items():
            filters.append("{}: {},".format(key, value))
        filters = ''.join(filters)
        query = {"query" : open(GRAPHQL_DIR+'user_starred_repositories.graphql', 'r').read() % (self.login, filters)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        starred_repositories = json.loads(resp.text)
        if self._errors_exist('GithubStarredRepositories', self.login, starred_repositories):
            return False

        return starred_repositories

    @connection
    def watching(self, **kwargs):
        """A list of repositories the given user is watching. This is a connection
        (edge/relationship).

        Keyword Arguments:
            affiliations ([RepositoryAffiliation]) - Affiliation options for repositories returned
                    from the connection

                    The default value is
                    ["OWNER", "COLLABORATOR", "ORGANIZATION_MEMBER"]
            after (str) - Returns the elements in the list that come after the specified cursor.
            before (str) - Returns the elements in the list that come before the specified cursor.
            first (int) - Returns the first n elements from the list.
            isLocked (Boolean) - If non-null, filters repositories according to whether they have
                    been locked.
            last (int) - Returns the last n elements from the list.
            orderBy (RepositoryOrder) - Ordering options for repositories returned from the
                                        connection
            ownerAffiliations ([RepositoryAffiliation]) - Array of owner's affiliation options for
                    repositories returned from the connection.  For example, OWNER will include only
                    repositories that the organization or user being viewed owns.

                    The default value is ["OWNER", "COLLABORATOR"].
            privacy (RepositoryPrivacy) - If non-null, filters repositories according to privacy.

        Returns:
            Repositories (GithubObject) - an iterable data object of repositories

        Raises:
            NotImplementedError
        """
        filters = []
        for key, value in kwargs.items():
            filters.append("{}: {},".format(key, value))
        filters = ''.join(filters)
        query = {"query" : open(GRAPHQL_DIR+'user_watching.graphql', 'r').read() % (self.login, filters)}
        resp = requests.post(url=self.endpoint, json=query, headers=self.headers)
        watching = json.loads(resp.text)
        if self._errors_exist('GithubWatching', self.login, watching):
            return False

        return watching

    @property
    def avatarUrl(self, size=None):
        """
        :type: str
        """
        return self.response['data']['user']['avatarUrl']

    @property
    def bio(self):
        """
        :type: str
        """
        return self.response['data']['user']['bio']

    @property
    def bioHTML(self):
        """
        :type: str
        """
        return self.response['data']['user']['bioHTML']

    @property
    def company(self):
        """
        :type: str
        """
        return self.response['data']['user']['company']

    @property
    def companyHTML(self):
        """
        :type: str
        """
        return self.response['data']['user']['companyHTML']

    @property
    def createdAt(self):
        """Identifies the date and time when the object was created.
        :type: string  (An ISO-8601 encoded UTC date string)
        """
        return self.response['data']['user']['createdAt']

    @property
    def databaseId(self):
        """
        :type: int
        """
        return self.response['data']['user']['databaseId']

    @property
    def email(self):
        """
        :type: str
        """
        return self.response['data']['user']['email']

    @property
    def id(self):
        """
        :type: str
        """
        return self.response['data']['user']['id']

    @property
    def isBountyHunter(self):
        """
        :type: Boolean
        """
        return self.response['data']['user']['isBountyHunter']

    @property
    def isCampusExpert(self):
        """
        :type: Boolean
        """
        return self.response['data']['user']['isCampusExpert']

    @property
    def isDeveloperProgramMember(self):
        """
        :type: Boolean
        """
        return self.response['data']['user']['isDeveloperProgramMember']

    @property
    def isEmployee(self):
        """
        :type: Boolean
        """
        return self.response['data']['user']['isEmployee']

    @property
    def isHireable(self):
        """
        :type: Boolean
        """
        return self.response['data']['user']['isHireable']

    @property
    def isSiteAdmin(self):
        """
        :type: Boolean
        """
        return self.response['data']['user']['isSiteAdmin']

    @property
    def isViewer(self):
        """
        :type: Boolean
        """
        return self.response['data']['user']['isViewer']

    @property
    def location(self):
        """
        :type: string
        """
        return self.response['data']['user']['location']

    @property
    def login(self):
        """
        :type: string
        """
        return self.response['data']['user']['login']

    @property
    def name(self):
        """
        :type: string
        """
        return self.response['data']['user']['name']

    @property
    def resourcePath(self):
        """
        :type: string
        """
        return self.response['data']['user']['resourcePath']

    @property
    def updatedAt(self):
        """
        :type: string
        """
        return self.response['data']['user']['updatedAt']

    @property
    def url(self):
        """
        :type: string
        """
        return self.response['data']['user']['url']

    @property
    def viewerCanFollow(self):
        """
        :type: string
        """
        return self.response['data']['user']['viewerCanFollow']

    @property
    def viewerIsFollowing(self):
        """
        :type: string
        """
        return self.response['data']['user']['viewerIsFollowing']

    @property
    def websiteUrl(self):
        """
        :type: string
        """
        return self.response['data']['user']['websiteUrl']
