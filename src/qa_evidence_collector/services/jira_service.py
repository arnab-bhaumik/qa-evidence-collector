from __future__ import annotations

import base64
from pathlib import Path

import requests


class JiraService:

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _auth_header(self, email: str, token: str) -> dict:
        credentials = base64.b64encode(f"{email}:{token}".encode()).decode()
        return {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
        }

    # ------------------------------------------------------------------
    # Test connection
    # ------------------------------------------------------------------

    def test_connection(self, url: str, email: str, token: str) -> tuple[bool, str]:
        """
        Returns (success, message).
        Calls GET /rest/api/3/myself to validate credentials.
        """
        if not url or not email or not token:
            return False, "Please fill in Jira URL, Email, and API Token."

        try:
            resp = requests.get(
                f"{url.rstrip('/')}/rest/api/3/myself",
                headers=self._auth_header(email, token),
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                display_name = data.get("displayName") or data.get("name") or email
                return True, f"Connected — logged in as {display_name}"
            elif resp.status_code == 401:
                return False, "Authentication failed — check your email and API token."
            elif resp.status_code == 403:
                return False, "Access forbidden — check your API token permissions."
            elif resp.status_code == 404:
                return False, "Jira URL not found — check the URL."
            else:
                return False, f"Connection failed (HTTP {resp.status_code})."
        except requests.exceptions.ConnectionError:
            return False, "Cannot reach Jira — check the URL and your internet connection."
        except requests.exceptions.Timeout:
            return False, "Connection timed out — Jira may be slow or unreachable."
        except Exception as exc:
            return False, f"Unexpected error: {exc}"

    # ------------------------------------------------------------------
    # Upload attachment
    # ------------------------------------------------------------------

    def upload_attachment(
        self, url: str, email: str, token: str, issue_key: str, file_path: str
    ) -> tuple[bool, str]:
        """
        Attaches a file to a Jira issue.
        Returns (success, issue_url_or_error_message).
        """
        try:
            credentials = base64.b64encode(f"{email}:{token}".encode()).decode()
            headers = {
                "Authorization": f"Basic {credentials}",
                "X-Atlassian-Token": "no-check",
            }
            with open(file_path, "rb") as f:
                resp = requests.post(
                    f"{url.rstrip('/')}/rest/api/2/issue/{issue_key}/attachments",
                    headers=headers,
                    files={"file": (Path(file_path).name, f, "application/octet-stream")},
                    timeout=30,
                )
            if resp.status_code in (200, 201):
                issue_url = f"{url.rstrip('/')}/browse/{issue_key}"
                return True, issue_url
            elif resp.status_code == 401:
                return False, "Authentication failed — check your credentials in Settings."
            elif resp.status_code == 404:
                return False, f"Issue {issue_key} not found — check the issue key."
            else:
                return False, f"Upload failed (HTTP {resp.status_code})."
        except FileNotFoundError:
            return False, "Report file not found — generate the report first."
        except requests.exceptions.ConnectionError:
            return False, "Cannot reach Jira — check your internet connection."
        except requests.exceptions.Timeout:
            return False, "Upload timed out — try again."
        except Exception as exc:
            return False, f"Unexpected error: {exc}"

    # ------------------------------------------------------------------
    # Post comment
    # ------------------------------------------------------------------

    def post_comment(
        self, url: str, email: str, token: str, issue_key: str, comment: str
    ) -> tuple[bool, str]:
        """
        Posts a comment to a Jira issue activity feed.
        Returns (success, message).
        """
        try:
            resp = requests.post(
                f"{url.rstrip('/')}/rest/api/2/issue/{issue_key}/comment",
                headers=self._auth_header(email, token),
                json={"body": comment},
                timeout=15,
            )
            if resp.status_code in (200, 201):
                return True, "Comment posted."
            else:
                return False, f"Comment failed (HTTP {resp.status_code})."
        except Exception as exc:
            return False, f"Could not post comment: {exc}"
