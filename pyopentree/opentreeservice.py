# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import locale
import json
import sys

if sys.hexversion < 0x03000000:
    from urllib2 import Request
    from urllib2 import urlopen
    from urllib import urlencode
    from urllib2 import HTTPError
else:
    from urllib.request import Request
    from urllib.request import urlopen
    from urllib.parse import urlencode
    from urllib.error import HTTPError

class OpenTreeService(object):

    ENCODING = locale.getdefaultlocale()[1]
    TREE_SCHEMA_EXTENSION_MAP = {
            "nexus"  : ".nex",
            "newick" : ".tre",
            "nexml"  : ".nexml",
            "nexson" : ".nexson",
            "json"   : ".json",
            }

    class OpenTreeError(Exception):
        pass

    def __init__(self, base_url=None):
        if base_url is None:
            self.base_url = 'http://devapi.opentreeoflife.org/v2'
        else:
            self.base_url = base_url
        self.is_testing_mode = False

    def otl_format_specifier_extension(self, schema):
        schema = schema.lower()
        return OpenTreeService.TREE_SCHEMA_EXTENSION_MAP[schema]

    def open_url(self, request):
        """
        Override this to provide custom added functionality, to, e.g. cache the
        requests. Signature and return is the same as Python's standard
        library's `urlopen`.
        """
        return urlopen(request)

    def request(self,
            sub_url,
            payload=None,
            headers=None,
            protocol="POST",
            process_response_as="json",
            ):
        if headers is None:
            headers = {'content-type': 'application/json'}
        url = self.base_url + sub_url
        if protocol == "POST":
            if payload is None:
                payload = {}
            data = json.dumps(payload).encode("utf-8")
        else:
            data = None
        request = Request(
                url=url,
                data=data,
                headers=headers)
        response = self.open_url(request)
        response_contents = response.read().decode(OpenTreeService.ENCODING)
        if process_response_as == "json":
            response_contents = json.loads(response_contents)
            if 'error' in response_contents and not self.is_testing_mode:
                raise OpenTreeService.OpenTreeError(response_contents['error'])
        elif process_response_as == "text":
            pass
        else:
            raise ValueError("Response type '{}' is not supported".format(process_response_as))
        return response_contents

    def tol_about(self, study_list=True):
        """
        Return information about the current draft tree itself.

        Returns summary information about the current draft tree of life, including
        information about the list of source trees and the taxonomy used to build
        it.

        Wraps::

            curl -X POST http://devapi.opentreeoflife.org/v2/tree_of_life/about -H "content-type:application/json"  -d '{"study_list":true}'

        Parameters
        ----------
        study_list : bool
            Return a list of source studies.

        Returns
        -------
        d : dict
            A python dictionary with the following fields:

                "root_node_id"
                "study_list"
                "root_taxon_name"
                "num_source_studies"
                "taxonomy_version"
                "root_ott_id"
                "num_tips"
                "date"
                "tree_id"
        """
        payload = {'study_list': study_list}
        return self.request(
                '/tree_of_life/about',
                payload)

    def tol_mrca(
            self,
            ott_ids=None,
            node_ids=None):
        """
        Return the most recent common ancestor of a set of nodes in the draft tree.

        Get the MRCA of a set of nodes on the current draft tree. Accepts any
        combination of node ids and ott ids as input. Returns information about the
        most recent common ancestor (MRCA) node as well as the most recent
        taxonomic ancestor (MRTA) node (the closest taxonomic node to the MRCA node
        in the synthetic tree; the MRCA and MRTA may be the same node).
        Node ids that are not in the synthetic tree are dropped from the MRCA
        calculation. For a valid ott id that is not in the synthetic tree (i.e. it
        is not recovered as monophyletic from the source tree information),
        the taxonomic descendants of the node are used in the MRCA calculation.
        Returns any unmatched node ids / ott ids.

        Wraps::

            curl -X POST http://devapi.opentreeoflife.org/v2/tree_of_life/mrca -H "content-type:application/json" -d '{"ott_ids":[412129, 536234]}'

        Parameters
        ----------
        ott_ids : iterable of integers
            An iterable of ott ids. If `ott_ids` is not specified, then `node_ids`
            must specified, and vice versa. A combination of `ott_ids` and
            `node_ids` may also be specified.
        node_ids : iterable of integers
            An iterable of node ids. If `node_ids` is not specified, then `ott_ids`
            must specified, and vice versa. A combination of `ott_ids` and
            `node_ids` may also be specified.

        Returns
        -------
        d : dict
            A python dictionary with the following fields:

                "mrca_name"
                "nearest_taxon_mrca_rank"
                "mrca_rank"
                "nearest_taxon_mrca_ott_id"
                "invalid_node_ids"
                "nearest_taxon_mrca_node_id"
                "ott_ids_not_in_tree"
                "nearest_taxon_mrca_unique_name"
                "ott_id"
                "mrca_node_id"
                "mrca_unique_name"
                "nearest_taxon_mrca_name"
                "node_ids_not_in_tree"
                "invalid_ott_ids"
        """
        if ott_ids is None and node_ids is None:
            raise ValueError('Must specify ott_ids or node_ids or both.')
        if ott_ids is not None and len(ott_ids) == 0:
            raise ValueError('ott_ids cannot be an empty list.')
        if node_ids is not None and len(node_ids) == 0:
            raise ValueError('node_ids cannot be an empty list.')
        payload = {'node_ids': node_ids, 'ott_ids': ott_ids}
        return self.request(
                '/tree_of_life/mrca',
                payload)

    def tol_subtree(
            self,
            ott_id=None,
            node_id=None,
            tree_id=None):
        """
        Return the complete subtree below a given node.

        Return a complete subtree of the draft tree descended from some specified
        node. The node to use as the start node may be specified using either a
        node id or an ott id, but not both. If the specified node is not in the
        synthetic tree (or is entirely absent from the graph), an error will be
        returned.

        Wraps::

            curl -X POST http://devapi.opentreeoflife.org/v2/tree_of_life/subtree -H "content-type:application/json" -d '{"ott_id":3599390}'

        Parameters
        ----------
        ott_id : integer
            An ott id. If `ott_id` is not specified, then `node_id` must specified,
            and vice versa. Both cannot be specified.
        node_id : integer
            A node id. If `node_id` is not specified, then `ott_id` must specified,
            and vice versa. Both cannot be specified.
        tree_id : string
            The identifier for the synthesis tree. We currently only support a
            single draft tree in the db at a time, so this argument is superfluous
            and may be safely ignored.

        Returns
        -------
        d : dict
            A python dictionary with the following fields:

                "newick"
                "tree_id"
        """
        if ott_id is None and node_id is None:
            raise ValueError('Must specify ott_id or node_id but not both.')
        if ott_id is not None and ott_id == '':
            raise ValueError('ott_id cannot be an empty string.')
        if node_id is not None and node_id == '':
            raise ValueError('node_id cannot be an empty string.')
        payload = {'ott_id': ott_id, 'node_id': node_id, 'tree_id': tree_id}
        result = self.request(
                '/tree_of_life/subtree',
                payload=payload)
        return result

    def tol_induced_tree(
            self,
            ott_ids=None,
            node_ids=None):
        """
        Return the induced subtree on the draft tree that relates a set of nodes.

        Return a tree with tips corresponding to the nodes identified in the input
        set(s), that is consistent with topology of the current draft tree. This
        tree is equivalent to the minimal subtree induced on the draft tree by the
        set of identified nodes. Any combination of node ids and ott ids may be used
        as input. Nodes or ott ids that do not correspond to any found nodes in the
        graph, or which are in the graph but are absent from the synthetic tree,
        will be identified in the output (but will of course not be present in the
        resulting induced tree). Branch lengths in the result may be arbitrary, and
        the leaf labels of the tree may either be taxonomic names or (for nodes not
        corresponding directly to named taxa) node ids.

        WARNING: there is currently a known bug if any of the input nodes is the
        parent of another, the returned tree may be incorrect. Please avoid this
        input case.

        Wraps::

            curl -X POST http://devapi.opentreeoflife.org/v2/tree_of_life/induced_subtree -H "content-type:application/json" -d '{"ott_ids":[292466, 501678, 267845, 666104, 316878, 102710, 176458]}'

        Parameters
        ----------
        ott_ids : iterable of integers
            An iterable of ott ids. If `ott_ids` is not specified, then `node_ids`
            must specified, and vice versa. A combination of `ott_ids` and
            `node_ids` may also be specified.
        node_ids : iterable of integers
            An iterable of node ids. If `node_ids` is not specified, then `ott_ids`
            must specified, and vice versa. A combination of `ott_ids` and
            `node_ids` may also be specified.

        Returns
        -------
        d : dict
            A python dictionary with the following fields:

                "subtree"
                "ott_ids_not_in_tree"
                "ott_ids_not_in_graph"
                "node_ids_not_in_graph"
                "node_ids_not_in_tree"
        """
        if ott_ids is None and node_ids is None:
            raise ValueError('Must specify ott_ids or node_ids or both.')
        if ott_ids is not None and len(ott_ids) == 0:
            raise ValueError('ott_ids cannot be an empty list.')
        if node_ids is not None and len(node_ids) == 0:
            raise ValueError('node_ids cannot be an empty list.')
        payload = {'node_ids': node_ids, 'ott_ids': ott_ids}
        result = self.request(
                '/tree_of_life/induced_subtree',
                payload=payload)
        return result

    def gol_about(self):
        """
        Get information about the graph of life itself.

        Returns summary information about the entire graph database, including
        identifiers for the taxonomy and source trees used to build it.

        Wraps::

            curl -X POST http://devapi.opentreeoflife.org/v2/graph/about

        Returns
        -------
        d : dict
            A python dictionary with the following fields:

                "graph_num_source_trees"
                "graph_taxonomy_version"
                "graph_num_tips"
                "graph_root_name"
                "graph_root_node_id"
                "graph_root_ott_id"
        """
        return self.request('/graph/about')

    def gol_source_tree(
            self,
            study_id,
            tree_id,
            git_sha,
            schema=None):
        """
        Return a source tree (including metadata) from the graph of life.

        Returns a source tree (corresponding to a tree in some study) as it exists
        within the graph. Although the result of this service is a tree
        corresponding directly to a tree in a study, the representation of the tree
        in the graph may differ slightly from its canonical representation in the
        study, due to changes made during tree import (for example, pruning tips
        from the tree that cannot be mapped to taxa in the graph). In addition, both
        internal and terminal nodes are labelled ott ids. The tree is returned in
        newick format.

        Wraps::

            curl -X POST http://devapi.opentreeoflife.org/v2/graph/source_tree -H "content-type:applicatin/json" -d '{"study_id":"pg_420", "tree_id":"522", "git_sha":"a2c48df995ddc9fd208986c3d4225112550c8452"}'

        Parameters
        ----------
        study_id : string
            The study identifier. Will typically include a prefix ("pg_" or "ot_").
        tree_id : string
            The tree identifier for a given study.
        git_sha : string
            The git SHA identifying a particular source version.
        schema : string
            The name of the return format. The only currently supported format is newick.

        Returns
        -------
        d : dict
            A python dictionary with the following fields:

                "newick"
        """
        payload = {
                'study_id': study_id,
                'tree_id': tree_id,
                'git_sha': git_sha,
                'format': schema, }
        result = self.request(
                '/graph/source_tree',
                payload=payload)
        return result

    def gol_node_info(
            self,
            ott_id=None,
            node_id=None,
            include_lineage=False):
        """
        Get information about a node in the graph of life.

        Returns summary information about a node in the graph. The node of interest
        may be specified using either a node id, or an ott id, but not both. If the
        specified node or ott id is not in the graph, an error will be returned.

        Wraps::

            curl -X POST http://devapi.opentreeoflife.org/v2/graph/node_info -H "content-type:application/json" -d '{"ott_id":810751}'

        Parameters
        ----------
        ott_id : integer
            An ott id. If `ott_id` is not specified, then `node_id` must specified,
            and vice versa. Both cannot be specified.
        node_id : integer
            A node id. If `node_id` is not specified, then `ott_id` must specified,
            and vice versa. Both cannot be specified.
        include_lineage : bool
            Include the ancestral lineage of the node in the draft tree. If this
            argument is `True`, then a list of all the ancestors of this node in the
            draft tree, down to the root of the tree itself, will be included in the
            results. Higher list indices correspond to more incluive (i.e. deeper)
            ancestors, with the immediate parent of the specified node occupying
            position 0 in the list.

        Returns
        -------
        d : dict
            A python dictionary with the following fields:

                "synth_sources"
                "in_synth_tree"
                "rank"
                "in_graph"
                "name"
                "num_tips"
                "ott_id"
                "num_synth_children"
                "tax_source"
                "tree_sources"
                "node_id"
        """
        if ott_id is None and node_id is None:
            raise ValueError('Must specify ott_id or node_id but not both.')
        if ott_id is not None and ott_id == '':
            raise ValueError('ott_id cannot be an empty string.')
        if node_id is not None and node_id == '':
            raise ValueError('node_id cannot be an empty string.')
        payload = {'ott_id': ott_id, 'node_id': node_id, 'include_lineage': include_lineage}
        result = self.request(
                '/graph/node_info',
                payload=payload)
        return result

    def tnrs_match_names(
            self,
            names,
            context_name=None,
            do_approximate_matching=True,
            ids=None,
            include_deprecated=False,
            include_dubious=False):
        """
        Returns a list of potential matches to known taxonomic names.

        Accepts one or more taxonomic names and returns information about potential
        matches for these names to known taxa in OTT. This service uses taxonomic
        contexts to disambiguate homonyms and misspelled names; a context may be
        specified using the `context_name` parameter. If no context is specified, then
        the context will be inferred: the shallowest taxonomic context that contains
        all unambiguous names in the input set will be used. A name is considered
        unambiguous if it is not a synonym and has only one exact match to any taxon
        name in the entire taxonomy.

        Taxonomic contexts are uncontested higher taxa that have been selected to
        allow limits to be applied to the scope of TNRS searches (e.g. 'match names
        only within flowering plants'). Once a context has been identified (either
        user-specified or inferred), all taxon name matches will performed only
        against taxa within that context.

        To obtain a list of available taxonomic contexts, use the `tnrs_contexts`
        function.

        Wraps::

            curl -X POST http://devapi.opentreeoflife.org/v2/tnrs/match_names -H "content-type:application/json" -d '{"names":["Aster","Symphyotrichum","Erigeron","Barnadesia"]}'

        Parameters
        ----------
        names : iterable of strings
            An iterable of taxon names to be queried.
        context_name : string
            The name of the taxonomic context to be searched
        do_approximate_matching : bool
            A boolean indicating whether or not to perform approximate string
            (a.k.a. "fuzzy") matching. Will greatly improve speed if this is turned
            OFF (`False`). By default, however, it is on (`True`).
        ids : iterable of strings
            An iterable of string ids to use for identifying names. These will be
            assigned to each name in the names array. If ids is provided, then ids
            and names must be identical in length.
        include_deprecated : bool
            A boolean indicating whether or not to include deprecated taxa in the
            search.
        include_dubious : bool
            Whether to include so-called 'dubious' taxa--those which are not
            accepted by OTT.

        Returns
        -------
        d : dict
            A python dictionary with the following fields:

                "governing_code"
                "unambiguous_name_ids"
                "unmatched_name_ids"
                "matched_name_ids"
                "context"
                "includes_deprecated_taxa"
                "includes_dubious_names"
                "includes_approximate_matches"
                "taxonomy"
                "author"
                "weburl"
                "source"
                "results"
        """
        payload = {
                'names': names,
                'context_name': context_name,
                'do_approximate_matching': do_approximate_matching,
                'ids': ids, 'include_deprecated': include_deprecated,
                'include_dubious': include_dubious, }
        result = self.request(
                '/tnrs/match_names',
                payload=payload)
        return result

    def tnrs_contexts(self):
        """
        Return a list of pre-defined taxonomic contexts (i.e. clades), which can be
        used to limit the scope of tnrs queries.

        Taxonomic contexts are available to limit the scope of TNRS searches. These
        contexts correspond to uncontested higher taxa such as 'Animals' or 'Land
        plants'. This service returns a list containing all available taxonomic
        context names, which may be used as input (via the `context_name` parameter)
        to limit the search scope of `tnrs_match_names`.

        Wraps::

            curl -X POST http://devapi.opentreeoflife.org/v2/tnrs/contexts

        Returns
        -------
        d : dict
            A python dictionary with the following fields:

                "FUNGI"
                "LIFE"
                "ANIMALS"
                "MICROBES"
                "PLANTS"
        """
        return self.request('/tnrs/contexts')

    def tnrs_infer_context(self, names):
        """
        Return a taxonomic context given a list of taxonomic names.

        Find the least inclusive taxonomic context that includes all the unambiguous
        names in the input set. Unambiguous names are names with exact matches to
        non-homonym taxa. Ambiguous names (those without exact matches to non-
        homonym taxa) are indicated in results.

        Wraps::

            curl -X POST http://devapi.opentreeoflife.org/v2/tnrs/infer_context -H "content-type:application/json" -d  '{"names":["Pan","Homo","Mus","Bufo","Drosophila"]}'

        Parameters
        ----------
        names : iterable of strings
            An iterable of taxon names to be queried.

        Returns
        -------
        d : dict
            A python dictionary with the following fields:

                "context_name"
                "context_ott_id"
                "ambiguous_names"
        """
        payload = {'names': names}
        result = self.request(
                '/tnrs/infer_context',
                payload=payload)
        return result

    def taxonomy_about(self):
        """
        Return information about the taxonomy, including version.

        Return metadata and information about the taxonomy itself. Currently the
        available metadata is fairly sparse, but includes (at least) the version,
        and the location from which the complete taxonomy source files can be
        downloaded.

        Wraps::

            curl -X POST http://devapi.opentreeoflife.org/v2/taxonomy/about

        Returns
        -------
        d : dict
            A python dictionary with the following fields:

                "author"
                "weburl"
                "source"
        """
        result = self.request('/taxonomy/about')
        return result

    def taxonomy_lica(self, ott_ids, include_lineage=False):
        """
        Given a set of ott ids, get the taxon that is the least inclusive common
        ancestor (the LICA) of all the identified taxa.

        Return information about the least inclusive common ancestral taxon (the
        LICA) of the identified taxa. A taxonomic LICA is analogous to a most
        recent common ancestor (MRCA) in a phylogenetic tree. For example, the
        LICA for the taxa 'Pan' and 'Lemur' in the taxonomy represented by the
        newick string '(((Pan,Homo,Gorilla)Hominidae,Gibbon)Hominoidea,Lemur)Primates' is 'Primates'.

        Wraps::

            curl -X POST http://devapi.opentreeoflife.org/v2/taxonomy/lica -H 'content-type:application/json' -d '{"ott_ids":[515698,590452,409712,643717]}'

        Parameters
        ----------
        ott_ids : iterable of integers
            An iterable of ott ids.
        include_lineage : bool
            Whether or not to include information about the higher level taxa
            that include the identified LICA. By default, this option is set to
            false. If it is set to true, the lineage will be provided in an
            ordered array, with the least inclusive taxa at lower indices
            (i.e. higher indices are higher taxa).

        Returns
        -------
        d : dict
            A python dictionary with the following fields:

                "lica"
                "ott_ids_not_found"
        """
        if len(ott_ids) == 0:
            raise ValueError('ott_ids cannot be an empty list.')
        payload = {'ott_ids': ott_ids, 'include_lineage': include_lineage}
        result = self.request(
            '/taxonomy/lica',
            payload=payload)
        return result

    def taxonomy_subtree(self, ott_id):
        """
        Given an ott id, return complete taxonomy subtree descended from specified
        taxon.

        Extract and return the inclusive taxonomic subtree i.e. (a subset of the
        taxonomy) below a given taxon. The taxonomy subtree is returned in newick
        format.

        Wraps::

            curl -X POST http://devapi.opentreeoflife.org/v2/taxonomy/subtree -H 'Content-type:application/json' -d '{"ott_id":515698}'

        Parameters
        ----------
        ott_id : integers
            An ott id.

        Returns
        -------
        d : dict
            A python dictionary with the following fields:

                "subtree"
        """
        payload = {'ott_id': ott_id}
        result = self.request(
            '/taxonomy/subtree',
            payload=payload)
        return result

    def taxonomy_taxon(self, ott_id, include_lineage=False):
        """
        Given an ott id, return information about the specified taxon.

        Get information about a known taxon in the taxonomy.

        Wraps::

            curl -X POST http://devapi.opentreeoflife.org/v2/taxonomy/taxon -H 'content-type:application/json' -d '{"ott_id":515698}'

        Parameters
        ----------
        ott_id : integers
            An ott id.
        include_lineage : bool
            Whether or not to include information about all the higher level taxa
            that include this one. By default, this option is set to false. If it is
            set to true, the lineage will be provided in an ordered array, with the
            least inclusive taxa at lower indices (i.e. higher indices are higher
            taxa).

        Returns
        -------
        d : dict
            A python dictionary with the following fields:

                "ot:ottId"
                "rank"
                "flags"
                "unique_name"
                "synonyms"
                "ot:ottTaxonName"
                "node_id"
        """
        payload = {'ott_id': ott_id, 'include_lineage': include_lineage}
        result = self.request(
            '/taxonomy/taxon',
            payload=payload)
        return result

    def studies_find_studies(
            self,
            study_property=None,
            value=None,
            exact=False,
            verbose=False):
        """
        Return a list of studies that match a given property. If no property
        provided, returns a list of all studies.

        Perform a simple search for indexed studies. To find all studies, omit both
        the property and the value from your query.

        Wraps::

            curl -X POST http://devapi.opentreeoflife.org/v2/studies/find_studies -H "content-type:application/json" -d '{"property":"ot:studyId","value":"pg_719","verbose":true}'

        Parameters
        ----------
        study_property : string
            The property to be searched on. A list of searchable properties is
            available from the `studies_properties` function. To find all studies,
            omit both the property and the value from your query.
        value : string
            The value to be searched. This must be passed as a string, but will be
            converted to the datatype corresponding to the specified searchable
            value. To find all studies, omit both the property and the value from
            your query.
        exact : bool
            Whether to perform exact matching ONLY. Defaults to false, i.e. fuzzy
            matching is enabled. Fuzzy matching is only available for some string
            properties.
        verbose : bool
            Whether or not to include all metadata. By default, only the nexson ids
            of elements will be returned.

        Returns
        -------
        d : dict
            A python dictionary with the following fields:

                "matched_studies"
        """
        payload = {"exact" : exact}
        if study_property is None or value is None:
            if study_property is not None:
                raise ValueError("If 'study_property' is specified, 'value' must be specified as well")
            if value is not None:
                raise ValueError("If 'value' is specified, 'study_property' must be specified as well")
        else:
            payload["property"] = study_property
            payload["value"] = value
        result = self.request(
            '/studies/find_studies',
            payload=payload)
        return result

    def studies_find_trees(
            self,
            study_property,
            value,
            exact=False,
            verbose=False):
        """
        Return a list of trees (and the studies that contain them) that match a
        given property.

        Perform a simple search for trees in indexed studies.

        Wraps::

            curl -X POST http://devapi.opentreeoflife.org/v2/studies/find_trees -H "content-type:application/json" -d '{"property":"ot:ottTaxonName","value":"Garcinia"}'

        Parameters
        ----------
        study_property : string
            The property to be searched on. A list of searchable properties is
            available from the `studies_properties` function.
        value : string
            The value to be searched. This must be passed as a string, but will be
            converted to the datatype corresponding to the specified searchable
            value.
        exact : bool
            Whether to perform exact matching ONLY. Defaults to false, i.e. fuzzy
            matching is enabled. Fuzzy matching is only available for some string
            properties.
        verbose : bool
            Whether or not to include all metadata. By default, only the nexson ids
            of elements will be returned.

        Returns
        -------
        d : dict
            A python dictionary with the following fields:

                "matched_studies"
        """
        payload = {
                "exact" : exact,
                "property": study_property,
                "value": value, }
        result = self.request(
            '/studies/find_trees',
            payload=payload)
        return result

    def studies_properties(self):
        """
        Return a list of properties that can be used to search studies and trees.

        Get a list of properties that can be used to search for studies and trees.

        Wraps::

            curl -X POST http://devapi.opentreeoflife.org/v2/studies/properties

        Returns
        -------
        d : dict
            A python dictionary with the following fields:

                "tree_properties"
                "study_properties"
        """
        result = self.request('/studies/properties')
        return result

    def get_study(self, study_id):
        result = self.request('/study/{STUDY_ID}'.format(STUDY_ID=study_id),
                protocol="GET")
        return result

    def get_study_tree(
            self,
            study_id,
            tree_id,
            schema="nexson"):
        schema = schema.lower()
        payload = {
            "STUDY_ID": study_id,
            "TREE_ID": tree_id,
            "TREE_SCHEMA_EXT": self.otl_format_specifier_extension(schema),
        }
        if schema in ["json", "nexson",]:
            process_response_as = "json"
        else:
            process_response_as = "text"
        sub_url = '/study/{STUDY_ID}/tree/{TREE_ID}{TREE_SCHEMA_EXT}'.format(**payload)
        result = self.request(
                sub_url,
                protocol="GET",
                process_response_as=process_response_as)
        return result

    def get_study_meta(self, study_id):
        payload = {
            "STUDY_ID": study_id,
        }
        sub_url = '/study/{STUDY_ID}/meta'.format(**payload)
        result = self.request(
                sub_url,
                protocol="GET")
        return result

    def get_study_subtree(
            self,
            study_id,
            tree_id,
            subtree_id,
            schema="nexson"):
        schema = schema.lower()
        payload = {
            "STUDY_ID": study_id,
            "TREE_ID": tree_id,
            "SUBTREE_ID": subtree_id,
            "TREE_SCHEMA_EXT": self.otl_format_specifier_extension(schema),
        }
        if schema in ["json", "nexson",]:
            process_response_as = "json"
        else:
            process_response_as = "text"
        sub_url = '/study/{STUDY_ID}/tree/{TREE_ID}{TREE_SCHEMA_EXT}?subtree_id={SUBTREE_ID}'.format(**payload)
        result = self.request(
                sub_url,
                protocol="GET",
                process_response_as=process_response_as)
        return result

    def get_study_otu(
            self,
            study_id,
            otu_name=""):
        payload = {
            "STUDY_ID": study_id,
            "OTU": otu_name,
        }
        sub_url = '/study/{STUDY_ID}/otu/{OTU}'.format(**payload)
        try:
            result = self.request(
                    sub_url,
                    protocol="GET")
        except HTTPError as e:
            # TODO: More specific exception
            raise OpenTreeService.OpenTreeError(e)
        return result

    def get_study_otus(
            self,
            study_id,
            otu_names=""):
        payload = {
            "STUDY_ID": study_id,
            "OTUS": otu_names,
        }
        sub_url = '/study/{STUDY_ID}/otus/{OTUS}'.format(**payload)
        try:
            result = self.request(
                    sub_url,
                    protocol="GET")
        except HTTPError as e:
            # TODO: More specific exception
            raise OpenTreeService.OpenTreeError(e)
        return result

    def get_study_otumap(self, study_id):
        payload = {
            "STUDY_ID": study_id,
        }
        sub_url = '/study/{STUDY_ID}/otumap'.format(**payload)
        result = self.request(
                sub_url,
                protocol="GET")
        return result

