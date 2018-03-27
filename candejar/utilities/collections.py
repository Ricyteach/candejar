# -*- coding: utf-8 -*-

"""Tools for combining multiple sequences together."""

import collections

class MyCounter(collections.Counter):
    """A special `collections.Counter` that can be incremented."""
    def incremented(self, key):
        """The post-incremented count of `key`."""
        self[key] += 1
        return self[key]
