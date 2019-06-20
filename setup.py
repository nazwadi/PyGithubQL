#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools
import textwrap

version = "0.1"


if __name__ == "__main__":
    setuptools.setup(
        name="githubv4",
        version=version,
        description="Implements the Github GraphQL APIv4",
        url="",
        packages=[
            "githubv4",
        ],
        classifiers=[
            "Development Status :: 0 - ",
        ],
        use_2to3=False,
        python_requires=">=3.7",
        install_requires=[
            "configparser>=3.5.0",
            "elasticsearch>=6.3.1",
            "requests>=2.14.0",
        ],
    )