GLOBAL_OPEN_TREE_SERVICE = OpenTreeService(base_url=None)

def tol_about(study_list=True):
    """
    Forwards to :meth:`OpenTreeService.tol_about()` of the global :class:`OpenTreeService` instance.
    """
    return GLOBAL_OPEN_TREE_SERVICE.tol_about(study_list=study_list)

def tol_mrca(
        ott_ids=None,
        node_ids=None,
        ):
    """
    Forwards to :meth:`OpenTreeService.tol_mrca()` of the global :class:`OpenTreeService` instance.
    """
    return GLOBAL_OPEN_TREE_SERVICE.tol_mrca(
            ott_ids=ott_ids,
            node_ids=node_ids)

def tol_subtree(
        ott_id=None,
        node_id=None,
        tree_id=None,
        ):
    """
    Forwards to :meth:`OpenTreeService.tol_subtree()` of the global :class:`OpenTreeService` instance.
    """
    return GLOBAL_OPEN_TREE_SERVICE.tol_subtree(
            ott_id=ott_id,
            node_id=node_id,
            tree_id=tree_id)

def tol_induced_tree(
        ott_ids=None,
        node_ids=None,
        ):
    """
    Forwards to :meth:`OpenTreeService.tol_induced_tree()` of the global :class:`OpenTreeService` instance.
    """
    return GLOBAL_OPEN_TREE_SERVICE.tol_induced_tree(
            ott_ids=ott_ids,
            node_ids=node_ids)

