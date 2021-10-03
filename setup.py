"""
Install bgd via setuptools
"""
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as testcommand

with open("README.md") as readme_file:
    README = readme_file.read()


# pylint: disable=import-outside-toplevel
class PyTest(testcommand):
    """PyTest class to enable running `python setup.py test`"""

    user_options = testcommand.user_options[:]
    user_options += [
        ("coverage", "C", "Produce a coverage report for bgd"),
        ("pep8", "P", "Produce a pep8 report for bgd"),
        ("pylint", "l", "Produce a pylint report for bgd"),
    ]
    coverage = None
    pep8 = None
    lint = None
    test_suite = False
    test_args = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        self.test_suite = True
        self.test_args = []
        if self.coverage:
            self.test_args.extend(["--cov", "bgd"])
        if self.pep8:
            self.test_args.append("--pep8")
        if self.lint:
            self.test_args.append("--lint")

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        # Needed in order for pytest_cache to load properly
        # Alternate fix: import pytest_cache and pass to pytest.main
        import _pytest.config
        import pytest

        plugin_manager = _pytest.config.get_plugin_manager()
        plugin_manager.consider_setuptools_entrypoints()
        sys.exit(pytest.main(self.test_args))


setup(
    name="board_game_deals",
    version="0.0.0",
    license="None",
    author="ar0ne",
    author_email="",
    url="http://github.com/ar0ne/bgd",
    description=("Best deal aggregator for board games"),
    long_description=README,
    packages=find_packages(),
    install_requires=[],  # see requirements.txt
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Programming Language :: Python",
    ],
    # test_suite="vehicle_api.tests",
    tests_require=[],  # see test_requirements.txt
    cmdclass={"test": PyTest},
    include_package_data=True,
    zip_safe=False,
)
