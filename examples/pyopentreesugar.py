# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import dendropy
import pyopentree

# NEXSS sugar ------------------------------------------------------------------

class NEXSS(object):

    def __init__(self):
        self.datatype_hint = 'xsd:string'
        self.name_prefix = 'nexss'
        self.namespace = 'http://phylotastic.org/nexss#'
        self.styles = list()

    def style_id_index(self, style_id):
        for i, style in enumerate(self.styles):
            if style[0] == style_id:
                return i
                break
        return -1

    def write_to_path(self, path):
        with open(path, 'w') as nexss_file:
            for style in self.styles:
                nexss_file.write(style[1] + '\n\n')

    def annotate_node(self, node, tag, content, style):

        node.annotations.drop(name=tag)

        node.annotations.add_new(
            name=tag,
            value=content,
            datatype_hint=self.datatype_hint,
            name_prefix=self.name_prefix,
            namespace=self.namespace,
            name_is_prefixed=False,
            is_attribute=False,
            annotate_as_reference=False,
            is_hidden=False)

        style_id = 'node[' + self.name_prefix + ':' + tag + '=' + content + ']'

        sid_idx = self.style_id_index(style_id)
        if sid_idx >= 0:
            self.styles.pop(sid_idx)

        style_str_left = style_id + ' {\n'
        style_str_right = '}'
        style_str = style_str_left

        for k in style:
            style_str = style_str + '\t' + k + ': ' + style[k] + ';\n'

        style_str = style_str + style_str_right

        self.styles.append([style_id, style_str])

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

def write_tree_to_path(tree, path, schema='nexml'):
    tree.write_to_path(dest=path, schema=schema)

def get_internal_nodes(tree, only_named_nodes=False, exclude_seed_node=False):
    node_iterator = tree.preorder_internal_node_iter(
        filter_fn=None, exclude_seed_node=exclude_seed_node)
    nodes = list()
    for node in node_iterator:
        if (not only_named_nodes) or (only_named_nodes and node.taxon is not None):
            nodes.append(node)
    return nodes

def get_leaf_nodes(tree):
    node_iterator = tree.leaf_node_iter(
        filter_fn=None)
    nodes = list()
    for node in node_iterator:
        nodes.append(node)
    return nodes

def normalize_branch_lengths(tree, branch_length=1.0):
    node_iterator = tree.preorder_node_iter(
        filter_fn=None)
    for node in node_iterator:
        node.edge.length = branch_length
    return tree

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
        suppress_internal_node_taxa=False,
        terminating_semicolon_required=False)

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
        suppress_internal_node_taxa=False,
        terminating_semicolon_required=False)

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
        suppress_internal_node_taxa=False,
        terminating_semicolon_required=False)

    subtree = parse_opentree_taxon_labels_in_dendropy_tree(
        tree=subtree,
        keep_taxon_name=keep_taxon_name,
        keep_ott_id=keep_ott_id)

    return subtree

def tol_mrca(ott_ids):
    raw_api_data = pyopentree.tol_mrca(ott_ids=ott_ids.values(), node_ids=None)

    return {raw_api_data['mrca_name']: raw_api_data['ott_id']}

