"""Agen Ketua Tim — susun draft LHR dari temuan.json."""
from claude_agent_sdk import ClaudeAgentOptions

from app.agents.base import build_agent_options
from app.tools.feedback_tools import FEEDBACK_TOOLS
from app.tools.lhr_tools import LHR_TOOLS
from app.tools.wiki_tools import WIKI_TOOLS


def build_ketua_tim_agent() -> ClaudeAgentOptions:
    return build_agent_options(
        prompt_name="ketua_tim",
        tools=LHR_TOOLS + WIKI_TOOLS + FEEDBACK_TOOLS,
        server_name="kt",
        model="claude-sonnet-4-6",
    )
