import os  # noqa: F401

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

version = '0.1.1'

# If a tagged commit, don't make a pre-release
if 'CI_COMMIT_TAG' not in os.environ:
    version = f"{ version }.dev{ os.getenv('CI_PIPELINE_ID') or None }"

setup(
    name="flask-request-id-header",
    version=version,
    author="British Antarctic Survey",
    author_email="webapps@bas.ac.uk",
    description="Python Flask middleware to ensure all requests have a request ID header",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/antarctica/flask-request-id-header",
    license='Open Government Licence v3.0',
    install_requires=['flask'],
    packages=find_packages(exclude=['tests']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Flask",
        "Development Status :: 5 - Production/Stable",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers"
    ],
)
