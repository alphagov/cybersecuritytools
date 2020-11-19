import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gds_json_logger",
    version="0.0.1",
    author="GDS Cyber Security",
    author_email="cyber.security@digital.cabinet-office.gov.uk",
    description="Create a logger which outputs JSON",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alphagov/cybersecuritytools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)