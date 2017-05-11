try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='py_compile_win_helpers',
    version='1.0.2',  # Also update in py_compile_win_helpers.py
    description='Helpers to setup the environment to compile extensions for Python',
    author='Fabio Zadrozny',
    url='https://github.com/fabioz/py_compile_win_helpers',
    py_modules=['py_compile_win_helpers'],
)

# Note: nice reference: https://jamie.curle.io/blog/my-first-experience-adding-package-pypi/
# New version: change version and then:
# git tag -a py_compile_win_helpers_1_0_2
# git push --tags
# python setup.py sdist
# python setup.py sdist upload

#
# Note: Upload may fail if ~/.pypirc is not present with username (see: https://github.com/pypa/setuptools/issues/941)
# Contents of ~/.pypirc:
#
# [distutils]
# index-servers =
#     pypi
#
# [pypi]
# repository: https://upload.pypi.org/legacy/
# username: <username>
