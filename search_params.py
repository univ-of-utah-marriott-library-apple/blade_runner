
class SearchParams(object):
    def __init__(self, params):
        self.all = self.string_to_bool(params)
        self.enabled = self.remove_false_keys(self.all)
        self.needs_search = self.remove_false_keys(self.all)

    def _string_to_bool(self, verify_data):
        for field in verify_data:
            if verify_data[field].lower() == "false":
                verify_data[field] = False
            elif verify_data[field].lower() == "true":
                verify_data[field] = True
        return verify_data

    def _remove_false_keys(self, params):
        for param in params:
            if params[param] is False:
                params.pop(param, None)
        return params