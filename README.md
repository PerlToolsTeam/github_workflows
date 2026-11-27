# GitHub Workflows

A collection of GitHub workflows to use for Perl development

## Workflows

### Beta test

These workflows seem to work as expected. There probably won't be any major changes
to them (but there will, almost certainly, be new features and bug fixes).

#### cpan-test

Runs the standard Perl testing framework

##### Inputs:

* ***perl_version*** - List of Perl versions to run the tests against
* ***os*** - List of operating systems to run the test on

*Note:* GitHub Actions currently doesn't support lists as inputs to callable workflows.
We work around this by passing a string containing a JSON-encoded list which is decoded
in the workflow. You can see the format of these lists from their default values:

* ***perl_version:*** "['5.24', '5.26', '5.28', '5.30', '5.32', '5.34', '5.36', '5.38','5.40','5.42']"
* ***os:*** "['windows-latest', 'macos-latest', 'ubuntu-latest']"

*Note:* The `cpan-test` workflow now includes configure steps to run `perl Build.PL` if `Build.PL` exists, and `perl Makefile.PL` if `Makefile.PL` exists, before running `prove`.

##### Todo

* A way to install other CPAN modules (ones that, for some reason, aren't in the prereqs)
* A way to install other required software

#### cpan-coverage

Checks the test coverage for your Perl code and reports the results to Coveralls.io

The workflow installs dependencies, including configure requirements, then
configures the distribution explicitly before running
`cover -test -report Coveralls`. It uses `Build.PL` when present, otherwise
`Makefile.PL`, matching
Devel::Cover's preference for a generated `Build` script. A missing build
definition or a failed configure step fails the job. Devel::Cover builds and
runs the tests under instrumentation; non-zero coverage exits remain failures.

The container job trusts only the checked-out workspace via Git's
`safe.directory` setting in the job's global configuration. This lets the
Coveralls reporter read commit and remote metadata when the container user
differs from the checkout owner. The reporter continues using the job's
`GITHUB_TOKEN`.

##### Todo

* Report to coverage tools other than coveralls.io
* Make reporting to a web site optional

#### cpan-perlcritic

Runs `perlcritic` against your Perl code

##### Inputs:

* ***level***: A number from 1 to 5 defining how brutal `perlcritic` will be. The default is 5

#### yaml-lint

Lints YAML files using `yamllint` to ensure they follow best practices and are properly formatted

### In early development

These workflows aren't guaranteed to do what they need to yet. They'll probably change quickly
over the coming weeks, so maybe don't use them just yet.

#### cpan-release

Releases a Perl distribution to CPAN

#### cpan-dzil-test

Runs the standard DistZilla testing framework

### Thinking about it

All bets are off with these workflows. I mean, you can try them but I'm giving no
guarantees whatsoever.

#### cpan-kwality

Test the "Kwality" of your Perl code

#### cpan-complexity

Report on the cyclomatic complexity of your code

## Using the workflows

These workflows have all been written so that you can simply refer to
them from within your own workflows. For example, a simple workflow that
runs the CPAN test, coverage and `perlcritic` workflows would look like this:

    name: CI

    on:
      push:
        branches: [ main ]
      pull_request:
        branches: [ main ]
      workflow_dispatch:

    jobs:
      test:
        uses: PerlToolsTeam/github_workflows/.github/workflows/cpan-test.yml@main

      coverage:
        uses: PerlToolsTeam/github_workflows/.github/workflows/cpan-coverage.yml@main

      perlcritic:
        uses: PerlToolsTeam/github_workflows/.github/workflows/cpan-perlcritic.yml@main

## Developing the coverage workflow

The regression tests execute the workflow's shell steps with temporary
distribution fixtures. They cover both builders, failed configuration,
coverage failures, paths containing spaces, and Git's ownership checks.
Dependency installation and report submission use local stand-ins, so these
tests do not install Perl modules or contact Coveralls. Real integration
validation should also run this workflow from a consumer distribution and
confirm that tests execute and a non-empty report is submitted.

Run them with Python 3, Perl, Git, and a POSIX shell available:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-test.txt
.venv/bin/python -m unittest discover -s tests -v
```

The repository's CI runs these tests alongside YAML linting. Release changes
are recorded in [Changes.md](Changes.md).

