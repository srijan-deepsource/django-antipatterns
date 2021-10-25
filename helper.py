"""
Helper functions for writing the Macro.

This would be a part of our upcoming Macros SDK.
"""

import json
import tempfile
import os
import subprocess


def publish_result(issues, metrics=None, errors=None):
    """Publish the analysis results."""
    result = {
        "issues": issues,
        "metrics": metrics or [],
        "is_passed": bool(issues),
        "errors": errors  or [],
        "extra_data": ""
    }

    # write results into a json file:
    res_file = tempfile.NamedTemporaryFile().name
    with open(res_file, "w") as fp:
        fp.write(json.dumps(result))

    # publish result:
    subprocess.run(["/toolbox/marvin", "--publish-report", res_file])


def get_vcs_filepath(filepath):
    """Remove the /code/ prefix."""
    if filepath.startswith("/code/"):
        filepath = filepath[6:]

    return filepath


def make_issue(issue_code, issue_txt, filepath, line, col, endline=None, endcol=None):
    """Prepare issue structure for the given issue data."""
    filepath = get_vcs_filepath(filepath)
    return {
        "issue_code": issue_code,
        "issue_text": issue_txt,
        "location": {
            "path": filepath,
            "position": {
                "begin": {
                    "line": line,
                    "column": col
                },
                "end": {
                    "line": endline or line,
                    "column": endcol or col
                }
            }
        }
    }


def get_files(base_dir):
    """Return a generator with filepaths in base_dir."""
    for subdir, _, filenames in os.walk(base_dir):
        for filename in filenames:
            filepath = os.path.join(subdir, filename)
            yield filepath
