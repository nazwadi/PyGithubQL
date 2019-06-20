#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
collect_github_data.py

Collects data about a given list of Github users.

Save location is configured in the collectors.cfg file in the githubv4/ folder.
    Save options are: elasticsearch, filesystem, both.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
os.chdir("../")
from github import GithubCollector
from Repositories import Repositories # need to wrap this back under the github namespace

GC = GithubCollector()

logins = []
# The login list is a text file with a login username per line
with open('/path/to/github_user_list', 'r') as login_list:
    for login in login_list:
        logins.append(login.replace('\n', '').strip())

for index, login in enumerate(logins):
    path = ''.join(["/path/to/output_directory/", login])
    GC.save_user(login, path)
    GC.save_commit_comments(login, path) 
    GC.save_followers(login, path)
    GC.save_following(login, path)
    GC.save_gist_comments(login, path)
    GC.save_gists(login, path)
    GC.save_issue_comments(login, path)
    GC.save_issues(login, path)
    GC.save_organizations(login, path)
    GC.save_pinned_repositories(login, path)
    try:
        GC.save_repositories(login, path)
    except TypeError: # generated when 'NoneType' object is not subscriptable
        pass
    try:
        for resultset in Repositories(login): # Repositories returns a max of 100 results at a time
            for _, repo in enumerate(resultset.nodes):
                GC.save_repository(login, repo['name'], path)
    except TypeError as e: # generated when 'NoneType' object is not subscriptable
        print(e)
    GC.save_public_keys(login, path)
    GC.save_pull_requests(login, path)
    GC.save_starred_repositories(login, path)
    GC.save_repositories_contributed_to(login, path)
    GC.save_watching(login, path)
