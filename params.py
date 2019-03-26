#!/usr/bin/python

# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2019 University of Utah Student Computing Labs.
# All Rights Reserved.
#
# Author: Thackery Archuletta
# Creation Date: Oct 2018
# Last Updated: March 2019
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appears in all copies and
# that both that copyright notice and this permission notice appear
# in supporting documentation, and that the name of The University
# of Utah not be used in advertising or publicity pertaining to
# distribution of the software without specific, written prior
# permission. This software is supplied as is without expressed or
# implied warranties of any kind.
################################################################################


class Params(object):
    """Contains methods for pruning keys and changing values of a boolean based dictionary"""

    @staticmethod
    def _values_to_bools(dictionary):
        """Converts values, one level deep in a dictionary, that are string booleans to booleans, e.g.,

            "False" -> False
                or
            "false" -> False

        Args:
            dictionary (dict): Dictionary with values of string booleans.

        Returns:
            Altered copy of the dictionary with boolean values instead of string boolean values.
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>x
        # Deep copy of dictionary.
        dct = dict(dictionary)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # For every key, convert the string boolean into a boolean.
        for key in dictionary:
            if isinstance(dct[key], str):
                if dct[key].lower() == "false":
                    dct[key] = False
                elif dct[key].lower() == "true":
                    dct[key] = True
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Return the altered copy.
        return dct

    @staticmethod
    def _remove_keys_with_value(value, dictionary):
        """Remove keys that contain a certain value. Only removes up to one level deep.

        Args:
            value: Value that indicates key removal.
            dictionary (dict): Dictionary to searched.

        Returns:
            Altered copy of original dictionary.
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Deep copy dictionary.
        dct = dict(dictionary)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # For every key, check its value, and remove the key if the value matches the removal value.
        for key in dictionary:
            if dct[key] == value:
                dct.pop(key, None)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Return the altered copy.
        return dct

    @staticmethod
    def _invert_bool_values(dictionary):
        """Inverts boolean values one level deep in a dictionary, e.g.,

            False -> True
                or
            True -> False

        Args:
            dictionary (dict): Dictionary of boolean values.

        Returns:
            Altered copy of original dictionary.
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Deep copy dictionary.
        dct = dict(dictionary)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Invert all the boolean values.
        for key in dictionary:
            if dct[key] is True:
                dct[key] = False
            elif dct[key] is False:
                dct[key] = True
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Return the altered copy.
        return dct


class SearchParams(Params):
    """Manipulates a dictionary containing boolean values. This dictionary indicates whether or not a certain
    key has been searched in the JSS and which keys are to be used in the search.
    """

    def __init__(self, params_dict):
        """Process the dictionary.

        Args:
            params_dict (dict): Dictionary that indicates which keys are to be used in the search. Values are booleans.
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Deep copy dictionary.
        params_dict = self._values_to_bools(params_dict)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Store the originals.
        self.originals = params_dict
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Make a set of the enabled search params.
        self.enabled = set(self._remove_keys_with_value(False, params_dict))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Make a set of the disabled params.
        self.disabled = set(self._remove_keys_with_value(True, params_dict))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set the search status of the enabled search params.
        self.search_status = self._invert_bool_values(self._remove_keys_with_value(False, params_dict))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set the matched status of the enabled search params.
        self.match_status = self._invert_bool_values(self._remove_keys_with_value(False, params_dict))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set the search count.
        self.search_count = 0

    def was_searched(self, param):
        """Returns if the param has already been searched.

        Args:
            param (str): Search parameter key.

        Returns:
            True if parameter was searched, False otherwise.
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Check if key exists in dict. Return its searched status.
        if param in self.search_status:
            return self.search_status[param]

    def set_searched(self, param):
        """Set the searched status of search parameter.

        Args:
            param (str): Search parameter key.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set params searched status to True.
        if param in self.search_status:
            self.search_status[param] = True
            self.search_count += 1

    def set_match(self, param):
        """Set matched status of a search parameter.

        Args:
            param (str): Search parameter key.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set params matched status to True.
        if param in self.match_status:
            self.match_status[param] = True

    def exists_match(self):
        """Return whether or not a match has been found for any of the search parameters.

        Returns:
            True if match exists, False otherwise.
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        return any(self.match_status.values())

    def all_searched(self):
        """Returns status on whether or not all the search parameters have been searched.

        Returns:
            True if all search parameters have been searched, False otherwise.
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        return all(self.search_status.values())

    def __iter__(self):
        """Defines an iterator. Iterator is a list of the enabled search parameters.

        Returns:
            Enabled search parameters.
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        for param in self.enabled:
            yield param


class VerifyParams(Params):
    """Converts a dictionary of enabled verification parameters into other data structures and representations, such as
    which parameters are enabled, disabled, and which ones have been searched for in the JSS.
    """

    def __init__(self, params_dict):
        """Convert the enabled verification parameters dictionary into enabled, disabled, and searched verification
        params.

        Args:
            params_dict (dict): Enabled verification parameters denoted by boolean values.
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Deep copy of params_dict
        params_dict = self._values_to_bools(params_dict)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Store the originals.
        self.originals = params_dict
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create a set of the enabled parameters.
        self.enabled = set(self._remove_keys_with_value(False, params_dict))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create a set of the disabled parameters.
        self.disabled = set(self._remove_keys_with_value(True, params_dict))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create a dictionary of the searched status of the parameters.
        self.search_status = self._invert_bool_values(self._remove_keys_with_value(False, params_dict))