def gol_about():
    """
    Forwards to :meth:`OpenTreeService.gol_about()` of the global :class:`OpenTreeService` instance.
    """
    return GLOBAL_OPEN_TREE_SERVICE.gol_about()

def gol_source_tree(
        study_id,
        tree_id,
        git_sha,
        schema=None,
        ):
    """
    Forwards to :meth:`OpenTreeService.gol_source_tree()` of the global :class:`OpenTreeService` instance.
    """
    return GLOBAL_OPEN_TREE_SERVICE.gol_source_tree(
            study_id=study_id,
            tree_id=tree_id,
            git_sha=git_sha,
            schema=schema)

def gol_node_info(
        ott_id=None,
        node_id=None,
        include_lineage=False,
        ):
    """
    Forwards to :meth:`OpenTreeService.gol_node_info()` of the global :class:`OpenTreeService` instance.
    """
    return GLOBAL_OPEN_TREE_SERVICE.gol_node_info(
            ott_id=ott_id,
            node_id=node_id,
            include_lineage=include_lineage)

def tnrs_match_names(
        names,
        context_name=None,
        do_approximate_matching=True,
        ids=None,
        include_deprecated=False,
        include_dubious=False,
        ):
    """
    Forwards to :meth:`OpenTreeService.tnrs_match_names()` of the global :class:`OpenTreeService` instance.
    """
    return GLOBAL_OPEN_TREE_SERVICE.tnrs_match_names(
        names=names,
        context_name=context_name,
        do_approximate_matching=do_approximate_matching,
        ids=ids,
        include_deprecated=include_deprecated,
        include_dubious=include_dubious)

