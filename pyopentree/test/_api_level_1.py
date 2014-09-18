from __future__ import print_function
from __future__ import unicode_literals
import unittest
import sys
import locale
ENCODING = locale.getdefaultlocale()[1]
# so we import local api before any globally installed one
sys.path.insert(0,"../")
import opentreelib
from opentreelib import OpenTreeService
import json
if sys.version_info.major < 3:
    from urllib2 import urlopen
    from urllib2 import URLError, HTTPError
else:
    from urllib.request import urlopen
    from urllib.error import URLError

use_file = True

def exec_and_return_locals(statement, locals_dict=None):
    """
    Executes `statement` and returns locals dict.
    """
    if locals_dict is None:
        locals_dict = locals()
    exec(statement, None, locals_dict)
    return locals_dict

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


class OpenTreeLib(unittest.TestCase):

    def test_tree_of_life_tests(self):
        print("\n" + bcolors.OKBLUE + "     Running ToL tests\n" + bcolors.ENDC)
        try:
            if (not use_file):
                data_file = urlopen('https://raw.githubusercontent.com/OpenTreeOfLife/opentree-interfaces/master/python/test/tree_of_life.json')
                data = json.loads(data_file.read().decode(ENCODING))
            else:
                with open('tree_of_life.json') as data_file:
                    data = json.load(data_file)
            self.run_tests(data)
        except URLError as e:
            if e.code == 404:
                self.assertTrue(False,"Error fetching tree_of_life.json from GitHub")
            else:
                raise


    def test_graph_of_life_tests(self):
        print("\n" + bcolors.OKBLUE + "     Running GoL tests\n" + bcolors.ENDC)
        try:
            response = opentreelib.gol_source_tree("pg_420", "522", "a2c48df995ddc9fd208986c3d4225112550c8452")

            if (not use_file):
                data_file = urlopen('https://raw.githubusercontent.com/OpenTreeOfLife/opentree-interfaces/master/python/test/graph_of_life.json')
                data = json.loads(data_file.read().decode(ENCODING))
            else:
                with open('graph_of_life.json') as data_file:
                    data = json.load(data_file)
            self.run_tests(data)
        except URLError as e:
            if e.code == 404:
                self.assertTrue(False,"Error fetching graph_of_life.json from GitHub")
            else:
                raise


    def test_tnrs_tests(self):
        print("\n" + bcolors.OKBLUE + "     Running TNRS tests\n" + bcolors.ENDC)
        try:
            if (not use_file):
                data_file = urlopen('https://raw.githubusercontent.com/OpenTreeOfLife/opentree-interfaces/master/python/test/tnrs.json')
                data = json.loads(data_file.read().decode(ENCODING))
            else:
                with open('tnrs.json') as data_file:
                    data = json.load(data_file)
            self.run_tests(data)
        except URLError as e:
            if e.code == 404:
                self.assertTrue(False,"Error fetching tnrs.json from GitHub")
            else:
                raise


    def test_taxonomy_tests(self):
        print("\n" + bcolors.OKBLUE + "     Running Taxonomy tests\n" + bcolors.ENDC)
        try:
            if (not use_file):
                data_file = urlopen('https://raw.githubusercontent.com/OpenTreeOfLife/opentree-interfaces/master/python/test/taxonomy.json')
                data = json.loads(data_file.read().decode(ENCODING))
            else:
                with open('taxonomy.json') as data_file:
                    data = json.load(data_file)
            self.run_tests(data)
        except URLError as e:
            if e.code == 404:
                self.assertTrue(False,"Error fetching taxonomy.json from GitHub")
            else:
                raise

    def test_studies_tests(self):
        print("\n" + bcolors.OKBLUE + "     Running Studies tests\n" + bcolors.ENDC)
        try:
            if (not use_file):
                data_file = urlopen('https://raw.githubusercontent.com/OpenTreeOfLife/opentree-interfaces/master/python/test/studies.json')
                data = json.loads(data_file.read().decode(ENCODING))
            else:
                with open('studies.json') as data_file:
                    data = json.load(data_file)
            self.run_tests(data)
        except URLError as e:
            if e.code == 404:
                self.assertTrue(False,"Error fetching studies.json from GitHub")
            else:
                raise

    # This is the function that does the heavy lifting
    def run_tests(self, data):
        for key in data:
            print("\tRunning test: "+key)
            try:
                if (data[key]['test_input'] == {}):
                    response = exec_and_return_locals('response = opentreelib.'+data[key]['test_function']+'()', locals())["response"]
                else:
                    arguments = ""
                    i = 0
                    for arg in data[key]['test_input']:
                        if i == len(data[key]['test_input'])-1:
                            arguments = arguments + arg + "=" + str(data[key]['test_input'][arg])
                        else:
                            arguments = arguments + arg + "=" + str(data[key]['test_input'][arg]) + ","
                        i += 1
                    response = exec_and_return_locals('response = opentreelib.'+data[key]['test_function']+'('+arguments+')', locals())["response"]
            except:
                if "error" in data[key]['tests']:
                    for sub_test in data[key]['tests']['error']:
                        with self.assertRaises(eval(sub_test[0])):
                            if (data[key]['test_input'] == 'null'):
                                exec_and_return_locals('response = opentreelib.'+data[key]['test_function']+'()', locals())
                            else:
                                arguments = ""
                                i = 0
                                for arg in data[key]['test_input']:
                                    if i == len(data[key]['test_input'])-1:
                                        arguments = arguments + arg + "=" + str(data[key]['test_input'][arg])
                                    else:
                                        arguments = arguments + arg + "=" + str(data[key]['test_input'][arg]) + ","
                                    i += 1
                                response = exec_and_return_locals('response = opentreelib.'+data[key]['test_function']+'('+arguments+')', locals())["response"]
                else:
                    # we got here because there was an exception, but we didn't test for it. Raise it.
                    raise
            # now test as we didn't get an error
            for test in data[key]['tests']:
                if test == 'contains':
                    for sub_test in data[key]['tests'][test]:
                        self.assertTrue(sub_test[0] in response, key+": "+sub_test[1])
                elif test == 'of_type':
                    sub_test = data[key]['tests'][test]
                    self.assertTrue(isinstance(response,eval(sub_test[0])), key+": "+sub_test[1])
                elif test == 'equals':
                    for sub_test in data[key]['tests'][test]:
                        self.assertTrue(eval("response["+sub_test[0][0]+"]") == eval(sub_test[0][1]), key+": "+sub_test[1])
                elif test == 'len_gt':
                    for sub_test in data[key]['tests'][test]:
                        self.assertTrue(eval("len(response["+sub_test[0][0]+"])") > sub_test[0][1], key+": "+sub_test[1] + " len "+str(eval("len(response["+sub_test[0][0]+"])")))
                elif test == 'len_lt':
                    for sub_test in data[key]['tests'][test]:
                        self.assertTrue(eval("len(response["+sub_test[0][0]+"])") < sub_test[0][1], key+": "+sub_test[1] + " len "+str(eval("len(response["+sub_test[0][0]+"])")))
                elif test == "error":
                    continue
                    # dealt with above!
                else:
                    print("\t\t" + bcolors.FAIL + "Oh oh. I didn't know how to deal with test type: " + test + bcolors.ENDC)



if __name__ == '__main__':
    unittest.main()

