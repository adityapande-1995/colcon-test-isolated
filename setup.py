# Copyright 2016-2018 Dirk Thomas
# Licensed under the Apache License, Version 2.0

from setuptools import setup, Extension

setup(
    ext_modules=[
        Extension(
            name="isolate",  # as it would be imported
                               # may include packages/namespaces separated by `.`

            sources=["colcon_test_isolated/isolate.cc"], # all sources are compiled into a single binary file
        ),
    ]
)
