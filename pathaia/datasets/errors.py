# coding: utf8
"""
A module to handle datasets errors.

Enable catching of level and filter accesses.
"""


class Error(Exception):
    """
    Base of custom errors.

    **********************
    """

    pass


class UnknownSplitModeError(Error):
    """
    Raise when trying to split a dataset with an unknown option.

    *********************************************************
    """

    pass


class InvalidDatasetError(Error):
    """
    Raise when trying to perform operation on a dataset with bad properties.

    ************************************************************************
    """

    pass
