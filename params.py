
# TODO There is a potential bug when using search_status. See below.
'''
The key "computer_name" in the verify config is not a valid search item, but it gets stored in the search_status
dictionary. This could be misleading in future implementations of search_status. Haven't devised a fix yet, as I want
all enabled parameters in the same config. Right now the main controller removes the computer_name key before storing
it in the search_status list.
'''


class Params(object):
    def __init__(self, params_dict):
        params_dict = self._values_to_bools(params_dict)

        self.all = params_dict
        self.enabled = set(self._remove_keys_with_value(False, params_dict))
        self.disabled = set(self._remove_keys_with_value(True, params_dict))
        self.search_status = self._invert_bool_values(self._remove_keys_with_value(False, params_dict))

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

