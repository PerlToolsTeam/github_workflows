# GitHub Workflows

A collection of GitHub workflows to use for Perl development

## Workflows

### Beta test

#### cpan-test

Runs the standard Perl testing framework

#### cpan-coverage

Checks the test coverage for your Perl code and reports the results to Coveralls.io

#### cpan-perlcritic

Runs `perlcritic` against your Perl code

### In early development

#### cpan-release

Releases a Perl distribution to CPAN

#### cpan-kwality

Test the "Kwality" of your Perl code

#### cpan-dzil-test

Runs the standard DistZilla testing framework

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

