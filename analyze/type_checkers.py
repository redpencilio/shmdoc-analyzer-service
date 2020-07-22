import datefinder
from urllib.parse import urlparse

def is_any(el):
    # Always prevent is_any getting selected
    return False

def is_int(el):
    return isinstance(el, int)


def is_bool(el):
    return isinstance(el, bool) or (is_int(el) and (el == 0 or el == 1))


def is_float(el):
    return isinstance(el, float)


def is_str(el):
    return isinstance(el, str)


def is_datetime(string):
    # Check whether there's any date / datetime somewhere in the string
    matches = datefinder.find_dates(string)
    try:
        for match in matches:
            # I didn't find a way to check len(matches) or matches.empty, so this iteration solves it
            return True
    except TypeError:
        pass  # No idea why a TypeError is raised sometimes, but this solves the problem temporarily :-)
    return False


def is_uri(string):
    # Check wheter there's a uri in this string
    # NOTE: this function will only check for absolute URI's, relative URI's are not accepted.
    # Even though the xsd:type used is anyURI (which also encompasses relative URI's)
    # source https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc, result.path])
    except:
        return False