if __name__ == "__main__":

    # ott_ids = get_ott_ids(
    #     names=['dog', 'cat', 'canada goose', 'african elephant', 'monarch butterfly', 'Solanum chilense', 'Prunus dulcis'],
    #     context_name=None,
    #     do_approximate_matching=False,
    #     include_deprecated=False,
    #     include_dubious=False)
    # print(ott_ids)

    # ott_ids_collapsed = collapse_tnrs_match_names_results(
    #     results=ott_ids,
    #     method='first_hit_only')
    # print(ott_ids)

    # induced_tree = get_tol_induced_tree(
    #     ott_ids=ott_ids,
    #     keep_taxon_name=True,
    #     keep_ott_id=False)
    # print(induced_tree)

    # internal_nodes = get_internal_nodes(
    #     tree=induced_tree, only_named_nodes=True, exclude_seed_node=False)
    # for internal_node in internal_nodes:
    #     print(internal_node)
    # print()

    # leaf_nodes = get_leaf_nodes(
    #     tree=induced_tree)
    # for leaf_node in leaf_nodes:
    #     print(leaf_node)
    # print()

    # colors = ['red', 'green', 'blue', 'orange', 'pink']
    # nexss = NEXSS()
    # internal_node_count = len(internal_nodes)
    # j = 0
    # for i, node in enumerate(internal_nodes):
    #     if i % len(colors) == 0:
    #         j = 0
    #     else:
    #         j = j + 1
    #     style = {'color': colors[j]}
    #     nexss.annotate_node(
    #         node=node,
    #         tag='clade',
    #         content=node.taxon.label,
    #         style=style)

    # nexss.write_to_path('/Users/karolis/Desktop/induced_tree.nexss')

    # induced_tree = normalize_branch_lengths(
    #     tree=induced_tree,
    #     branch_length=1.0)

    # write_tree_to_path(
    #     tree=induced_tree,
    #     path='/Users/karolis/Desktop/induced_tree.nexml',
    #     schema='nexml')

    # Clade
    clade = 'Hominoidea'
    ott_ids = get_ott_ids(
        names=[clade],
        context_name=None,
        do_approximate_matching=False,
        include_deprecated=False,
        include_dubious=False)
    print(ott_ids)

    # ott_ids = get_ott_ids(
    #     names=['Geospiza', 'Iridophanes'],
    #     context_name=None,
    #     do_approximate_matching=False,
    #     include_deprecated=False,
    #     include_dubious=False)
    # print(ott_ids)

    # ott_ids_collapsed = collapse_tnrs_match_names_results(
    #     results=ott_ids,
    #     method='first_hit_only')
    # print(ott_ids)

    # mrca = tol_mrca(ott_ids)

    # clade = mrca.keys()[0]

    # ott_ids = get_ott_ids(
    #     names=[clade],
    #     context_name=None,
    #     do_approximate_matching=False,
    #     include_deprecated=False,
    #     include_dubious=False)
    # print(ott_ids)

    tol_subtree = get_tol_subtree(
        ott_id=ott_ids[clade][0],
        keep_taxon_name=True,
        keep_ott_id=False)
    # print(tol_subtree)

    internal_nodes = get_internal_nodes(
        tree=tol_subtree, only_named_nodes=True, exclude_seed_node=False)
    # for internal_node in internal_nodes:
    #     print(internal_node)
    # print()

    leaf_nodes = get_leaf_nodes(
        tree=tol_subtree)
    # for leaf_node in leaf_nodes:
    #     print(leaf_node)
    # print()

    colors = ['red', 'green', 'blue', 'orange']
    nexss = NEXSS()
    internal_node_count = len(internal_nodes)
    j = 0
    for i, node in enumerate(internal_nodes):
        if i % len(colors) == 0:
            j = 0
        else:
            j = j + 1
        style = {'color': colors[j]}
        nexss.annotate_node(
            node=node,
            tag='clade',
            content=node.taxon.label,
            style=style)

    tol_subtree.ladderize(ascending=True)

    nexss.write_to_path('/Users/karolis/Desktop/' + clade + '.nexss')

    tol_subtree = normalize_branch_lengths(
        tree=tol_subtree,
        branch_length=1.0)

    write_tree_to_path(
        tree=tol_subtree,
        path='/Users/karolis/Desktop/' + clade + '.nexml',
        schema='nexml')

    write_tree_to_path(
        tree=tol_subtree,
        path='/Users/karolis/Desktop/' + clade + '.newick',
        schema='newick')

    import subprocess
    # command = 'pstastic.py ~/Desktop/' + clade + '.nexml ~/Desktop/' + clade + '.nexss --output ~/Desktop/' + clade + '.pdf -ow 3000 -oh 8000 --dpi 300'
    command = 'pstastic.py ~/Desktop/' + clade + '.nexml ~/Desktop/' + clade + '.nexss --output ~/Desktop/' + clade + '.pdf'
    subprocess.call(
        command,
        # stdout=subprocess.PIPE,
        # stderr=subprocess.PIPE,
        shell=True)

    subprocess.call(
        'open ~/Desktop/' + clade + '.pdf',
        # stdout=subprocess.PIPE,
        # stderr=subprocess.PIPE,
        shell=True)


    taxonomy_subtree = get_taxonomy_subtree(
        ott_id='541933',
        keep_taxon_name=True,
        keep_ott_id=False)
    print(taxonomy_subtree)
