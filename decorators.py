#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

def connection(func):
    """Currently used as more of a fancy label to indicate functions
    representing Connections.  Additional functionality may be added later.

    Connection functions all query the remote endpoint when called, and as such
    they represent additional network latency. The goal is to eventually find a way
    to update the GithubObject once by initiating it with a hint at the connections
    that are desired during initialization.

    For upstream documentation, see
    https://developer.github.com/v4/guides/intro-to-graphql/#connection
    """
    def wrapper(self, **kwargs):
        return func(self, **kwargs)
    return wrapper
