import unittest
import sys
# so we import local api before any globally installed one
sys.path.insert(0,"../pyopentree")
# we might also be calling this from root, so
sys.path.insert(0,"pyopentree")
import opentreeservice
from opentreeservice import OpenTreeService
import json
from urllib2 import urlopen
from urllib2 import URLError, HTTPError

use_file = False
TestingOpenTreeClass = OpenTreeService()
TestingOpenTreeClass.is_testing_mode = True

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

class OpenTreeLib(unittest.TestCase):

    def test_tree_of_life_tests(self):
        print "\n" + bcolors.OKBLUE + "     Running ToL tests\n" + bcolors.ENDC
        try:
            if (not use_file):
                data_file = urlopen('https://raw.githubusercontent.com/OpenTreeOfLife/shared-api-tests/master/tree_of_life.json')
                data = json.loads(data_file.read())
            else:
                data_file = open('tree_of_life.json').read()
                data = json.loads(data_file)
            self.run_tests(data)
        except URLError, e:
            if e.code == 404:
                self.assert_(False,"Error fetching tree_of_life.json from GitHub")
            else:
                raise


    def test_graph_of_life_tests(self):
        print "\n" + bcolors.OKBLUE + "     Running GoL tests\n" + bcolors.ENDC
        try:
            response = opentreeservice.gol_source_tree("pg_420", "522", "a2c48df995ddc9fd208986c3d4225112550c8452")

            if (not use_file):
                data_file = urlopen('https://raw.githubusercontent.com/OpenTreeOfLife/shared-api-tests/master/graph_of_life.json')
                data = json.loads(data_file.read())
            else:
                data_file = open('graph_of_life.json').read()
                data = json.loads(data_file)
            self.run_tests(data)
        except URLError, e:
            if e.code == 404:
                self.assert_(False,"Error fetching graph_of_life.json from GitHub")
            else:
                raise


    def test_tnrs_tests(self):
        print "\n" + bcolors.OKBLUE + "     Running TNRS tests\n" + bcolors.ENDC
        try:
            if (not use_file):
                data_file = urlopen('https://raw.githubusercontent.com/OpenTreeOfLife/shared-api-tests/master/tnrs.json')
                data = json.loads(data_file.read())
            else:
                data_file = open('tnrs.json').read()
                data = json.loads(data_file)
            self.run_tests(data)
        except URLError, e:
            if e.code == 404:
                self.assert_(False,"Error fetching tnrs.json from GitHub")
            else:
                raise


    def test_taxonomy_tests(self):
        print "\n" + bcolors.OKBLUE + "     Running Taxonomy tests\n" + bcolors.ENDC
        try:
            if (not use_file):
                data_file = urlopen('https://raw.githubusercontent.com/OpenTreeOfLife/shared-api-tests/master/taxonomy.json')
                data = json.loads(data_file.read())
            else:
                data_file = open('taxonomy.json').read()
                data = json.loads(data_file)
            self.run_tests(data)
        except URLError, e:
            if e.code == 404:
                self.assert_(False,"Error fetching taxonomy.json from GitHub")
            else:
                raise

    def test_studies_tests(self):
        print "\n" + bcolors.OKBLUE + "     Running Studies tests\n" + bcolors.ENDC
        try:
            if (not use_file):
                data_file = urlopen('https://raw.githubusercontent.com/OpenTreeOfLife/shared-api-tests/master/studies.json')
                data = json.loads(data_file.read())
            else:
                data_file = open('studies.json').read()
                data = json.loads(data_file)
            self.run_tests(data)
        except URLError, e:
            if e.code == 404:
                self.assert_(False,"Error fetching studies.json from GitHub")
            else:
                raise

    def construct_arguments(self,data):
        
        arguments = ""
        i = 0

        for arg in data['test_input']:
            if isinstance(data['test_input'][arg], basestring):
                arg_val = "'"+data['test_input'][arg]+"'"
            else:
                arg_val = str(data['test_input'][arg])
            # Exceptions - some keywords need amended to python values
            if data['test_function'] == 'studies_find_studies':
                if arg == 'property':
                    # this is actually study_property
                    arg = 'property_name'
                if arg == 'value':
                    arg = 'property_value'
            if data['test_function'] == 'studies_find_trees':
                if arg == 'property':
                    # this is actually study_property
                    arg = 'property_name'
                if arg == 'value':
                    arg = 'property_value'

            if i == len(data)-1:
                arguments = arguments + arg + "=" + arg_val
            else:
                arguments = arguments + arg + "=" + arg_val + ","
            i += 1

        return 'response = TestingOpenTreeClass.'+data['test_function']+'('+arguments+')'

    # This is the function that does the heavy lifting
    def run_tests(self, data):

        for key in data:
            print "\tRunning test: "+key
            try:
                if (data[key]['test_input'] == {}):
                    exec('response = TestingOpenTreeClass.'+data[key]['test_function']+'()')
                else:
                    args = self.construct_arguments(data[key])
                    exec(args)
            except:
                if "parameters_error" in data[key]['tests']:
                    with self.assertRaises(eval(data[key]['tests']['parameters_error'][0])):
                        if (data[key]['test_input'] == {}):
                            exec('response = TestingOpenTreeClass.'+data[key]['test_function']+'()')
                        else:
                            args = self.construct_arguments(data[key])
                            exec(args)
                else:
                    # we got here because there was an exception, but we didn't test for it. Raise it.
                    raise
            # now test as we didn't get an error
            for test in data[key]['tests']:
                if test == 'contains':
                    for sub_test in data[key]['tests'][test]:
                        self.assert_(sub_test[0] in response, key+": "+sub_test[1])
                elif test == 'of_type':
                    sub_test = data[key]['tests'][test]
                    self.assert_(isinstance(response,eval(sub_test[0])), key+": "+sub_test[1])
                elif test == 'equals':
                    for sub_test in data[key]['tests'][test]:
                        self.assert_(eval("response['"+sub_test[0][0]+"']") == sub_test[0][1], key+": "+sub_test[1])
                elif test == 'deep_equals':
                    for sub_test in data[key]['tests'][test]:
                        results = ""
                        i = 0
                        for result in sub_test[0][0]:
                            if isinstance(result,basestring):
                                results += "['" + result + "']"
                            else:
                                results += "["+str(result)+"]"
                            i += 1

                        self.assert_(eval("response"+results) == sub_test[0][1], key+": "+sub_test[1])
                elif test == 'length_greater_than':
                    for sub_test in data[key]['tests'][test]:
                        self.assert_(eval("len(response['"+sub_test[0][0]+"'])") > sub_test[0][1], key+": "+sub_test[1] + " len "+str(eval("len(response['"+sub_test[0][0]+"'])")))
                elif test == 'length_less_than':
                    for sub_test in data[key]['tests'][test]:
                        self.assert_(eval("len(response['"+sub_test[0][0]+"'])") < sub_test[0][1], key+": "+sub_test[1] + " len "+str(eval("len(response['"+sub_test[0][0]+"'])")))
                elif test == "parameters_error":
                    continue
                    # dealt with above!
                elif test == "contains_error":
                    sub_test = data[key]['tests'][test]                    
                    self.assert_("error" in response, key+": "+sub_test[0])
                else:
                    print "\t\t" + bcolors.FAIL + "Oh oh. I didn't know how to deal with test type: " + test + bcolors.ENDC

def run():
    suite = unittest.TestSuite()
    for method in dir(OpenTreeLib):
       if method.startswith("test"):
          suite.addTest(OpenTreeLib(method))
    unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    run()
