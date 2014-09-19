# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import dendropy
import pyopentree

# Utility functions ------------------------------------------------------------

def parse_opentree_taxon_label(taxon_label):

    taxon_label_split = taxon_label.split('_')

    taxon_name_parts = taxon_label_split[0:-1]
    ott_id = taxon_label_split[-1].strip('ott')

    return {'taxon_name_parts': taxon_name_parts, 'ott_id': ott_id}

def parse_opentree_taxon_labels_in_dendropy_tree(tree, keep_taxon_name=True, keep_ott_id=True):

    node_iterator = tree.preorder_node_iter(filter_fn=None)

    for node in node_iterator:
        if node.taxon is not None:
            parsed_label = parse_opentree_taxon_label(taxon_label=node.taxon.label)

            new_label = ''
            if keep_taxon_name:
                new_label = '_'.join(parsed_label['taxon_name_parts'])
            if keep_ott_id:
                if keep_taxon_name:
                    new_label = new_label + '_'
                new_label = new_label + 'ott' + parsed_label['ott_id']

            node.taxon.label = new_label

    return tree

def collapse_tnrs_match_names_results(results, method='first_hit_only'):

    if method == 'first_hit_only':
        for key in results:
            results[key] = results[key][0]
    else:
        raise NotImplementedError()

    return results

# Abstract pyopentree wrappers -------------------------------------------------

def extract_property_from_tnrs_match_names(
    names,
    prop,
    context_name=None,
    do_approximate_matching=False,
    include_deprecated=False,
    include_dubious=False):

    raw_api_data = pyopentree.tnrs_match_names(
        names=names,
        context_name=context_name,
        do_approximate_matching=do_approximate_matching,
        ids=None,
        include_deprecated=False,
        include_dubious=False)

    extracted_results = dict()
    for result in raw_api_data['results']:
        user_specified_name = result['id']
        opentree_matches = result['matches']
        opentree_matches_extracted = list()
        for match in opentree_matches:
            opentree_matched_property = match[prop]
            opentree_matches_extracted.append(opentree_matched_property)
        extracted_results[user_specified_name] = opentree_matches_extracted

    return extracted_results

# Specific pyopentree wrappers -------------------------------------------------

def get_ott_ids(
    names,
    context_name=None,
    do_approximate_matching=False,
    include_deprecated=False,
    include_dubious=False):

    ott_ids = extract_property_from_tnrs_match_names(
        names=names,
        prop='ot:ottId',
        context_name=context_name,
        do_approximate_matching=do_approximate_matching,
        include_deprecated=include_deprecated,
        include_dubious=include_dubious)

    return ott_ids

def get_tol_induced_tree(ott_ids, keep_taxon_name=True, keep_ott_id=True):

    raw_api_data = pyopentree.tol_induced_tree(
            ott_ids=ott_ids.values(),
            node_ids=None)

    induced_tree = dendropy.Tree.get_from_string(
        src=raw_api_data['subtree'],
        schema='newick',
        preserve_underscores=True,
        suppress_internal_node_taxa=False)

    induced_tree = parse_opentree_taxon_labels_in_dendropy_tree(
        tree=induced_tree,
        keep_taxon_name=keep_taxon_name,
        keep_ott_id=keep_ott_id)

    return induced_tree

def get_tol_subtree(ott_id, keep_taxon_name=True, keep_ott_id=True):

    raw_api_data = pyopentree.tol_subtree(ott_id=ott_id, node_id=None, tree_id=None)

    subtree = dendropy.Tree.get_from_string(
        src=raw_api_data['newick'],
        schema='newick',
        preserve_underscores=True,
        suppress_internal_node_taxa=False)

    subtree = parse_opentree_taxon_labels_in_dendropy_tree(
        tree=subtree,
        keep_taxon_name=keep_taxon_name,
        keep_ott_id=keep_ott_id)

    return subtree

def get_taxonomy_subtree(ott_id, keep_taxon_name=True, keep_ott_id=True):

    raw_api_data = pyopentree.taxonomy_subtree(ott_id=ott_id)

    subtree = dendropy.Tree.get_from_string(
        src=raw_api_data['subtree'],
        schema='newick',
        preserve_underscores=True,
        suppress_internal_node_taxa=False)

    subtree = parse_opentree_taxon_labels_in_dendropy_tree(
        tree=subtree,
        keep_taxon_name=keep_taxon_name,
        keep_ott_id=keep_ott_id)

    return subtree

if __name__ == "__main__":

    ott_ids = get_ott_ids(
        names=['dog', 'cat', 'canada goose', 'african elephant', 'monarch butterfly', 'Solanum chilense', 'Prunus dulcis'],
        context_name=None,
        do_approximate_matching=False,
        include_deprecated=False,
        include_dubious=False)
    print(ott_ids)


    ott_ids_collapsed = collapse_tnrs_match_names_results(
        results=ott_ids,
        method='first_hit_only')
    print(ott_ids)


    induced_tree = get_tol_induced_tree(
        ott_ids=ott_ids,
        keep_taxon_name=True,
        keep_ott_id=False)
    print(induced_tree)


    tol_subtree = get_tol_subtree(
        ott_id='541933',
        keep_taxon_name=True,
        keep_ott_id=False)
    print(tol_subtree)


    # taxonomy_subtree = get_taxonomy_subtree(
    #     ott_id='541933',
    #     keep_taxon_name=True,
    #     keep_ott_id=False)
    # print(taxonomy_subtree)