def tnrs_contexts():
    """
    Forwards to :meth:`OpenTreeService.tnrs_contexts()` of the global :class:`OpenTreeService` instance.
    """
    return GLOBAL_OPEN_TREE_SERVICE.tnrs_contexts()

def tnrs_infer_context(names):
    """
    Forwards to :meth:`OpenTreeService.tnrs_infer_context()` of the global :class:`OpenTreeService` instance.
    """
    return GLOBAL_OPEN_TREE_SERVICE.tnrs_infer_context(names)

def taxonomy_about():
    """
    Forwards to :meth:`OpenTreeService.taxonomy_about()` of the global :class:`OpenTreeService` instance.
    """
    return GLOBAL_OPEN_TREE_SERVICE.taxonomy_about()

def taxonomy_lica(ott_ids, include_lineage=False):
    """
    Forwards to :meth:`OpenTreeService.taxonomy_lica()` of the global :class:`OpenTreeService` instance.
    """
    return GLOBAL_OPEN_TREE_SERVICE.taxonomy_lica(
            ott_ids=ott_ids,
            include_lineage=include_lineage,
            )

def taxonomy_subtree(ott_id):
    """
    Forwards to :meth:`OpenTreeService.taxonomy_subtree()` of the global :class:`OpenTreeService` instance.
    """
    return GLOBAL_OPEN_TREE_SERVICE.taxonomy_subtree(ott_id=ott_id)

