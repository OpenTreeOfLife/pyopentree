#! /usr/bin/env python


"""
Package setup and installation.
"""

import sys
import os

###############################################################################
# Identification

from pyopentree import __version__
# from pyopentree import __version__, revision, description
# __revision__ = revision()
# sys.stderr.write("-setup.py: {}\n".format(description()))

###############################################################################
# setuptools/distutils/etc. import and configuration

try:
    import ez_setup
    try:
        ez_setup_path = " ('" + os.path.abspath(ez_setup.__file__) + "')"
    except OSError:
        ez_setup_path = ""
    sys.stderr.write("-setup.py: using ez_setup{}\n".format(ez_setup_path))
    ez_setup.use_setuptools()
    import setuptools
    try:
        setuptools_path = " ('" +  os.path.abspath(setuptools.__file__) + "')"
    except OSError:
        setuptools_path = ""
    sys.stderr.write("-setup.py: using setuptools{}\n".format(setuptools_path))
    from setuptools import setup, find_packages
except ImportError as e:
    sys.stderr.write("-setup.py: using distutils\n")
    from distutils.core import setup
    sys.stderr.write("-setup.py: using canned package list\n")
    PACKAGES = [
            'pyopentree',
            ]
else:
    sys.stderr.write("-setup.py: searching for packages\n")
    PACKAGES = find_packages()
EXTRA_KWARGS = dict(
    install_requires = ['setuptools'],
    include_package_data = True,
    test_suite = "test.test_pyopentree",
    zip_safe = True,
    )

PACKAGE_DIRS = [p.replace(".", os.path.sep) for p in PACKAGES]
PACKAGE_INFO = [("{p[0]:>40} : {p[1]}".format(p=p)) for p in zip(PACKAGES, PACKAGE_DIRS)]
sys.stderr.write("-setup.py: packages identified:\n{}\n".format("\n".join(PACKAGE_INFO)))
ENTRY_POINTS = {}

###############################################################################
# Script paths

SCRIPT_SUBPATHS = [
    # ['scripts', 'sumtrees', 'sumtrees.py'],
    # ['scripts', 'sumtrees', 'cattrees.py'],
    # ['scripts', 'sumtrees', 'sumlabels.py'],
    # ['scripts', 'calculators', 'strict_consensus_merge.py'],
    # ['scripts', 'calculators', 'long_branch_symmdiff.py'],
]
SCRIPTS = [os.path.join(*i) for i in SCRIPT_SUBPATHS]
sys.stderr.write("\n-setup.py: scripts identified: {}\n".format(", ".join(SCRIPTS)))

###############################################################################
# setuptools/distuils command extensions

try:
    from setuptools import Command
except ImportError:
    sys.stderr.write("-setup.py: setuptools.Command could not be imported: setuptools extensions not available\n")
else:
    sys.stderr.write("-setup.py: setuptools command extensions are available\n")
    command_hook = "distutils.commands"
    ENTRY_POINTS[command_hook] = []

###############################################################################
# Main setup

### compose long description ###
long_description = open('README.md').read()
long_description = long_description.replace("PyOpenTree-x.x.x", "PyOpenTree-{}".format(__version__))
long_description = long_description.replace("""download the source code archive""",
    """`download the source code archive <http://pypi.python.org/packages/source/D/PyOpenTree/PyOpenTree-{}.tar.gz>`_""".format(__version__))

# if __revision__.is_available:
#     revision_text = " (revision: {}, {})".format(__revision__.commit_id, str(__revision__.commit_date))
# else:
#     revision_text = ""
long_description = long_description + ("""\

Current Release
===============

The current release of PyOpenTree is version {}.

""".format(__version__))

setup(name='PyOpenTree',
      version=__version__,
      author='Jeet Sukumaran and Mark T. Holder',
      author_email='jeetsukumaran@gmail.com and mtholder@ku.edu',
      url='http://packages.python.org/PyOpenTree/',
      description="Python interface and bindings for working with the Open Tree of Life services.",
      license='BSD',
      packages=PACKAGES,
      package_dir=dict(zip(PACKAGES, PACKAGE_DIRS)),
      # For some reason, following does not work in 2.5 (not tried in 2.6),
      # so this packaging is now implemented through processing of MANIFEST.in
#      package_data={
#        "" : ['doc/Makefile',
#              '/doc/source',
#              'extras'
#             ],
#        "pyopentree.test" : ["data/trees"],
#      },
      scripts = SCRIPTS,
      long_description=long_description,
      entry_points = ENTRY_POINTS,
      classifiers = [
            "Intended Audience :: Developers",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: BSD License",
            "Natural Language :: English",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.1",
            "Programming Language :: Python :: 3.2",
            "Programming Language :: Python :: 3.3",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python",
            "Topic :: Scientific/Engineering :: Bio-Informatics",
            ],
      keywords='phylogenetics phylogeny phylogenies phylogeography evolution evolutionary biology systematics coalescent population genetics phyloinformatics bioinformatics',
      **EXTRA_KWARGS
      )
