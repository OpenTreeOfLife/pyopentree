#! /usr/bin/env python

###############################################################################
##
##  Copyright 2014 Jeet Sukumaran.
##
##  This program is free software; you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation; either version 3 of the License, or
##  (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.
##
##  You should have received a copy of the GNU General Public License along
##  with this program. If not, see <http://www.gnu.org/licenses/>.
##
###############################################################################

"""
This program does something.
"""

import sys
import os
import argparse
import collections
import pyopentree

try:
    import vcr
    CACHING_AVAILABLE = True
except ImportError:
    CACHING_AVAILABLE = False
    pass

__prog__ = os.path.basename(__file__)
__version__ = "1.0.0"
__description__ = __doc__
__author__ = 'Jeet Sukumaran'
__copyright__ = 'Copyright (C) 2014 Jeet Sukumaran.'

import pprint
_DEBUG_LOG = pprint.PrettyPrinter(
        indent=0,
        width=80,
        depth=None,
        stream=None)

class OpenTreeDoiSearcher(pyopentree.OpenTreeService):

    StudyInfo = collections.namedtuple("StudyInfo", ["study_id", "doi", "citation"])

    def __init__(self, *args, **kwargs):
        self.cache_path = kwargs.pop("cache_path",
                ".opentree.cache.yaml")
        pyopentree.OpenTreeService.__init__(self, *args, **kwargs)

    def open_url(self, request):
        if CACHING_AVAILABLE:
            with vcr.use_cassette(self.cache_path,
                    record_mode="new_episodes"):
                return pyopentree.OpenTreeService.open_url(self, request)
        else:
            return pyopentree.OpenTreeService.open_url(self, request)

    def slice_from(self, slice_from, slice_limit):
        """
        - slice_from: 1-based index of where to start slice; defaults to None (=first)
        - slice_limit: number of items to get; defaults to None (=all)
        """
        if slice_from is not None:
            slice_start = slice_from - 1
        else:
            slice_start = None
        if slice_limit is not None:
            if slice_start is None:
                slice_to = slice_limit
            else:
                slice_to = slice_start + slice_limit
        else:
            slice_to = None
        slice_result = slice(slice_from, slice_to)
        return slice_result

    def yield_studies(
            self,
            list_from=None,
            max_studies=None):
        studies_dict = self.studies_find_studies()
        study_list = []
        study_slice = self.slice_from(list_from, max_studies)
        for study_dict in studies_dict["matched_studies"][study_slice]:
            study_id = study_dict["ot:studyId"]
            study_dict = pyopentree.get_study_meta(study_id)["nexml"]
            citation = study_dict.get('^ot:studyPublicationReference', None)
            doi_dict = study_dict.get('^ot:studyPublication', None)
            if doi_dict is not None:
                doi = doi_dict["@href"]
            else:
                doi = None
            if doi is not None:
                s = OpenTreeDoiSearcher.StudyInfo(
                        study_id=study_id,
                        doi=doi,
                        citation=citation)
                yield s

    def list_studies(self,
            list_from=None,
            max_studies=None,
            as_table=True,
            table_column_delimiter="\t",
            out=sys.stdout):
        for study in self.yield_studies(
                list_from=list_from,
                max_studies=max_studies):
            if as_table:
                out.write("{}{}{}\n".format(
                    study.doi,
                    table_column_delimiter,
                    study.citation))
            else:
                out.write("[{}]\n{}\n\n".format(
                    study.doi,
                    study.citation))

def main():
    """
    Main CLI handler.
    """

    parser = argparse.ArgumentParser(description=__description__)
    subparsers = parser.add_subparsers(help='commands', dest="subparser_name")

    # A list command
    list_studies_parser = subparsers.add_parser('list-studies', help='List contents')
    list_studies_parser.add_argument("--filter-for-taxon",
            action="append",
            default=False,
            help="Filter for studies with specific taxa")
    list_studies_parser.add_argument("--list-from",
            type=int,
            default=None,
            help="First study to list (default: first)")
    list_studies_parser.add_argument("--max-studies",
            type=int,
            default=None,
            help="Maximum number of studies to list")
    list_studies_parser.add_argument("--as-table",
            action="store_true",
            default=False,
            help="Format as (tab-delimited) rows")

    # A create command
    # create_parser = subparsers.add_parser('create', help='Create a directory')
    # create_parser.add_argument('dirname', action='store', help='New directory to create')
    # create_parser.add_argument('--read-only', default=False, action='store_true',
    #                         help='Set permissions to prevent writing to the directory',
    #                         )

    # # A delete command
    # delete_parser = subparsers.add_parser('delete', help='Remove a directory')
    # delete_parser.add_argument('dirname', action='store', help='The directory to remove')
    # delete_parser.add_argument('--recursive', '-r', default=False, action='store_true',
    #                         help='Remove the contents of the directory, too',
    #                         )
    # ots = pyopentree.OpenTreeService()

    args = parser.parse_args()

    ots = OpenTreeDoiSearcher()
    if args.subparser_name == "list-studies":
        ots.list_studies(
                list_from=args.list_from,
                max_studies=args.max_studies,
                as_table=args.as_table,
                )
    else:
        parser.print_usage(sys.stderr)
        sys.exit(1)


    # studies = ots.studies_find_studies()
    # study_ids = []
    # for study_dict in studies["matched_studies"][:10]:
    #     study_ids.append(study_dict["ot:studyId"])
    # for study_id in study_ids:
    #     study_dict = ots.get_study_meta(study_id)
    #     x = study_dict["nexml"]
    #     citation = x.get('^ot:studyPublicationReference', None)
    #     doi_dict = x.get('^ot:studyPublication', None)
    #     if doi_dict is not None:
    #         doi = doi_dict["@href"]
    #     else:
    #         doi = None
    #     if doi is not None:
    #         print("{}\n    {}\n".format(doi, citation))

if __name__ == '__main__':
    main()


