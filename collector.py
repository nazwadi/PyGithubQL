#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
github.py - Collect Github data using the GraphQL API v4

Dependencies
============
This script requires access to Elasticsearch and a redis cache.  The configurations for these
are written in the __init__ function of the GithubCollector class.
"""
import json
import os
#from pathlib import Path
import logging
import logging.config

import datetime
import redis

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import TransportError

from abscollector import Collector
from User import User


class GithubCollector(Collector):
    """Creates a Github collection object."""

    def __init__(self):
        """Configure logger & establish connections to cache and datastore"""
        super(GithubCollector, self).__init__()
        config_file = ('collectors.cfg')
        log_file = self.config['Github']['log_file']
        logging.config.fileConfig(config_file,
                                  defaults={'GithubCollector': log_file}
                                 )
        self.logger = logging.getLogger('GithubCollector')
        self.elasticsearch = Elasticsearch(['localhost:9200'])
        self.redis = redis.Redis(host='127.0.0.1', port=6379, password='')
        self.timestamp = datetime.date.today().isoformat()

    def __repr__(self):
        """Defines the representation of the object when repr() is called"""
        return 'GithubCollector()'

    def __str__(self):
        """Defines a less formal string representation for when str() is called on the object"""
        return 'A Github Data Collector'

    @staticmethod
    def _generate_filename(doc_type, login, *args):
        """Internal function that generates the filenames for json query results

        Arguments:
            doc_type (str)  - the query this filename provides results for
                             i.e. "GithubUser", "GithubRepository", "GithubGists"
            login (str) - the username of the account being queried

        Optional Arguments:
            args (list) - a list of strings to append to the required arguments

        Returns:
            filename (str) - the filename
        """
        filename = []
        filename.append(doc_type)
        filename.append(login)
        for item in args:
            filename.append(item)
            filename.append(datetime.datetime.now().isoformat(timespec='microseconds'))
            filename = '_'.join(filename)
            return filename

    @staticmethod
    def _save_file(json_response, path, filename):
        """Used internally by all save queries to save the json responses
        to a file.

        Arguments:
            json_response (str) - the json string returned from a query
            path (str) - the file path to where the file should be saved
                        filename - the name of the file
        """
        if path is not None:
            if path[-1] != "/":
                path = path+"/"
                filepath = os.path.join(path, filename)
                if not os.path.exists(path):
                    os.makedirs(path)

                with open(filepath+'.json', 'w') as output_file:
                    output_file.write(json_response.text)

    def _save_elasticsearch(self, json_response, index, doc_type):
        """Used internally by all save queries to save the json responses
        directly to an elasticsearch node.

        Arguments:
            json_response (dict) - a json object returned from the graphql query
            index (str) - the name of the elasticsearch index you want the
                        json document to get added into
            nodes (optional, list) - a list of nodes with the following format
                                    ['localhost:443', 'other_host:443']
                                    the default is ['localhost:443']

        Returns:
            boolean - True on success, False on failure
        """
        try:
            _ = self._ensure_es_index(index)
            data = self.elasticsearch.index(index=index,
                                            doc_type=doc_type,
                                            body=json.dumps(json_response))
            self.elasticsearch.indices.refresh(index=index)
        except TransportError as error_msg:
            self.logger.error('%s triggered while trying to index type %s with body: %s',
                              error_msg.error, doc_type, json.dumps(json_response))
            return False
        self.logger.debug("Document added to index '%s' with type '%s'. Document: %s which " \
                          "returned data: %s", index, doc_type, json.dumps(json_response), data)
        return True

    def _ensure_es_index(self, index):
        """Used internally when writing to elasticsearch to ensure a given
        index exists.

        Arguments:
            index (str) - the name of the elasticsearch index
        Returns:
            boolean - True if the index exists, False if something went wrong
        """
        if not self.elasticsearch.indices.exists(index):
            try:
                self.elasticsearch.indices.create(index=index)
            except TransportError as error_msg:
                self.logger.error(str(error_msg.error))
                return False
            self.logger.info('Created Index: %s', index)

        return True


    def _errors_exist(self, doc_type, login, response_payload):
        """Internal function that checks for errors in the response payload
        of a query.

        Arguments:
            doc_type (str) - the type of data being queried (i.e. GithubUser)
            login (str) - the github login queried against when the error occurred
            response_payload (str) - the json string returned from a query

        Returns:
            True if there were errors in the response, otherwise False
        """
        if "errors" in response_payload:
            for _, error in enumerate(response_payload["errors"]):
                message = ':'.join([doc_type, login, str(error)])
                self.logger.error(message)
            return True
        return False

    def _write_to_datastore(self, index, doc_type, document, login, path):
        """Writes to either the filesystem or elasticsearch depending on the
        configuration settings.

        Arguments:
            index (str) - the Elasticsearch index to insert the data to
            doc_type (str) - the Elasticsearch doc_type
            document (str) - a json payload to write to Elasticsearch or the filesystem
            login (str) - the login name of the Github user
            path (str) - the path to the file you want to write the document to
        """
        if self.config['Github']['datastore'] == 'filesystem':
            filename = self._generate_filename(doc_type, login)
            self._save_file(json.dumps(document), path, filename)
        elif self.config['Github']['datastore'] == 'elasticsearch':
            self._save_elasticsearch(document, index, doc_type)
        elif self.config['Github']['datastore'] == 'both':
            filename = self._generate_filename(doc_type, login)
            self._save_file(json.dumps(document), path, filename)
            self._save_elasticsearch(document, index, doc_type)
        else:
            error_msg = "Unable to save result data for {}.  Check " \
                    " configuration file setting: {}" \
                    .format(doc_type, self.config['Github']['datastore'])
            self.logger.error(error_msg)

    def save_user(self, user, path=None):
        """Saves user account information to disk by querying Github GraphQL v4 API.

        Documentation for the upstream Query is located at:
            https://developer.github.com/v4/object/user/

        Required Arguments:
            user - an instance of a GithubUser

        Optional Arguments:
            path (str) - the full file path to where you want the json
                        response saved. Examples: 'c:/your/full/path' or
                        '/home/username/your/full/path'

                        If this option is omitted, files will be saved
                        to the local directory where the script is run.

        Returns:
            boolean - True if query succeeds, False otherwise

        Raises:
            None
        """
        # Check if this user already exists in elasticsearch
        index = ''.join(['gh_user-', self.timestamp])

        self._write_to_datastore(index=index,
                                 doc_type='GithubUser',
                                 document=user.response,
                                 login=user.login,
                                 path=path)

        return True

    def save_commit_comments(self, user, path=None):
        """Saves a list of commit comments made by this user.

        Required Arguments:
            user (GithubUser) - a GithubUser instance

        Optional Arguments:
            path (str) - the filesystem path to where the query result should be saved

        Returns:
            boolean - True if query succeeds, False otherwise

        Raises:
            None
        """
        # Redis has an end_cursor if we've collected this data before
        end_cursor = self.redis.get(''.join(['gh:', user.login, ':commitComments:endCursor']))
        if end_cursor:
            end_cursor = end_cursor.decode('utf-8')
            end_cursor = ''.join(['"', end_cursor, '"'])
            commit_comments = u.commitComments(first=100, after=end_cursor)
        else:
            commit_comments = u.commitComments(first=100)
        if not commit_comments: # False when errors occured (check log file)
            return False
        while True:
            if commit_comments['data']['user']['commitComments']['edges']:
                index = ''.join(['gh_commit_comments-', self.timestamp])
                self._write_to_datastore(index=index,
                                         doc_type='GithubCommitComments',
                                         document=commit_comments,
                                         login=user.login,
                                         path=path)
                has_next_page = commit_comments['data']['user']['commitComments']['pageInfo']['hasNextPage']
                end_cursor = commit_comments['data']['user']['commitComments']['pageInfo']['endCursor']
                if has_next_page:
                    commit_comments = u.commitComments(first=100, after=end_cursor)
                else:
                    # Cache the end_cursor where we last collected data
                    self.redis.set(''.join(['gh:', u.login, ':commitComments:endCursor']), end_cursor)
                    break
            else:
                break

        return True

    def save_followers(self, user, path=None):
        """Saves a list of users the given user is following.

        Required Arguments:
            user (GithubUser) - a GithubUser instance

        Optional Arguments:
            path (str) - the full file path to where you want the json
                        response saved. Examples: 'c:/your/full/path' or
                        '/home/username/your/full/path'

                        If this option is ommitted, files will be saved
                        to the local directory where the script is run.

        Returns:
            boolean - True if query succeeds, False otherwise

        Raises:
            None
        """
        # Redis has an end_cursor if we've collected this data before
        end_cursor = self.redis.get(''.join(['gh:', user.login, ':followers:endCursor']))
        if end_cursor:
            end_cursor = end_cursor.decode('utf-8')
            end_cursor = ''.join(['"', end_cursor, '"'])
            followers = u.followers(first=100, after=end_cursor)
        else:
            followers = u.followers(first=100)

        if not followers:
            return False

        while True:
            try:
                if followers['data']['user']['followers']['edges']:
                    index = ''.join(['gh_followers-', self.timestamp])
                    self._write_to_datastore(index=index,
                                            doc_type='GithubFollowers',
                                            document=followers,
                                            login=user.login,
                                            path=path)
                    has_next_page = followers['data']['user']['followers']['pageInfo']['hasNextPage']
                    end_cursor = followers['data']['user']['followers']['pageInfo']['endCursor']
                    if has_next_page:
                        end_cursor = ''.join(['"', end_cursor, '"'])
                        followers = u.followers(first=100, after=end_cursor)
                    else:
                        # Cache the end_cursor where we last collected data
                        self.redis.set(''.join(['gh:', u.login, ':followers:endCursor']), end_cursor)
                        break
                else:
                    break
            except TypeError as e:
                self.logger.error('GithubFollowers', u.login, e)
                break

        return True

    def save_following(self, user, path=None):
        """Saves a list of users the given user is followed by.

        Required Arguments:
            user (GithubUser) - a GithubUser instance

        Optional Arguments:
            path (str) - the full file path to where you want the json
                         response saved. Examples: 'c:/your/full/path' or
                         '/home/username/your/full/path'

                        If this option is ommitted, files will be saved
                        to the local directory where the script is run.

        Returns:
            boolean - True if query succeeds, False otherwise

        Raises:
            None
        """
        # Redis has an end_cursor if we've collected this data before
        end_cursor = self.redis.get(''.join(['gh:', user.login, ':following:endCursor']))
        if end_cursor:
            end_cursor = end_cursor.decode('utf-8')
            end_cursor = ''.join(['"', end_cursor, '"'])
            following = u.following(first=100, after=end_cursor)
        else:
            following = u.following(first=100)
        if not following:
            return False
        while True:
            if following['data']['user']['following']['edges']:
                index = ''.join(['gh_following-', self.timestamp])
                self._write_to_datastore(index=index,
                                         doc_type='GithubFollowing',
                                         document=following,
                                         login=user.login,
                                         path=path)
                has_next_page = following['data']['user']['following']['pageInfo']['hasNextPage']
                end_cursor = following['data']['user']['following']['pageInfo']['endCursor']
                if has_next_page:
                    following = u.following(first=100, after=end_cursor)
                else:
                    # Cache the end_cursor where we last collected data
                    self.redis.set(''.join(['gh:', u.login, ':following:endCursor']), end_cursor)
                    break
            else:
                break

        return True

    def save_gist_comments(self, user, path=None):
        """Saves a list of gist comments made by this user.

        Required Arguments:
            user (GithubUser) - a GithubUser instance

        Optional:
            path (str) - the filesystem path to where the query result should be saved

        Returns:
            boolean - True if query succeeds, False otherwise

        Raises:
            None
        """
        # Redis has an end_cursor if we've collected this data before
        end_cursor = self.redis.get(''.join(['gh:', user.login, ':gistComments:endCursor']))
        if end_cursor:
            end_cursor = end_cursor.decode('utf-8')
            end_cursor = ''.join(['"', end_cursor, '"'])
            gist_comments = u.gistComments(first=100, after=end_cursor)
        else:
            gist_comments = u.gistComments(first=100)
        if not gist_comments:
            return False
        while True:
            if gist_comments['data']['user']['gistComments']['edges']:
                index = ''.join(['gh_gist_comments-', self.timestamp])
                self._write_to_datastore(index=index,
                                         doc_type='GithubGistComments',
                                         document=gist_comments,
                                         login=user.login,
                                         path=path)
                has_next_page = gist_comments['data']['user']['gistComments']['pageInfo']['hasNextPage']
                end_cursor = gist_comments['data']['user']['gistComments']['pageInfo']['endCursor']
                if has_next_page:
                    gist_comments = u.gistComments(first=100, after=end_cursor)
                else:
                    # Cache the end_cursor where we last collected data
                    self.redis.set(''.join(['gh:', u.login, ':gistComments:endCursor']), end_cursor)
                    break
            else:
                break

        return True

    def save_gists(self, user, path=None):
        """Saves a list of Gists the user has created.

        Arguments:
            user (GithubUser) - a GithubUser instance

        Optional:
            path (str) - the full file path to where you want the json
                        response saved. Examples: 'c:/your/full/path' or
                        '/home/username/your/full/path'

                        If this option is ommitted, files will be saved
                        to the local directory where the script is run.

        Returns:
            boolean - True if query succeeds, False otherwise

        Raises:
            None
        """
        # Redis has an end_cursor if we've collected this data before
        end_cursor = self.redis.get(''.join(['gh:', user.login, ':gists:endCursor']))
        if end_cursor:
            end_cursor = end_cursor.decode('utf-8')
            end_cursor = ''.join(['"', end_cursor, '"'])
            gists = u.gists(first=100,
                            after=end_cursor,
                            orderBy='{direction: DESC, field: CREATED_AT}',
                            privacy='ALL')
        else:
            gists = u.gists(first=100,
                            orderBy='{direction: DESC, field: CREATED_AT}',
                            privacy='ALL')

        if not gists:
            return False

        while True:
            if gists['data']['user']['gists']['edges']:
                index = ''.join(['gh_gists-', self.timestamp])
                self._write_to_datastore(index=index,
                                         doc_type='GithubGists',
                                         document=gists,
                                         login=user.login,
                                         path=path)
                has_next_page = gists['data']['user']['gists']['pageInfo']['hasNextPage']
                end_cursor = gists['data']['user']['gists']['pageInfo']['endCursor']
                if has_next_page:
                    gists = u.gists(first=100,
                                    after=end_cursor,
                                    orderBy='{direction: DESC, field: CREATED_AT}',
                                    privacy='ALL')
                else:
                    # Cache the end_cursor where we last collected data
                    self.redis.set(''.join(['gh:', u.login, ':gists:endCursor']), end_cursor)
                    break
            else:
                break

        return True

    def save_issue_comments(self, user, path=None):
        """Saves a list of issue comments made by this user.

        Required Arguments:
            user (GithubUser) - a GithubUser instance

        Optional Arguments:
            path (str) - the filesystem path to where the query result should be saved

        Returns:
            boolean - True if query succeeds, False otherwise

        Raises:
            None
        """
        # Redis has an end_cursor if we've collected this data before
        end_cursor = self.redis.get(''.join(['gh:', user.login, ':issueComments:endCursor']))
        if end_cursor:
            end_cursor = end_cursor.decode('utf-8')
            end_cursor = ''.join(['"', end_cursor, '"'])
            issue_comments = u.issueComments(first=100, after=end_cursor)
        else:
            issue_comments = u.issueComments(first=100)

        if not issue_comments:
            return False

        while True:
            if issue_comments['data']['user']['issueComments']['edges']:
                index = ''.join(['gh_issue_comments-', self.timestamp])
                self._write_to_datastore(index=index,
                                         doc_type='GithubIssueComments',
                                         document=issue_comments,
                                         login=user.login,
                                         path=path)
                has_next_page = issue_comments['data']['user']['issueComments']['pageInfo']['hasNextPage']
                end_cursor = issue_comments['data']['user']['issueComments']['pageInfo']['endCursor']
                if has_next_page:
                    issue_comments = u.issueComments(first=100, after=end_cursor)
                else:
                    # Cache the end_cursor where we last collected data
                    self.redis.set(''.join(['gh:', u.login, ':issueComments:endCursor']), end_cursor)
                    break
            else:
                break

        return True

    def save_issues(self, user, path=None):
        """Saves a list of issues associated with this user.

        Required Arguments:
            login (str) - the username used to login to GitHub

        Optional Arguments:
            path (str) - the filesystem path to where the query result should be saved

        Returns:
            boolean - True if query succeeds, False otherwise

        Raises:
            None
        """
        # Redis has an end_cursor if we've collected this data before
        last_run = self.redis.get('ghc_last_run').decode('utf-8')
        if last_run is None:
            last_run = '2004-01-01' # pull everything

        end_cursor = self.redis.get(''.join(['gh:', user.login, ':issues:endCursor']))
        if end_cursor:
            end_cursor = end_cursor.decode('utf-8')
            end_cursor = ''.join(['"', end_cursor, '"'])
            issues = u.issues(first=100,
                              after=end_cursor,
                              orderBy='{direction: DESC, field: CREATED_AT}')
        else:
            issues = u.issues(first=100,
                              orderBy='{direction: DESC, field: CREATED_AT}')

        if not issues:
            return False

        while True:
            if issues['data']['user']['issues']['edges']:
                index = ''.join(['gh_issues-', self.timestamp])
                self._write_to_datastore(index=index,
                                         doc_type='GithubIssues',
                                         document=issues,
                                         login=user.login,
                                         path=path)
                has_next_page = issues['data']['user']['issues']['pageInfo']['hasNextPage']
                end_cursor = issues['data']['user']['issues']['pageInfo']['endCursor']
                if has_next_page:
                    issues = u.issues(first=100,
                                      after=end_cursor,
                                      orderBy='{direction: DESC, field: CREATED_AT}',
                                      filterBy='{ since: "'+last_run+'" }')
                else:
                    # Cache the end_cursor where we last collected data
                    self.redis.set(''.join(['gh:', u.login, ':issues:endCursor']), end_cursor)
                    break
            else:
                break

        return True

    def save_organizations(self, user, path=None):
        """Saves a list of organizations the user belongs to.

        Arguments:
            user (GithubUser) - a GithubUser instance

        Optional Arguments:
            path (str) - the filesystem path where the result should be
                            saved (defaults to the local directory the script is running from)

        Returns:
            True if query succeeds, False otherwise

        Raises:
            None
        """
        # Redis has an end_cursor if we've collected this data before
        end_cursor = self.redis.get(''.join(['gh:', user.login, ':organizations:endCursor']))
        if end_cursor:
            end_cursor = end_cursor.decode('utf-8')
            end_cursor = ''.join(['"', end_cursor, '"'])
            organizations = u.organizations(first=100, after=end_cursor)
        else:
            organizations = u.organizations(first=100)
        if not organizations:
            return False
        while True:
            if organizations['data']['user']['organizations']['edges']:
                index = ''.join(['gh_organizations-', self.timestamp])
                self._write_to_datastore(index=index,
                                         doc_type='GithubOrganizations',
                                         document=organizations,
                                         login=user.login,
                                         path=path)
                has_next_page = organizations['data']['user']['organizations']['pageInfo']['hasNextPage']
                end_cursor = organizations['data']['user']['organizations']['pageInfo']['endCursor']
                if has_next_page:
                    organizations = u.organizations(first=100, after=end_cursor)
                else:
                    # Cache the end_cursor where we last collected data
                    self.redis.set(''.join(['gh:', u.login, ':organizations:endCursor']), end_cursor)
                    break
            else:
                break

        return True

    def save_pinned_repositories(self, user, path=None):
        """Saves a list of repositories this user has pinned to their profile.

        Required Arguments:
            user (GithubUser) - a GithubUser instance

        Optional Arguments:
            path (str) - filesystem path where result should be saved

        Returns:
            True if query succeeds, False otherwise

        Raises:
            None
        """
        # Redis has an end_cursor if we've collected this data before
        end_cursor = self.redis.get(''.join(['gh:', user.login, ':pinnedRepositories:endCursor']))
        if end_cursor:
            end_cursor = end_cursor.decode('utf-8')
            end_cursor = ''.join(['"', end_cursor, '"'])
            pinned_repositories = u.pinnedRepositories(first=100, # usually more like 6, but we want all possible
                                                       after=end_cursor,
                                                       orderBy='{direction: DESC, field: CREATED_AT}')
        else:
            pinned_repositories = u.pinnedRepositories(first=100,
                                                       orderBy='{direction: DESC, field: CREATED_AT}')

        if not pinned_repositories:
            return False

        while True:
            if pinned_repositories['data']['user']['pinnedRepositories']['edges']:
                index = ''.join(['gh_pinned_repositories-', self.timestamp])
                self._write_to_datastore(index=index,
                                         doc_type='GithubPinnedRepositories',
                                         document=pinned_repositories,
                                         login=user.login,
                                         path=path)
                has_next_page = pinned_repositories['data']['user']['pinnedRepositories']['pageInfo']['hasNextPage']
                end_cursor = pinned_repositories['data']['user']['pinnedRepositories']['pageInfo']['endCursor']
                if has_next_page:
                    pinned_repositories = u.pinnedRepositories(first=100,
                                                               after=end_cursor,
                                                               orderBy='{direction: DESC, field: CREATED_AT}')
                else:
                    # Cache the end_cursor where we last collected data
                    self.redis.set(''.join(['gh:', u.login, ':pinnedRepositories:endCursor']), end_cursor)
                    break
            else:
                break

        return True

    def save_public_keys(self, user, path=None):
        """Saves a list of public keys associated with this user.

        Required Arguments:
            user (GithubUser) - a GithubUser instance

        Optional Arguments:
            path (str) - the filesystem path to where the query result should be
            saved; defaults to the current working directory

        Returns:
            boolean - True if query succeeds, False otherwise

        Raises:
            None
        """
        # Redis has an end_cursor if we've collected this data before
        end_cursor = self.redis.get(''.join(['gh:', user.login, ':publicKeys:endCursor']))
        if end_cursor:
            end_cursor = end_cursor.decode('utf-8')
            end_cursor = ''.join(['"', end_cursor, '"'])
            public_keys = u.publicKeys(first=100, after=end_cursor)
        else:
            public_keys = u.publicKeys(first=100)

        if not public_keys:
            return False

        while True:
            if public_keys['data']['user']['publicKeys']['edges']:
                index = ''.join(['gh_public_keys-', self.timestamp])
                self._write_to_datastore(index=index,
                                         doc_type='GithubPublicKeys',
                                         document=public_keys,
                                         login=user.login,
                                         path=path)
                has_next_page = public_keys['data']['user']['publicKeys']['pageInfo']['hasNextPage']
                end_cursor = public_keys['data']['user']['publicKeys']['pageInfo']['endCursor']
                if has_next_page:
                    public_keys = u.publicKeys(first=100, after=end_cursor)
                else:
                    # Cache the end_cursor where we last collected data
                    self.redis.set(''.join(['gh:', u.login, ':publicKeys:endCursor']), end_cursor)
                    break
            else:
                break

        return True

    def save_pull_requests(self, user, path=None):
        """Saves a list of pull requests associated with this user.

        Required Arguments:
            user (GithubUser) - a GithubUser instance

        Optional Arguments:
            path (str) - the filesystem path to where the query result should be
                         saved; defaults to the current working directory

        Returns:
            boolean - True if query succeeds, False otherwise

        Raises:
            None
        """
        # Redis has an end_cursor if we've collected this data before
        end_cursor = self.redis.get(''.join(['gh:', user.login, ':pullRequests:endCursor']))
        if end_cursor:
            end_cursor = end_cursor.decode('utf-8')
            end_cursor = ''.join(['"', end_cursor, '"'])
            pull_requests = u.pullRequests(first=100,
                                           after=end_cursor,
                                           orderBy='{direction: DESC, field: CREATED_AT}')
        else:
            pull_requests = u.pullRequests(first=100,
                                           orderBy='{direction: DESC, field: CREATED_AT}')

        if not pull_requests:
            return False

        while True:
            if pull_requests['data']['user']['pullRequests']['edges']:
                index = ''.join(['gh_pull_requests-', self.timestamp])
                self._write_to_datastore(index=index,
                                         doc_type='GithubPullRequests',
                                         document=pull_requests,
                                         login=user.login,
                                         path=path)
                has_next_page = pull_requests['data']['user']['pullRequests']['pageInfo']['hasNextPage']
                end_cursor = pull_requests['data']['user']['pullRequests']['pageInfo']['endCursor']
                if has_next_page:
                    pull_requests = u.pullRequests(first=100,
                                                   after=end_cursor,
                                                   orderBy='{direction: DESC, field: CREATED_AT}')
                else:
                    # Cache the end_cursor where we last collected data
                    self.redis.set(''.join(['gh:', u.login, ':pullRequests:endCursor']), end_cursor)
                    break
            else:
                break

        return True

    def save_repositories(self, user, path=None):
        """Saves a list of repositories that the user owns.

        Required Arguments:
            user (GithubUser) - a GithubUser instance

        Optional Arguments:
            path (str) - filesystem path where result should be saved

        Returns:
            True if query succeeds, False otherwise

        Raises:
            None
        """
        # Redis has an end_cursor if we've collected this data before
        end_cursor = self.redis.get(''.join(['gh:', user.login, ':repositories:endCursor']))
        if end_cursor:
            end_cursor = end_cursor.decode('utf-8')
            end_cursor = ''.join(['"', end_cursor, '"'])
            repositories = u.repositories(first=100,
                                          after=end_cursor,
                                          orderBy='{direction: DESC, field: CREATED_AT}')
        else:
            repositories = u.repositories(first=100,
                                          orderBy='{direction: DESC, field: CREATED_AT}')

        if not repositories:
            return False

        while True:
            if repositories['data']['user']['repositories']['edges']:
                index = ''.join(['gh_repositories-', self.timestamp])
                self._write_to_datastore(index=index,
                                         doc_type='GithubRepositories',
                                         document=repositories,
                                         login=user.login,
                                         path=path)
                has_next_page = repositories['data']['user']['repositories']['pageInfo']['hasNextPage']
                end_cursor = repositories['data']['user']['repositories']['pageInfo']['endCursor']
                if has_next_page:
                    repositories = u.repositories(first=100,
                                                  after=end_cursor,
                                                  orderBy='{direction: DESC, field: CREATED_AT}')
                else:
                    # Cache the end_cursor where we last collected data
                    self.redis.set(''.join(['gh:', u.login, ':repositories:endCursor']), end_cursor)
                    break
            else:
                break

        return True

    def save_repositories_contributed_to(self, user, path=None):
        """Saves a list of repositories that the user recently contributed
        to other than their own.

        Required Arguments:
            user (GithubUser) - a GithubUser instance

        Optional Arguments:
            path (str) - filesystem path where result should be saved

        Returns:
            True if query succeeds, False otherwise

        Raises:
            None
        """
        # Redis has an end_cursor if we've collected this data before
        end_cursor = self.redis.get(''.join(['gh:', user.login, ':repositoriesContributedTo:endCursor']))
        if end_cursor:
            end_cursor = end_cursor.decode('utf-8')
            end_cursor = ''.join(['"', end_cursor, '"'])
            repositories_contributed_to = u.repositoriesContributedTo(first=100,
                                                                      after=end_cursor,
                                                                      orderBy='{direction: DESC, field: CREATED_AT}')
        else:
            repositories_contributed_to = u.repositoriesContributedTo(first=100,
                                                                      orderBy='{direction: DESC, field: CREATED_AT}')

        if not repositories_contributed_to:
            return False

        while True:
            if repositories_contributed_to['data']['user']['repositoriesContributedTo']['edges']:
                index = ''.join(['gh_repositories_contributed_to-', self.timestamp])
                self._write_to_datastore(index=index,
                                         doc_type='GithubRepositoriesContributedTo',
                                         document=repositories_contributed_to,
                                         login=user.login,
                                         path=path)
                has_next_page = repositories_contributed_to['data']['user']['repositoriesContributedTo']['pageInfo']['hasNextPage']
                end_cursor = repositories_contributed_to['data']['user']['repositoriesContributedTo']['pageInfo']['endCursor']
                if has_next_page:
                    repositories_contributed_to = u.repositoriesContributedTo(first=100,
                                                                              after=end_cursor,
                                                                              orderBy='{direction: DESC, field: CREATED_AT}')
                else:
                    # Cache the end_cursor where we last collected data
                    self.redis.set(''.join(['gh:', u.login, ':repositoriesContributedTo:endCursor']), end_cursor)
                    break
            else:
                break

        return True

    def save_starred_repositories(self, user, path=None):
        """Saves a list of repositories that the user has starred.

        Required Arguments:
            user (GithubUser) - a GithubUser instance

        Optional Arguments:
            path (str) - the path to the file where the result should be
                        saved; defaults to the local directory

        Returns:
            True if query was successful, False otherwise
        """
        # Redis has an end_cursor if we've collected this data before
        end_cursor = self.redis.get(''.join(['gh:', user.login, ':starredRepositories:endCursor']))
        if end_cursor:
            end_cursor = end_cursor.decode('utf-8')
            end_cursor = ''.join(['"', end_cursor, '"'])
            starred_repositories = u.starredRepositories(first=100,
                                                         after=end_cursor,
                                                         orderBy='{direction: DESC, field: STARRED_AT}')
        else:
            starred_repositories = u.starredRepositories(first=100,
                                                         orderBy='{direction: DESC, field: STARRED_AT}')

        if not starred_repositories:
            return False

        while True:
            try:
                if starred_repositories['data']['user']['starredRepositories']['edges']:
                    index = ''.join(['gh_starred_repositories-', self.timestamp])
                    self._write_to_datastore(index=index,
                                            doc_type='GithubStarredRepositories',
                                            document=starred_repositories,
                                            login=user.login,
                                            path=path)
                    has_next_page = starred_repositories['data']['user']['starredRepositories']['pageInfo']['hasNextPage']
                    end_cursor = starred_repositories['data']['user']['starredRepositories']['pageInfo']['endCursor']
                    if has_next_page:
                        end_cursor = ''.join(['"', end_cursor, '"'])
                        starred_repositories = u.starredRepositories(first=100,
                                                                    after=end_cursor,
                                                                    orderBy='{direction: DESC, field: STARRED_AT}')
                    else:
                        # Cache the end_cursor where we last collected data
                        self.redis.set(''.join(['gh:', u.login, ':starredRepositories:endCursor']), end_cursor)
                        break
                else:
                    break
            except TypeError as e:
                self.logger.error('GithubStarredRepositories', u.login, e)
                break

        return True

    def save_watching(self, user, path=None):
        """Saves a list of repositories that the given user is watching.

        Required Arguments:
            user (GithubUser) - a GithubUser instance

        Optional Arguments:
            path (str) - the path to the file where the result should be
                            saved; defaults to the local directory


        Returns:
            True if the query succeeds, False otherwise

        Raises:
            None
        """
        # Redis has an end_cursor if we've collected this data before
        end_cursor = self.redis.get(''.join(['gh:', user.login, ':watching:endCursor']))
        if end_cursor:
            end_cursor = end_cursor.decode('utf-8')
            end_cursor = ''.join(['"', end_cursor, '"'])
            watching = u.watching(first=100,
                                  after=end_cursor,
                                  orderBy='{direction: DESC, field: CREATED_AT}')
        else:
            watching = u.watching(first=100,
                                  orderBy='{direction: DESC, field: CREATED_AT}')

        if not watching:
            return False

        while True:
            if watching['data']['user']['watching']['edges']:
                index = ''.join(['gh_watching-', self.timestamp])
                self._write_to_datastore(index=index,
                                         doc_type='GithubWatching',
                                         document=watching,
                                         login=user.login,
                                         path=path)
                has_next_page = watching['data']['user']['watching']['pageInfo']['hasNextPage']
                end_cursor = watching['data']['user']['watching']['pageInfo']['endCursor']
                if has_next_page:
                    watching = u.watching(first=100,
                                          after=end_cursor,
                                          orderBy='{direction: DESC, field: CREATED_AT}')
                else:
                    # Cache the end_cursor where we last collected data
                    self.redis.set(''.join(['gh:', u.login, ':watching:endCursor']), end_cursor)
                    break
            else:
                break

        return True

    def verify(self):
        """Verify the api credentials are valid"""
        pass


if __name__ == "__main__":
    GC = GithubCollector()
    with open('/path/to/github_users', 'r') as login_list:
        for name in login_list:
            name = name.replace('\n', '').strip()
            try:
                u = User(name)
            except TypeError as e:
                print("Error: Type error on {}. Message: {}".format(name, e))
                continue

            try:
                GC.save_user(u)
            except TypeError as e:
                print('TypeError occurred as save_user({}), message: {}'.format(name, e))
                continue

            # All collector functions return True on success - we don't need that value here
            # because all errors are logged in /var/log/pipeline/github.log
            _ = GC.save_commit_comments(u)
            _ = GC.save_followers(u)
            _ = GC.save_following(u)
            _ = GC.save_gist_comments(u)
            _ = GC.save_gists(u)
            _ = GC.save_issue_comments(u)
            _ = GC.save_issues(u)
            _ = GC.save_organizations(u)
            _ = GC.save_pinned_repositories(u)
            _ = GC.save_public_keys(u)
            _ = GC.save_pull_requests(u)
            _ = GC.save_repositories(u)
            _ = GC.save_repositories_contributed_to(u)
            _ = GC.save_starred_repositories(u)
            _ = GC.save_watching(u)
