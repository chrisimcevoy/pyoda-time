"""Contains the current release version.

The __version__ attribute is updated automatically by release-please-action when it raises a pull request.
The only reason this exists is so that the labeler action knows to tag those auto-generated PRs as "release".
See also: `.github/workflows/labeler.yml`
"""

__version__ = "0.7.0"
