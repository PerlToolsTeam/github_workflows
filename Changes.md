# Change Log

## Unreleased

### Fixed

- Configure MakeMaker or Module::Build distributions explicitly before
  collecting coverage, even when dependency installation leaves no build.
- Trust the checked-out workspace in the coverage container so Coveralls
  can read commit and remote metadata without dubious-ownership errors.

### Added

- Regression tests for coverage build selection, failure propagation, and
  Git metadata access in a workspace with a different owner.
