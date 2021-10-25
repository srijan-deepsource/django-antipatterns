"""Entrypoint for the Macro. This contains the Macro logic."""
import json
import os
import subprocess

from helper import (
    make_issue,
    publish_result,
    get_files,
)

# Files that needs to be analyzed are going to be present in the CODE_PATH
CODE_PATH = os.environ.get("CODE_PATH", "/code")
RESULT_PATH = "/tmp/results.json"
APP_PATH = os.path.dirname(os.path.abspath(__file__))


def _get_issues():
    """Run semgrep rules on files and get issues."""
    issues = []

    # We would only want want to analyze Python files.
    files_to_analyze = [filename for filename in get_files(CODE_PATH) if filename.endswith(".py")]

    # Command to invoke `semgrep` with our custom rules
    analysis_command = [
        "/toolbox/venv/bin/semgrep",
        "--json",
        "-o",
        RESULT_PATH,
        # Load the rules config
        "-f",
        os.path.join(APP_PATH, "semgrep-django-rules")
    ]

    # Early exit, if there's nothing to analyze.
    if not files_to_analyze:
        return issues

    # There are files to analyze
    subprocess.run(analysis_command + files_to_analyze)

    # Read the result json, convert it to DeepSource issue format.
    with open(RESULT_PATH) as fp:
        raised_issues = json.load(fp)["results"]
    for issue in raised_issues:
        issue_code = issue["check_id"].split("::")[-1]
        issue_text = issue["extra"]["message"]
        filepath = issue["path"]
        startline = issue["start"]["line"]
        startcol = issue["start"]["col"]
        endline = issue["end"]["line"]
        endcol = issue["end"]["col"]
        issues.append(
            make_issue(
                issue_code, issue_text, filepath, startline, startcol, endline, endcol
            )
        )

    return issues

issues = _get_issues()

# Publish result on DeepSource
publish_result(issues)