def taxonomy_taxon(ott_id, include_lineage=False):
    """
    Forwards to :meth:`OpenTreeService.taxonomy_taxon()` of the global :class:`OpenTreeService` instance.
    """
    return GLOBAL_OPEN_TREE_SERVICE.taxonomy_taxon(
            ott_id=ott_id,
            include_lineage=include_lineage,
            )

def studies_find_studies(
        study_property=None,
        value=None,
        exact=False,
        verbose=False,
        ):
    """
    Forwards to :meth:`OpenTreeService.studies_find_studies()` of the global :class:`OpenTreeService` instance.
    """
    return GLOBAL_OPEN_TREE_SERVICE.studies_find_studies(
            study_property=study_property,
            value=value,
            exact=exact,
            verbose=verbose,
            )

def studies_find_trees(
        study_property,
        value,
        exact=False,
        verbose=False,
        ):
    """
    Forwards to :meth:`OpenTreeService.studies_find_trees()` of the global :class:`OpenTreeService` instance.
    """
    return GLOBAL_OPEN_TREE_SERVICE.studies_find_trees(
            study_property=study_property,
            value=value,
            exact=exact,
            verbose=verbose,
            )

def studies_properties():
    """
    Forwards to :meth:`OpenTreeService.studies_properties()` of the global :class:`OpenTreeService` instance.
    """
    return GLOBAL_OPEN_TREE_SERVICE.studies_properties()

