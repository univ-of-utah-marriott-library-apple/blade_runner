#!/usr/bin/python

# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2019 University of Utah Student Computing Labs.
# All Rights Reserved.
#
# Author: Thackery Archuletta
# Creation Date: Oct 2018
# Last Updated: Feb 2019
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

    def _values_to_bools(self, dictionary):
        """Converts values, one level deep in a dictionary, that are string booleans to booleans, e.g.,

            "False" -> False
                or
            "false" -> False

        Args:
            dictionary (dict): Dictionary with values of string booleans.

        Returns:
            Copy of the dictionary with boolean values instead of string boolean values.
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
        # Return the copy of the dictionary.
        return dct

    def _remove_keys_with_value(self, value, dictionary):
        """Remove keys that contain a certain value. Only removes up to one level deep.

        Args:
            value: Value that indicates key removal.
            dictionary (dict): Dictionary to searched.

        Returns:
            Copy of original dictionary.
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
        # Return a copy of the dictionary.
        return dct

    def _invert_bool_values(self, dictionary):
        """
        Inverts boolean values one level deep in a dictionary, e.g.,

            False -> True
                or
            True -> False

        :param dictionary: Dictionary.
        :return: Copy of dictionary.
        """
        dct = dict(dictionary)
        for key in dictionary:
            if dct[key] is True:
                dct[key] = False
            elif dct[key] is False:
                dct[key] = True
        return dct


class SearchParams(Params):
    def __init__(self, params_dict):
        params_dict = self._values_to_bools(params_dict)

        self.originals = params_dict
        self.enabled = set(self._remove_keys_with_value(False, params_dict))
        self.disabled = set(self._remove_keys_with_value(True, params_dict))
        self.search_status = self._invert_bool_values(self._remove_keys_with_value(False, params_dict))
        self.matches = self._invert_bool_values(self._remove_keys_with_value(False, params_dict))
        self.search_count = 0

    def was_searched(self, param):
        if param in self.search_status:
            return self.search_status[param]

    def set_searched(self, param):
        if param in self.search_status:
            self.search_status[param] = True
            self.search_count += 1

    def set_match(self, param):
        if param in self.matches:
            self.matches[param] = True

    def get_matches(self):
        return self.matches

    def exists_match(self):
        return any(self.matches.values())

    def all_searched(self):
        return all(self.search_status.values())

    def __iter__(self):
        for param in self.enabled:
            yield param


class VerifyParams(Params):
    def __init__(self, params_dict):
        params_dict = self._values_to_bools(params_dict)

        self.originals = params_dict
        self.enabled = set(self._remove_keys_with_value(False, params_dict))
        self.disabled = set(self._remove_keys_with_value(True, params_dict))
        self.search_status = self._invert_bool_values(self._remove_keys_with_value(False, params_dict))