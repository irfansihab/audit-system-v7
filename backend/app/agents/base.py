"""Helper untuk membangun agen Claude.

Pakai pola create_sdk_mcp_server + ClaudeAgentOptions dari claude-agent-sdk.
Setiap agen punya:
- system prompt yang di-load dari prompts/*.md
- daftar tools (in-process MCP server)
- allowlist tool yang sesuai peran
- model (haiku / sonnet)

DESIGN INVARIANT — agen TIDAK BOLEH memakai built-in tools (Bash/Edit/Write/
TodoWrite/Agent/Glob/Read). Hanya MCP tools yang kita ekspos lewat bridge.
Alasan: agen dalam konteks audit harus bekerja melalui pipeline V6 deterministic
dan bridge yang kita kontrol — bukan improvisasi shell/Edit ke file sistem.
"""
from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions, create_sdk_mcp_server

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def load_prompt(name: str) -> str:
    """Baca system prompt dari file markdown."""
    p = PROMPTS_DIR / f"{name}.md"
    if not p.exists():
        raise FileNotFoundError(f"Prompt tidak ditemukan: {p}")
    return p.read_text(encoding="utf-8")


def build_agent_options(
    *,
    prompt_name: str,
    tools: list,
    server_name: str = "audit-v7",
    model: str = "claude-sonnet-4-6",
    allowed_tool_names: list[str] | None = None,
) -> ClaudeAgentOptions:
    """Konstruksi ClaudeAgentOptions yang konsisten untuk semua agen.

    Returns:
        ClaudeAgentOptions siap dipakai ClaudeSDKClient.
    """
    server = create_sdk_mcp_server(name=server_name, version="0.1.0", tools=tools)

    # allowed_tool_names: format claude-agent-sdk = "mcp__{server_name}__{tool_name}"
    allowed = (
        [f"mcp__{server_name}__{n}" for n in allowed_tool_names]
        if allowed_tool_names
        else [f"mcp__{server_name}__{t.name}" for t in tools]
    )

    return ClaudeAgentOptions(
        system_prompt=load_prompt(prompt_name),
        # tools=[] mematikan SEMUA built-in (Bash, Edit, Write, Read, Glob,
        # TodoWrite, Agent, Skill, dll). Agen hanya bisa pakai MCP tools di
        # bawah supaya tidak menyentuh V6 atau filesystem lain di luar bridge.
        tools=[],
        mcp_servers={server_name: server},
        allowed_tools=allowed,
        # Defensive: walaupun tools=[] sudah mati, kita explicit-deny
        # tool-tool yang biasa dipakai agen untuk improvisasi.
        disallowed_tools=["Bash", "Edit", "Write", "Read", "TodoWrite", "Glob", "Grep", "Agent", "Skill"],
        model=model,
        # acceptEdits hanya berlaku untuk MCP tools sekarang (built-in mati).
        permission_mode="acceptEdits",
    )