def get_study(study_id):
    return GLOBAL_OPEN_TREE_SERVICE.get_study(study_id=study_id)

def get_study_tree(
        study_id,
        tree_id,
        schema="nexson",
        ):
    return GLOBAL_OPEN_TREE_SERVICE.get_study_tree(
            study_id=study_id,
            tree_id=tree_id,
            schema=schema,
            )

def get_study_meta(study_id):
    return GLOBAL_OPEN_TREE_SERVICE.get_study_meta(study_id=study_id)

def get_study_subtree(
        study_id,
        tree_id,
        subtree_id,
        schema="nexson",
        ):
    return GLOBAL_OPEN_TREE_SERVICE.get_study_subtree(
            study_id=study_id,
            tree_id=tree_id,
            subtree_id=subtree_id,
            schema=schema,
            )

def get_study_otu(
        study_id,
        otu_name="",
        ):
    return GLOBAL_OPEN_TREE_SERVICE.get_study_otu(
            study_id=study_id,
            otu_name=otu_name,
            )

def get_study_otus(
        study_id,
        otu_names="",
        ):
    return GLOBAL_OPEN_TREE_SERVICE.get_study_otus(
            study_id=study_id,
            otu_names=otu_names,
            )

def get_study_otumap(study_id, ):
    return GLOBAL_OPEN_TREE_SERVICE.get_study_otumap(
            study_id=study_id,
            )

