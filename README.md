# GitHub Workflows

A collection of GitHub workflows to use for Perl development

## Workflows

### Beta test

#### cpan-test

Runs the standard Perl testing framework

##### Inputs:

* ***perl_version*** - List of Perl versions to run the tests against
* ***os*** - List of operating systems to run the test on

*Note:* GitHub Actions currently doesn't support lists as inputs to callable workflows.
We work around this by passing a JSON list which is decoded in the workflow. You can see
the format of these lists from their default values:

* ***perl_version:*** "['5.24', '5.26', '5.28', '5.30', '5.32', '5.34', '5.36', '5.38']"
* ***os:*** "['windows-latest', 'macos-latest', 'ubuntu-latest']"

#### cpan-coverage

Checks the test coverage for your Perl code and reports the results to Coveralls.io

#### cpan-perlcritic

Runs `perlcritic` against your Perl code

##### Inputs:

* ***level***: A number from 1 to 5 defining how brutal `perlcritic` will be. The default is 5

### In early development

#### cpan-release

Releases a Perl distribution to CPAN

#### cpan-dzil-test

Runs the standard DistZilla testing framework

### Thinking about it

#### cpan-kwality

Test the "Kwality" of your Perl code

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
      build:
        uses: PerlToolsTeam/github_workflows/.github/workflows/cpan-test.yml@main

      coverage:
        uses: PerlToolsTeam/github_workflows/.github/workflows/cpan-coverage.yml@main

      perlcritic:
        uses: PerlToolsTeam/github_workflows/.github/workflows/cpan-perlcritic.yml@main

