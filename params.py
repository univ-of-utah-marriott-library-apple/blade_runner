class Params(object):

    def _values_to_bools(self, dictionary):
        """
        Converts values, one level deep in a dictionary, that are string booleans to booleans, e.g.,

            "False" -> False
                or
            "false" -> False

        :param dictionary: Dictionary.
        :return: Copy of dictionary.
        """
        dct = dict(dictionary)
        for key in dictionary:
            if isinstance(dct[key], str):
                if dct[key].lower() == "false":
                    dct[key] = False
                elif dct[key].lower() == "true":
                    dct[key] = True
        return dct

    def _remove_keys_with_value(self, value, dictionary):
        """
        Removes keys from a dictionary according to a given value that is one level deep.

        :param value: The value that indicates key removal.
        :param params: Dictionary.
        :return: Copy of the dictionary.
        """
        dct = dict(dictionary)
        for key in dictionary:
            if dct[key] == value:
                dct.pop(key, None)
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