# get_study_otumap <- function(study){
#     otl_GET(path=paste("study", study,"otumap", sep="/"))

if __name__ == "__main__":

    def human_readable_output_inspection(function_name, function_output):
        import pprint
        width = 120
        printer = pprint.PrettyPrinter(indent=0, width=width, depth=None, stream=None)
        print('-' * width)
        print('Output of', function_name)
        print('-' * width)
        printer.pprint(function_output)
        print()

    ### tree_of_life

    # curl -X POST http://devapi.opentreeoflife.org/v2/tree_of_life/about -H "content-type:application/json"  -d '{"study_list":false}'
    human_readable_output_inspection(
        function_name='tol_about',
        function_output=tol_about())

    # $ curl -X POST http://devapi.opentreeoflife.org/v2/tree_of_life/mrca -H "content-type:application/json" -d '{"ott_ids":[412129, 536234]}'
    human_readable_output_inspection(
        function_name='tol_mrca',
        function_output=tol_mrca(ott_ids=[412129, 536234]))

    # curl -X POST http://devapi.opentreeoflife.org/v2/tree_of_life/subtree -H "content-type:application/json" -d '{"ott_id":3599390}'
    human_readable_output_inspection(
        function_name='tol_subtree',
        function_output=tol_subtree(ott_id=3599390))

    # curl -X POST http://devapi.opentreeoflife.org/v2/tree_of_life/induced_subtree -H "content-type:application/json" -d '{"ott_ids":[292466, 501678, 267845, 666104, 316878, 102710, 176458]}'
    human_readable_output_inspection(
        function_name='tol_induced_tree',
        function_output=tol_induced_tree(ott_ids=[292466, 501678, 267845, 666104, 316878, 102710, 176458]))

    # ### graph_of_life

    # curl -X POST http://devapi.opentreeoflife.org/v2/graph/about
    human_readable_output_inspection(
        function_name='gol_about',
        function_output=gol_about())

    # curl -X POST http://devapi.opentreeoflife.org/v2/graph/source_tree -H "content-type:applicatin/json" -d '{"study_id":"pg_420", "tree_id":"522", "git_sha":"a2c48df995ddc9fd208986c3d4225112550c8452"}'
    human_readable_output_inspection(
        function_name='gol_source_tree',
        function_output=gol_source_tree(study_id="pg_420", tree_id="522", git_sha="a2c48df995ddc9fd208986c3d4225112550c8452"))

    # curl -X POST http://devapi.opentreeoflife.org/v2/graph/node_info -H "content-type:application/json" -d '{"ott_id":810751}'
    human_readable_output_inspection(
        function_name='gol_node_info',
        function_output=gol_node_info(ott_id=810751))

    ### tnrs

    # curl -X POST http://devapi.opentreeoflife.org/v2/tnrs/match_names -H "content-type:application/json" -d '{"names":["Aster","Symphyotrichum","Erigeron","Barnadesia"]}'
    human_readable_output_inspection(
        function_name='tnrs_match_names',
        function_output=tnrs_match_names(names=["Aster","Symphyotrichum","Erigeron","Barnadesia"]))

    # curl -X POST http://devapi.opentreeoflife.org/v2/tnrs/contexts
    human_readable_output_inspection(
        function_name='tnrs_contexts',
        function_output=tnrs_contexts())

    # curl -X POST http://devapi.opentreeoflife.org/v2/tnrs/infer_context -H "content-type:application/json" -d  '{"names":["Pan","Homo","Mus","Bufo","Drosophila"]}'
    human_readable_output_inspection(
        function_name='tnrs_infer_context',
        function_output=tnrs_infer_context(names=["Pan","Homo","Mus","Bufo","Drosophila"]))

    ### taxonomy

    # curl -X POST http://devapi.opentreeoflife.org/v2/taxonomy/about
    human_readable_output_inspection(
        function_name='taxonomy_about',
        function_output=taxonomy_about())

    # curl -X POST http://devapi.opentreeoflife.org/v2/taxonomy/lica -H 'content-type:application/json' -d '{"ott_ids":[515698,590452,409712,643717]}'
    human_readable_output_inspection(
        function_name='taxonomy_lica',
        function_output=taxonomy_lica(ott_ids=[515698,590452,409712,643717]))

    # curl -X POST http://devapi.opentreeoflife.org/v2/taxonomy/subtree -H 'Content-type:application/json' -d '{"ott_id":515698}'
    human_readable_output_inspection(
        function_name='taxonomy_subtree',
        function_output=taxonomy_subtree(ott_id=515698))

    # curl -X POST http://devapi.opentreeoflife.org/v2/taxonomy/taxon -H 'content-type:application/json' -d '{"ott_id":515698}'
    human_readable_output_inspection(
        function_name='taxonomy_taxon',
        function_output=taxonomy_taxon(ott_id=515698))

    ### studies

    # curl -X POST http://devapi.opentreeoflife.org/v2/studies/find_studies -H "content-type:application/json" -d '{"property":"ot:studyId","value":"pg_719","verbose":true}'
    human_readable_output_inspection(
        function_name='studies_find_studies',
        function_output=studies_find_studies(study_property="ot:studyId", value="pg_719", verbose=True))

    # curl -X POST http://devapi.opentreeoflife.org/v2/studies/find_trees -H "content-type:application/json" -d '{"property":"ot:ottTaxonName","value":"Garcinia"}'
    human_readable_output_inspection(
        function_name='studies_find_trees',
        function_output=studies_find_trees(study_property="ot:ottTaxonName", value="Garcinia"))

    # curl -X POST http://devapi.opentreeoflife.org/v2/studies/properties
    human_readable_output_inspection(
        function_name='studies_properties',
        function_output=studies_properties())

    # curl http://devapi.opentreeoflife.org/v2/study/pg_1144
    human_readable_output_inspection(
        function_name='get_study',
        function_output=get_study(study_id="pg_1144"))

    # curl http://devapi.opentreeoflife.org/v2/study/pg_1144/tree/tree2324
    human_readable_output_inspection(
        function_name='get_study_tree',
        function_output=get_study_tree(study_id="pg_1144", tree_id="tree2324"))

    # curl http://devapi.opentreeoflife.org/v2/study/pg_1144/meta
    human_readable_output_inspection(
        function_name='get_study_meta',
        function_output=get_study_meta(study_id="pg_1144"))

    human_readable_output_inspection(
        function_name='get_study_subtree',
        function_output=get_study_subtree("pg_1144", "tree2324", "ingroup", "newick"))

    human_readable_output_inspection(
        function_name='get_study_otu',
        function_output=get_study_otu("pg_719"))

    # print(get_study_otu("pg_719", "Nymphoides furculifolia"))
