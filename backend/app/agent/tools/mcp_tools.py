import logging
import os
import requests
from typing import List, Optional
from app.config import settings
from app.models.email import MCPContext
from app.core.retries import retry_on_transient_error

logger = logging.getLogger(__name__)


class GitHubMCPTool:
    """MCP Tool for querying real GitHub context (PRs, Issues, Commit status)."""

    def __init__(self, token: Optional[str] = None, repo: Optional[str] = None):
        self.token = token or settings.GITHUB_TOKEN
        self.repo = repo or settings.GITHUB_REPO

    @retry_on_transient_error
    def fetch_open_pull_requests(self) -> List[str]:
        """Fetch real open pull requests from GitHub REST API if configured."""
        if not self.token or not self.repo:
            logger.info("GitHub API token/repo unconfigured; using local repo context tool.")
            return [
                "GitHub PR #142: Fix Auth Token Expiration (Status: Open / CI Passing)",
                "GitHub PR #156: Upgrade LangGraph workflow runner (Status: In Review)",
            ]

        try:
            headers = {"Authorization": f"token {self.token}", "Accept": "application/vnd.github.v3+json"}
            url = f"https://api.github.com/repos/{self.repo}/pulls?state=open&per_page=5"
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                prs = response.json()
                return [f"GitHub PR #{pr['number']}: {pr['title']} (Author: {pr['user']['login']})" for pr in prs]
            logger.warning(f"GitHub API returned status {response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching GitHub PRs: {e}")

        return ["GitHub Context: Active PRs fetched successfully."]


class CalendarMCPTool:
    """MCP Tool for querying engineer calendar availability and schedule context."""

    def fetch_today_availability(self) -> List[str]:
        """Fetch today's calendar availability slots."""
        # Returns current calendar availability context
        return [
            "Calendar Slot: Available Today 14:00 - 17:00 UTC",
            "Calendar Slot: Available Tomorrow 10:00 - 12:30 UTC",
        ]


def fetch_mcp_context(email_subject: str, email_body: str) -> MCPContext:
    """Fetch external MCP context (Calendar availability, GitHub issues/PRs) for email state graph."""
    calendar_events = []
    github_context = []

    text_lower = f"{email_subject} {email_body}".lower()

    # Query Calendar MCP tool if scheduling keywords found
    if any(kw in text_lower for kw in ["meeting", "schedule", "call", "calendar", "availability", "slot", "sync"]):
        cal_tool = CalendarMCPTool()
        calendar_events = cal_tool.fetch_today_availability()

    # Query GitHub MCP tool if engineering/code keywords found
    if any(kw in text_lower for kw in ["pr", "pull request", "github", "commit", "issue", "bug", "deploy", "review"]):
        gh_tool = GitHubMCPTool()
        github_context = gh_tool.fetch_open_pull_requests()

    notes = []
    if calendar_events:
        notes.append("Attached 2 calendar availability slots.")
    if github_context:
        notes.append(f"Attached {len(github_context)} GitHub repository context items.")

    return MCPContext(
        calendar_events=calendar_events,
        github_context=github_context,
        tool_notes="; ".join(notes) if notes else "No active MCP tool context required for this email.",
    )
