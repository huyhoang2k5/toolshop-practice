"""Buoi 2 - B2.13 GitHub REST API (syllabus 6.2).

Same APIRequestContext you used for Toolshop, on a different, real public API.
Fixture: github (see conftest.py). Docs: https://docs.github.com/en/rest

Rate limit: without a token GitHub allows 60 calls per hour per IP address. The whole class shares
the school's IP, so create a token (github.com > Settings > Developer settings > Fine-grained tokens,
no permissions needed) and put it in .env as GITHUB_TOKEN. Never commit .env.

Run:  pytest tests/buoi2/test_b2_github_api.py -v
"""
import uuid  # noqa: F401  (you will need it)

import pytest

pytestmark = [pytest.mark.api, pytest.mark.github]

REPO = "microsoft/playwright-python"



# ---------------------------------------------------------------- B2.13a
def test_b2_13a_github_repo_returns_expected_metadata(github):
    """Verify GitHub repository metadata."""

    response = github.get(f"/repos/{REPO}")

    # Verify HTTP status
    assert response.status == 200, response.text()

    # Read repository metadata
    data = response.json()

    assert data["full_name"] == REPO
    assert data["language"] == "Python"
    assert data["license"]["spdx_id"] == "Apache-2.0"

    assert isinstance(data["stargazers_count"], int)
    assert data["stargazers_count"] > 0

    assert data["archived"] is False




# ---------------------------------------------------------------- B2.13b
def test_b2_13b_github_unknown_user_returns_404_with_message(github):
    """Verify GitHub returns 404 for a nonexistent user."""

    # Generate a unique username
    username = f"nonexistent-{uuid.uuid4().hex}"

    # Request a user that does not exist
    response = github.get(f"/users/{username}")

    # Verify HTTP 404
    assert response.status == 404, response.text()

    # Verify error message
    data = response.json()

    assert data["message"] == "Not Found"




# ---------------------------------------------------------------- B2.13c
def test_b2_13c_github_response_reports_rate_limit(github):
    """Verify GitHub API rate-limit headers."""

    # Request rate-limit information
    response = github.get("/rate_limit")

    # Verify HTTP status
    assert response.status == 200, response.text()

    # Read response headers
    headers = response.headers

    # Verify required headers exist
    assert "x-ratelimit-limit" in headers
    assert "x-ratelimit-remaining" in headers

    # Convert header values to integers
    limit = int(headers["x-ratelimit-limit"])
    remaining = int(headers["x-ratelimit-remaining"])

    # Verify rate-limit values
    assert limit > 0
    assert remaining >= 0
    assert remaining <= limit




# ---------------------------------------------------------------- B2.13d (challenge)
def test_b2_13d_github_latest_release_matches_installed_playwright(github):
    """Verify latest GitHub release is not older than installed Playwright."""

    from importlib.metadata import version
    from packaging.version import Version

    # Get latest release from GitHub
    response = github.get(f"/repos/{REPO}/releases/latest")

    assert response.status == 200, response.text()

    # Read release tag
    data = response.json()
    tag_name = data["tag_name"]

    assert tag_name.startswith("v"), (
        f"Unexpected release tag: {tag_name}"
    )

    # Compare GitHub release with installed version
    latest_version = Version(tag_name.lstrip("v"))
    installed_version = Version(version("playwright"))

    assert latest_version >= installed_version, (
        f"GitHub release {latest_version} is older "
        f"than installed Playwright {installed_version}"
    )

