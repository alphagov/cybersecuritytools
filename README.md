# Cyber Security Tools
A collection of tools and scripts for either standalone use or
importing into other projects. Collating these small utilites and code
snippets will decrease code duplication across our projects.

# Installing
To install the as a command run.

``` sh
pip3 install git+https://github.com/alphagov/cybersecuritytools.git@#egg=cybersecuritytools
```

You might run into pip keyring issues where the above install
hangs. You can work around it by setting the following environment
variable and re running the pip command.

``` shen
export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
```

# Running

Once installed you should be able to run `cst` from anywhere.

The CLI interface is setup to have multiple sub commands. This helps
us organise multiple projects tools into a single CLI. For example:

``` sh
cst sub1 sub2 command
```

# Developing

Install (pyenv)[https://github.com/pyenv/pyenv] then install Python 3.6, 3.7, and 3.8.

Find the latest python versions
``` sh
pyenv install -l | grep '^  3.[678]..$'
```

Install the Pythons
``` sh
pyenv install 3.6.11
pyenv install 3.7.8
pyenv install 3.8.5

```

Add the shims to your environment

``` sh
pyenv global 3.8.5 3.7.8 3.6.11 system
```

Install Poetry

``` sh
pip install poetry

```

Run tests with `make test`.

# Conventions
Test files live along side the python files. They have the same name
with a suffix of `_test`.  For example if your file is
`cybersecuritytools/foo/bar.py` then the tests will be in
`cybersecuritytools/foo/bar_test.py`.

# Committing
* Add documentation for any changes you've made.
* Ensure there are tests covering your changes
* Update the [detect-secrets](https://github.com/Yelp/detect-secrets) file [`.secrets.baseline`](.secrets.baseline)
* Run `tox`, all tests, formatting, and linting must pass.
* Update the [CODEOWNERS](CODEOWNERS) file if needed.
