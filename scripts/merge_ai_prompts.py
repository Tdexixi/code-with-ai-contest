"""将 Copilot_Conversation.md 与 Cursor JSONL 导出合并为 AI_PROMPTS.md（UTF-8，无 BOM）。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COPILOT = ROOT / "Copilot_Conversation.md"
OUT = ROOT / "AI_PROMPTS.md"
JSONL_REPO = ROOT / "cursor_agent_transcript.jsonl"
# 与正文标题完全一致，避免误匹配到 JSON 等其它位置
MARKER = "## 第一部分：GitHub Copilot"
# 本机 Cursor 导出路径（与 agent-transcripts 一致）；若不存在则仅用仓库内已复制的 jsonl
JSONL_DEFAULT = Path(
    r"C:\Users\11611\.cursor\projects\e-Projects-code-with-ai-contest"
    r"\agent-transcripts\43afba9c-62bc-4b86-99ca-667b44ca3d09"
    r"\43afba9c-62bc-4b86-99ca-667b44ca3d09.jsonl"
)


def main() -> int:
    copilot_raw = COPILOT.read_text(encoding="utf-8").strip("\r\n")
    json_src = JSONL_DEFAULT if JSONL_DEFAULT.is_file() else JSONL_REPO
    if not json_src.is_file():
        print("错误：找不到 Cursor JSONL（请先复制到", JSONL_REPO, "）", file=sys.stderr)
        return 1
    jsonl_raw = json_src.read_text(encoding="utf-8").strip("\r\n")

    # 同步副本到仓库根目录，便于提交
    JSONL_REPO.write_text(jsonl_raw + "\n", encoding="utf-8", newline="\n")

    default_hdr = """# Agent 交互日志

**团队名称：** [填写你的团队名称]  
**成员名单：** [填写成员1, 成员2, 成员3]  
**使用的 AI Coding Agent 工具：** GitHub Copilot（Chat）、Cursor（内置 Agent / Composer）

---

## 交互记录导出说明

为真实反映「Code with AI」代码构建过程，本文件采用 **方式一：直接粘贴完整日志**。以下两段均为 **与源文件逐字一致** 的全文（未做概括或改写）。

- **GitHub Copilot**：正文见下栏「第一部分」代码块，内容与仓库根目录 `Copilot_Conversation.md` **完全相同**（含时间戳行、换行与标点）。为**避免正文中的 \`\`\`bash 与 Markdown 反引号围栏冲突**导致预览空白，第一部分使用 **波浪线围栏**（`~`×10），并非未写入。
- **Cursor**：正文见下栏「第二部分」代码块，为 Cursor 导出的 **JSON Lines**（每行一条 JSON）；助手消息中的 `[REDACTED]` 与导出文件一致。仓库内另有同内容副本：`cursor_agent_transcript.jsonl`。

---

"""
    if OUT.exists():
        old = OUT.read_text(encoding="utf-8", newline="\n")
        pos = old.find(MARKER)
        if pos != -1:
            hdr = old[:pos].rstrip() + "\n\n"
        else:
            hdr = default_hdr
    else:
        hdr = default_hdr

    # 使用波浪线围栏：Copilot 原文含 ```bash，若用反引号围栏会导致多数预览器把第一部分显示为空
    til = "~" * 10
    hdr = hdr + f"""## 第一部分：GitHub Copilot Chat（`Copilot_Conversation.md` 全文）

{til}copilot
"""
    mid = f"""
{til}

---

## 第二部分：Cursor Agent（JSON Lines 全文）

{til}jsonl
"""
    tail = f"""
{til}

---

*（评审组将通过日志评估团队利用 AI 解决问题和代码演进的真实度，请保证记录与仓库提交内容一致、可追溯。）*
"""
    final = hdr + copilot_raw + "\n" + mid + jsonl_raw + "\n" + tail
    OUT.write_text(final, encoding="utf-8", newline="\n")
    print("Wrote", OUT, "bytes", len(final.encode("utf-8")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
