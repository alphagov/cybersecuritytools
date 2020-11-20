import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gds_flask_auth",
    version="0.0.1",
    author="GDS Cyber Security",
    author_email="cyber.security@digital.cabinet-office.gov.uk",
    description="Authentication decorators and helpers for flask apps",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alphagov/cybersecuritytools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "flask",
        "serverless_wsgi",
        "pyjwt",
        "requests",
        "jsonlogger @ git+https://github.com/alphagov/cybersecuritytools.git@authed-tech-docs#egg=jsonlogger&subdirectory=cybersecuritytools/jsonlogger"
    ],
    python_requires=">=3.6",
)