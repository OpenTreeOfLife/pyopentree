# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

from pyopentree import *

def inspect_opentreelib_output(opentreelib_output):
    import types
    import sys

    def local_recurse_inspect_opentreelib_output(whole, level=0):
        # ToDo: Make useful or kill!
        for part in whole:
            if (sys.hexversion < 0x03000000 and isinstance(part, types.StringTypes)) or (isinstance(part, str)):
                if not isinstance(whole, list):
                    print(' ' * 2 * level + part)
            if isinstance(whole, dict) and (isinstance(whole[part], dict) or isinstance(whole[part], list)):
                local_recurse_inspect_opentreelib_output(whole=whole[part], level=level+1)
            elif isinstance(whole, list) and (isinstance(part, dict) or isinstance(part, list)):
                local_recurse_inspect_opentreelib_output(whole=part, level=level+1)
            else:
                continue

    local_recurse_inspect_opentreelib_output(whole=opentreelib_output)

def get_ott_ids(names, context_name, do_approximate_matching=False):

    data = tnrs_match_names(
        names=names,
        context_name=context_name,
        do_approximate_matching=do_approximate_matching,
        ids=None,
        include_deprecated=False,
        include_dubious=False)

    ott_ids = list()

    for x in data['results']:
        ott_id = x['matches'][0]['ot:ottId']
        ott_ids.append(ott_id)

    return_value = ott_ids

    return return_value

def get_induced_tree(names, context_name, do_approximate_matching=False):

    ott_ids = get_ott_ids(
        names=names,
        context_name=context_name,
        do_approximate_matching=do_approximate_matching)

    data = tol_induced_tree(
            ott_ids=ott_ids,
            node_ids=None)

    induced_tree = data['subtree']

    return induced_tree

if __name__ == "__main__":

    induced_tree = get_induced_tree(
        names=['dog', 'cat', 'canada goose', 'african elephant', 'monarch butterfly'],
        context_name=None,
        do_approximate_matching=False)

    print(induced_tree)

    opentreelib_output = tnrs_match_names(
        names=['dog', 'canada goose'],
        context_name=None,
        do_approximate_matching=False,
        ids=None,
        include_deprecated=False,
        include_dubious=False)

    inspect_opentreelib_output(opentreelib_output)
