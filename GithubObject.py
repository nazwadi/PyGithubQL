#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
from configparser import ConfigParser
from abc import ABCMeta, abstractmethod
import os
import logging
import logging.config

LOCAL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))


class GithubObject(object, metaclass=ABCMeta):
    """Base class for a Github Object"""

    def __init__(self):
        self.config = ConfigParser()
        self.config.read(''.join([LOCAL_DIR, '/collectors.cfg']))
        self.endpoint = 'https://api.github.com/graphql'
        self.api_token = self.config['Github']['personal_access_token']
        self.headers = {'Authorization': 'token %s' % self.api_token, \
                        'Accept' : 'application/vnd.github.starfire-preview+json' }
        # Below is for logging
        config_file = (''.join([LOCAL_DIR, '/collectors.cfg']))
        log_file = self.config['Github']['log_file']
        logging.config.fileConfig(config_file,
                                  defaults={'GithubCollector': log_file}
                                 )
        self.logger = logging.getLogger('GithubCollector')

    @abstractmethod
    def __repr__(self):
        """Implements a representation of the GithubObject."""
        pass

    @abstractmethod
    def __eq__(self, other):
        """Implements equality test between GithubObjects"""
        pass

    @abstractmethod
    def __ne__(self, other):
        """Implements inequality test between GithubObjects"""
        pass

    @abstractmethod
    def update(self):
        """Updates the Issue object with data by querying the remote endpoint."""
        pass

    def _errors_exist(self, doc_type, login, response_payload):
        """Internal function that checks for errors in the response payload of
        a query.

        Arguments:
            doc_type (str) - the type of data being queried (i.e. GithubUser)
            login (str) - the github login queried against when the error occurred
            response_payload (str) - the json string returned from a query

        Returns:
            True if there were errors in the response
            False if no errors were present int he response
        """
        if "errors" in response_payload:
            for index, error in enumerate(response_payload["errors"]):
                message = ':'.join([doc_type, login, str(error)])
                self.logger.error(message)
            return True
        return False
