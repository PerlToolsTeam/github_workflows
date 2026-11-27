"""Exercise the coverage workflow's actual shell steps with local fixtures."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = yaml.safe_load(
    (ROOT / ".github/workflows/cpan-coverage.yml").read_text()
)
STEPS = WORKFLOW["jobs"]["coverage"]["steps"]


class CoverageWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="coverage workflow ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.workspace = self.root / "distribution with spaces"
        self.workspace.mkdir()
        binaries = self.root / "bin"
        binaries.mkdir()
        for name, body in {
            # Installing dependencies need not leave a configured build behind.
            "cpanm": "exit 0\n",
            "cover": (
                'if [ -n "${FIXTURE_COVER_STATUS:-}" ]; then\n'
                '  exit "$FIXTURE_COVER_STATUS"\n'
                "fi\n"
                "if [ ! -f Build ] && [ ! -f Makefile ]; then\n"
                '  echo "No configured build" >&2\n'
                "  exit 17\n"
                "fi\n"
                ": > coverage-ran\n"
            ),
        }.items():
            executable = binaries / name
            executable.write_text("#!/bin/sh\n" + body)
            executable.chmod(0o755)
        self.environment = {
            **os.environ,
            "PATH": str(binaries) + os.pathsep + os.environ["PATH"],
            "GITHUB_WORKSPACE": str(self.workspace),
            # Isolate configuration without changing the caller's HOME.
            "GIT_CONFIG_GLOBAL": str(self.root / "global.gitconfig"),
            "GIT_CONFIG_NOSYSTEM": "1",
        }

    def configure_fixture(self, filename, output):
        (self.workspace / filename).write_text(
            "open my $file, '>', '" + output + "' or die $!;\n"
            'print $file "configured\\n";\n'
            "close $file or die $!;\n"
        )

    def run_workflow(self):
        output = []
        for step in STEPS:
            if "run" not in step:
                continue
            result = subprocess.run(
                ["sh", "-e", "-c", step["run"]],
                cwd=self.workspace,
                env=self.environment,
                text=True,
                capture_output=True,
            )
            output.append(result.stdout + result.stderr)
            if result.returncode:
                return result.returncode, "\n".join(output)
        return 0, "\n".join(output)

    def assert_coverage_runs(self):
        status, output = self.run_workflow()
        self.assertEqual(status, 0, output)
        self.assertTrue((self.workspace / "coverage-ran").exists())

    def test_configures_makemaker_before_coverage(self):
        self.configure_fixture("Makefile.PL", "Makefile")
        self.assert_coverage_runs()
        self.assertEqual((self.workspace / "Makefile").read_text(), "configured\n")

    def test_configures_module_build_before_coverage(self):
        self.configure_fixture("Build.PL", "Build")
        self.assert_coverage_runs()
        self.assertEqual((self.workspace / "Build").read_text(), "configured\n")

    def test_prefers_module_build_when_both_builders_exist(self):
        self.configure_fixture("Makefile.PL", "Makefile")
        self.configure_fixture("Build.PL", "Build")
        self.assert_coverage_runs()
        self.assertFalse((self.workspace / "Makefile").exists())

    def test_makemaker_configuration_failure_is_not_hidden(self):
        (self.workspace / "Makefile.PL").write_text("exit 7;\n")
        status, output = self.run_workflow()
        self.assertEqual(status, 7, output)
        self.assertFalse((self.workspace / "coverage-ran").exists())

    def test_module_build_failure_does_not_fall_back_to_makemaker(self):
        self.configure_fixture("Makefile.PL", "Makefile")
        (self.workspace / "Build.PL").write_text("exit 9;\n")
        status, output = self.run_workflow()
        self.assertEqual(status, 9, output)
        self.assertFalse((self.workspace / "Makefile").exists())
        self.assertFalse((self.workspace / "coverage-ran").exists())

    def test_missing_build_definition_fails_clearly(self):
        status, output = self.run_workflow()
        self.assertNotEqual(status, 0)
        self.assertIn("Build.PL", output)
        self.assertIn("Makefile.PL", output)
        self.assertFalse((self.workspace / "coverage-ran").exists())

    def test_coverage_failure_is_not_hidden(self):
        self.configure_fixture("Makefile.PL", "Makefile")
        self.environment["FIXTURE_COVER_STATUS"] = "23"
        status, output = self.run_workflow()
        self.assertEqual(status, 23, output)

    def test_git_metadata_is_readable_with_different_workspace_owner(self):
        self.configure_fixture("Makefile.PL", "Makefile")
        (self.workspace / "Makefile").write_text("already configured\n")
        git = ["git", "-C", str(self.workspace)]
        for args in [
            ["init", "--quiet"],
            ["add", "Makefile.PL"],
            [
                "-c", "user.name=Coverage fixture",
                "-c", "user.email=coverage@example.invalid",
                "-c", "commit.gpgsign=false",
                "-c", "core.hooksPath=/dev/null",
                "commit", "--quiet", "-m", "Fixture commit",
            ],
            ["remote", "add", "origin", "https://example.invalid/coverage.git"],
        ]:
            subprocess.run(
                git + args, env=self.environment, check=True, capture_output=True
            )
        self.environment["GIT_TEST_ASSUME_DIFFERENT_OWNER"] = "1"
        before = subprocess.run(
            git + ["log", "-1"], env=self.environment, text=True, capture_output=True
        )
        self.assertNotEqual(before.returncode, 0)
        self.assertIn("dubious ownership", before.stderr)

        self.assert_coverage_runs()
        for args, expected in [
            (["log", "-1", "--format=%s"], "Fixture commit"),
            (["remote", "get-url", "origin"], "https://example.invalid/coverage.git"),
            (["config", "--global", "--get-all", "safe.directory"], str(self.workspace)),
        ]:
            result = subprocess.run(
                git + args, env=self.environment, text=True, capture_output=True
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), expected)
            self.assertNotIn("dubious ownership", result.stderr)


if __name__ == "__main__":
    unittest.main()
