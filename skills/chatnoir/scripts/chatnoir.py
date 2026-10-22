#!/usr/bin/env python3
"""ChatNoir: local evidence helpers. PDF export optionally requires ReportLab."""

from __future__ import annotations

import argparse
import ast
from bisect import bisect_left
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import runpy
import shlex
import stat
import string
import subprocess
import sys
from urllib.parse import quote

VERSION = "0.3.0"
FORMAT = "chatnoir.report/v1"
MAX_FILE = 1024 * 1024
MAX_TOTAL = 64 * 1024 * 1024
MAX_FILES = 20000
EXCLUDED = {".git", ".hg", ".svn", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".next", "vendor", ".chatnoir"}
SUFFIXES = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
SENSITIVE = re.compile(r"(^|/)(\.env(?:\..*)?|id_rsa|id_ed25519|credentials(?:\..*)?)$|\.(pem|key|p12|pfx)$", re.I)
RULES = {
    "CN001": ("Dynamic code evaluation", "CWE-95", "Use a data parser or an explicit operation allowlist instead of evaluating input."),
    "CN002": ("Shell command execution", "CWE-78", "Use an argument array with shell disabled; validate executable and options."),
    "CN003": ("Unsafe object deserialization", "CWE-502", "Use a data-only format and validate the decoded schema."),
    "CN004": ("Dynamically constructed SQL", "CWE-89", "Bind data as query parameters; allowlist identifiers separately."),
    "CN005": ("TLS certificate verification disabled", "CWE-295", "Enable certificate verification and configure the intended trust store."),
    "CN006": ("Dynamic content in a privileged prompt role", "CWE-1427", "Keep retrieved/user/tool content out of system/developer roles; enforce tool authorization independently of model output."),
    "CN007": ("Decoded data passed directly to an action dispatcher", "CWE-862", "Validate proposal shape and authorize the action against caller-owned capabilities before dispatch; decoded data cannot grant permission."),
    "CN008": ("Message-provided permissions merged into authority", "CWE-807", "Derive permissions from the trusted root task; never widen authority from a peer message's claimed capabilities."),
}


class ChatNoirError(Exception):
    pass


FIRST_REVIEW_SCOPES = {
    "auth": "Authentication: how identities and sessions are established and checked",
    "data": "Data access: whether one user can read or change another user's resources",
    "agents": "Agent permissions: whether retrieved text, tool outputs or peer messages can authorize actions",
}


def first_review(root: Path, focus: str | None) -> dict:
    """Prepare a source-review handoff; inventory is not a vulnerability verdict."""
    skill = Path(__file__).resolve().parents[1]
    required = ["SKILL.md", "references/first-review.md", "references/review.md",
                "references/report.md", "references/evidence.md", "references/remediation.md"]
    if focus == "agents":
        required.append("references/agent-security.md")
    if any(not (skill / name).is_file() for name in required):
        raise ChatNoirError("incomplete skill installation; restore the full ChatNoir skill directory")
    if focus is not None and focus not in FIRST_REVIEW_SCOPES:
        raise ChatNoirError("choose auth, data or agents")
    target, _ = collect(root)
    if not target["files"]:
        raise ChatNoirError("inventory includes no readable files; " + target["inventory_strategy"] +
                           "; inspect exclusions with inventory or use an explicitly scoped manual source review without helper identity")
    prompt = None
    if focus:
        prompt = (f"Use ChatNoir's guided first review on {json.dumps(str(root), ensure_ascii=True)}. "
                  f"Focus: {FIRST_REVIEW_SCOPES[focus]}. Keep this review read-only. "
                  "Inspect a bounded source path from entrypoint through enforcement to the sensitive operation; "
                  "scanner candidates need evidence. Do not run target code or install dependencies. "
                  "Summarize confirmed findings, unresolved candidates, dismissals, and what was not tested. "
                  "Show the smallest next action; do not apply a fix unless requested.")
    return {"version": VERSION, "skill": str(skill), "python": sys.version.split()[0],
            "target": str(root), "inventory": target, "focus": focus,
            "state": "ready_for_source_review" if focus else "choose_scope",
            "host_access": "not_checked", "review_performed": False, "review_request": prompt}


def render_first_review(plan: dict) -> str:
    # JSON quoting keeps control characters in filesystem names inert in output.
    quoted = lambda value: json.dumps(value, ensure_ascii=True)
    inventory = plan["inventory"]
    lines = ["ChatNoir first review", "",
             f"Local setup: ChatNoir {plan['version']} | Python {plan['python']}",
             f"Skill directory: {quoted(plan['skill'])}", f"Target: {quoted(plan['target'])}",
             f"Inventory: {len(inventory['files'])} readable files; {len(inventory['skipped'])} skipped.",
             f"Included-file snapshot: {inventory['snapshot_sha256']}",
             f"Git revision: {inventory['git_head'] or 'unavailable (Git is optional)'}",
             f"Working tree dirty: {inventory['dirty'] if inventory['dirty'] is not None else 'unknown'}"]
    if inventory["dirty_reason"]:
        lines.append(inventory["dirty_reason"])
    lines += ["", "No vulnerability review or runtime tests have run. Host/model access was not checked.",
              "Inventory exclusions and file hashes are available through the inventory command.", ""]
    if plan["focus"] is None:
        lines += ["Choose one scope:"] + [f"  {key}: {value}" for key, value in FIRST_REVIEW_SCOPES.items()]
        lines += ["", "Then rerun with --focus auth, --focus data, or --focus agents. For example:",
                  shlex.join([sys.executable, str(Path(plan["skill"]) / "scripts/chatnoir.py"),
                              "first-review", plan["target"], "--focus", "data"])]
    else:
        lines += [f"Scope: {FIRST_REVIEW_SCOPES[plan['focus']]}", "",
                  "Local setup is ready. Paste this request into your coding agent with ChatNoir loaded:",
                  "", plan["review_request"], "",
                  "If the host cannot load ChatNoir or call its model, report that blocker; do not claim a review."]
    return "\n".join(lines) + "\n"


def git(root: Path, *args: str) -> bytes:
    """Use fixed caller operations; disable pager and filesystem-monitor execution."""
    return subprocess.run(["git", "--no-pager", "-c", "core.fsmonitor=false", "-C", str(root), *args],
                          check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          timeout=30).stdout


def git_root(root: Path) -> Path | None:
    try:
        return Path(os.fsdecode(git(root, "rev-parse", "--show-toplevel")).strip()).resolve()
    except (OSError, subprocess.SubprocessError):
        return None


def dirty_state(root: Path) -> tuple[bool | None, str | None]:
    # Even `git status` can run clean/process filters while comparing content.
    # Inspect effective configuration without executing the configured programs.
    try:
        filters = git(root, "config", "--null", "--name-only", "--get-regexp", r"^filter\..*\.(clean|process)$")
    except subprocess.CalledProcessError as error:
        if error.returncode != 1:  # 1 means no matching configuration keys.
            raise
        filters = b""
    if filters:
        return None, "not checked: Git clean/process filters are configured"
    # Submodule content is outside this inventory; do not invoke its own filters.
    return bool(git(root, "status", "--porcelain", "--untracked-files=normal", "--ignore-submodules=all", "--", ".")), None


def safe_relative(value: str) -> bool:
    p = PurePosixPath(value)
    return bool(value) and not p.is_absolute() and ".." not in p.parts and "\\" not in value and not re.match(r"^[A-Za-z]:", value)


def read_source(root: Path, rel: str) -> bytes:
    if not safe_relative(rel):
        raise ChatNoirError("unsafe relative path")
    path = root / rel
    # Refuse linked components, not just final-file symlinks.
    current = root
    for part in PurePosixPath(rel).parts:
        current = current / part
        if current.is_symlink():
            raise ChatNoirError("symlink")
    if not path.resolve().is_relative_to(root):
        raise ChatNoirError("outside target")
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise ChatNoirError("not a regular file")
        if info.st_size > MAX_FILE:
            raise ChatNoirError("file size limit")
        data = stream.read(MAX_FILE + 1)
        if len(data) > MAX_FILE:
            raise ChatNoirError("file size limit")
        return data


def paths(root: Path) -> tuple[list[str], str]:
    top = git_root(root)
    if top:
        data = git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z", "--", ".")
        result = sorted(set(os.fsdecode(p) for p in data.split(b"\0") if p))
        strategy = "git tracked and untracked, honoring Git ignores for untracked files"
    else:
        result = []
        for directory, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d not in EXCLUDED and not (Path(directory) / d).is_symlink())
            result.extend((Path(directory) / f).relative_to(root).as_posix() for f in sorted(files))
            if len(result) > MAX_FILES:
                raise ChatNoirError("file count limit; select a narrower target")
        result.sort()
        strategy = "directory walk; Git ignore rules unavailable"
    if len(result) > MAX_FILES:
        raise ChatNoirError("file count limit; select a narrower target")
    return result, strategy


def collect(root: Path) -> tuple[dict, dict[str, bytes]]:
    if not root.is_dir():
        raise ChatNoirError("target must be a directory")
    names, strategy = paths(root)
    files, skipped, blobs = [], [], {}
    total = 0
    for rel in names:
        if any(part in EXCLUDED for part in PurePosixPath(rel).parts):
            skipped.append({"path": rel, "reason": "excluded directory"})
            continue
        if SENSITIVE.search(rel):
            skipped.append({"path": rel, "reason": "credential file excluded"})
            continue
        try:
            data = read_source(root, rel)
            total += len(data)
            if total > MAX_TOTAL:
                raise ChatNoirError("total byte limit; select a narrower target")
            if b"\0" in data:
                raise ChatNoirError("binary file")
            data.decode("utf-8")
        except (OSError, UnicodeError, ChatNoirError) as error:
            # Avoid echoing exception messages containing absolute paths or data.
            if isinstance(error, ChatNoirError) and str(error).startswith("total byte"):
                raise
            reason = str(error) if isinstance(error, ChatNoirError) else type(error).__name__
            skipped.append({"path": rel, "reason": reason})
            continue
        digest = hashlib.sha256(data).hexdigest()
        files.append({"path": rel, "sha256": digest, "bytes": len(data)})
        blobs[rel] = data
    identity = hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=True).encode()).hexdigest()
    head, dirty, dirty_reason = None, None, None
    if git_root(root):
        try:
            head = git(root, "rev-parse", "--verify", "HEAD").decode().strip()
            dirty, dirty_reason = dirty_state(root)
        except (OSError, subprocess.SubprocessError):
            dirty_reason = "Git state unavailable"
    return {"snapshot_sha256": identity, "git_head": head, "dirty": dirty, "dirty_reason": dirty_reason,
            "inventory_strategy": strategy, "files": files, "skipped": skipped}, blobs


def dotted(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = dotted(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return ""


def candidate(rule: str, path: str, line: int, detail: str) -> dict:
    title, cwe, remediation = RULES[rule]
    identity = f"{rule}:{path}:{line}"
    return {"id": "CN-" + hashlib.sha256(identity.encode()).hexdigest()[:12],
            "rule_id": rule, "title": title, "cwe": cwe, "path": path, "line": line,
            "status": "candidate", "severity": "unknown", "confidence": "low",
            "evidence": [detail], "attack_path": [], "counterevidence": [],
            "proof_gaps": ["Establish input provenance, runtime reachability and effective controls."],
            "remediation": remediation, "validation": {"method": "not_run", "result": "Not validated"}}


def python_candidates(path: str, text: str) -> list[dict]:
    tree = ast.parse(text, filename=path)
    parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
    # Index statement locations once. Repeated unresolved prompt/action names
    # must not rescan all preceding siblings for every candidate.
    locations = {}
    for parent in ast.walk(tree):
        for _, value in ast.iter_fields(parent):
            if isinstance(value, list):
                for index, child in enumerate(value):
                    if isinstance(child, ast.stmt):
                        locations[child] = (value, index)
    block_writes = {}
    aliases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for item in node.names:
                aliases[item.asname or item.name.split(".")[0]] = item.name if item.asname else item.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom) and node.module:
            for item in node.names:
                aliases[item.asname or item.name] = f"{node.module}.{item.name}"

    def resolve(node: ast.AST) -> str:
        name = dotted(node)
        first, dot, rest = name.partition(".")
        return aliases.get(first, first) + (dot + rest if dot else "")

    def local_value(expression: ast.AST, use: ast.AST, seen: frozenset = frozenset()) -> ast.AST:
        """Follow prior straight-line bindings in the same statement block only.

        This intentionally does not claim branch, closure or interprocedural flow.
        A local query must not inherit an unrelated function's similarly named value.
        """
        if not isinstance(expression, ast.Name) or expression.id in seen:
            return expression
        statement = use
        while statement not in locations and statement in parents:
            statement = parents[statement]
        if statement not in locations:
            return expression
        block, index = locations[statement]
        key = id(block)
        if key not in block_writes:
            writes = {}
            for position, previous in enumerate(block):
                for name in {n.id for n in ast.walk(previous)
                             if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}:
                    writes.setdefault(name, []).append((position, previous))
            block_writes[key] = writes
        events = block_writes[key].get(expression.id, [])
        previous_index = bisect_left(events, index, key=lambda item: item[0]) - 1
        if previous_index < 0:
            return expression
        previous = events[previous_index][1]
        targets = previous.targets if isinstance(previous, ast.Assign) else [previous.target] if isinstance(previous, (ast.AnnAssign, ast.AugAssign)) else []
        if any(isinstance(target, ast.Name) and target.id == expression.id for target in targets):
            if isinstance(previous, ast.AugAssign):
                return previous  # unsupported compound updates remain unresolved
            value = previous.value
            return local_value(value, previous, seen | {expression.id}) if value else expression
        # A nested/control-flow write is a barrier, not an older direct binding.
        return expression

    permission_fields = {"capabilities", "permissions", "scopes", "allowed_tools", "allowed_actions"}

    def permission_input(expression: ast.AST, use: ast.AST) -> bool:
        value = local_value(expression, use)
        return (isinstance(value, ast.Subscript) and isinstance(value.slice, ast.Constant)
                and isinstance(value.slice.value, str) and value.slice.value in permission_fields)

    def permission_target(expression: ast.AST) -> bool:
        return bool(re.search(r"(?:^|_)(?:capabilities|permissions|scopes|allowed_tools|allowed_actions)$",
                              dotted(expression).rsplit(".", 1)[-1]))

    result = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            fields = {key.value: value for key, value in zip(node.keys, node.values)
                      if isinstance(key, ast.Constant) and isinstance(key.value, str)}
            role = fields.get("role")
            if (isinstance(role, ast.Constant) and role.value in ("system", "developer")
                    and "content" in fields and not isinstance(local_value(fields["content"], node), ast.Constant)):
                result.append(candidate("CN006", path, node.lineno,
                                        "AST matched dynamic content with a literal privileged role; provenance and actual prompt use require review."))
        if (isinstance(node, ast.AugAssign) and isinstance(node.op, ast.BitOr)
                and permission_target(node.target) and permission_input(node.value, node)):
            result.append(candidate("CN008", path, node.lineno,
                                    "AST matched permission-container union with subscripted permission input; trust boundary requires review."))
        if not isinstance(node, ast.Call):
            continue
        name = resolve(node.func)
        kwargs = {kw.arg: kw.value for kw in node.keywords if kw.arg}
        rule = None
        if name in {"eval", "exec", "builtins.eval", "builtins.exec"}:
            rule = "CN001"
        elif name in {"os.system", "os.popen", "subprocess.getoutput", "subprocess.getstatusoutput"}:
            rule = "CN002"
        elif name.startswith("subprocess.") and isinstance(kwargs.get("shell"), ast.Constant) and kwargs["shell"].value is True:
            rule = "CN002"
        elif name in {"pickle.load", "pickle.loads", "dill.load", "dill.loads", "marshal.load", "marshal.loads", "yaml.unsafe_load", "yaml.unsafe_load_all"}:
            rule = "CN003"
        elif name in {"yaml.load", "yaml.load_all"}:
            loader = kwargs.get("Loader") or (node.args[1] if len(node.args) > 1 else None)
            if loader is None or resolve(loader) not in {"yaml.SafeLoader", "yaml.CSafeLoader"}:
                rule = "CN003"
        elif name.rsplit(".", 1)[-1] in {"execute", "executemany", "executescript"} and node.args and isinstance(local_value(node.args[0], node), (ast.JoinedStr, ast.BinOp, ast.Call)):
            rule = "CN004"
        elif isinstance(kwargs.get("verify"), ast.Constant) and kwargs["verify"].value is False and name.startswith(("requests.", "httpx.")):
            rule = "CN005"
        elif name.rsplit(".", 1)[-1] in {"execute_action", "dispatch_action", "execute_tool", "call_tool", "dispatch"} and any(
                isinstance(value := local_value(arg, node), ast.Call) and resolve(value.func) == "json.loads"
                for arg in [*node.args, *kwargs.values()]):
            rule = "CN007"
        elif (isinstance(node.func, ast.Attribute) and node.func.attr in {"update", "union"}
              and permission_target(node.func.value) and any(permission_input(arg, node) for arg in node.args)):
            rule = "CN008"
        if rule:
            result.append(candidate(rule, path, node.lineno, f"AST matched {name} call; source values omitted."))
    return sorted(result, key=lambda item: (item["line"], item["rule_id"]))


def baseline(root: Path) -> dict:
    target, blobs = collect(root)
    findings, reviewed, deferred = [], [], []
    for path, data in blobs.items():
        suffix = Path(path).suffix.lower()
        if suffix not in SUFFIXES:
            deferred.append({"path": path, "reason": "no baseline rules for this file type"})
            continue
        text = data.decode("utf-8-sig")
        if suffix == ".py":
            try:
                findings.extend(python_candidates(path, text))
            except (SyntaxError, RecursionError, ValueError, MemoryError):
                deferred.append({"path": path, "reason": "Python AST parse failed"})
                continue
        else:
            # A lexical lead, not a JS parser or data-flow analysis.
            for line, source in enumerate(text.splitlines(), 1):
                if re.search(r"\b(?:eval|new\s+Function)\s*\(", source):
                    findings.append(candidate("CN001", path, line, "Lexical dynamic-evaluation pattern; may be a comment, string or unreachable code."))
            deferred.append({"path": path, "reason": "JS/TS lexical check only; semantic review required"})
        reviewed.append(path)
    return {"format": FORMAT, "version": VERSION, "mode": "baseline", "target": target,
            "coverage": {"complete": False, "reviewed": reviewed, "deferred": deferred,
                         "limitations": ["Eight heuristic rule families; not a complete security audit.",
                                         "No taint, dependency, credential-content or runtime analysis.",
                                         "Absence of candidates does not establish safety.",
                                         "Snapshot identifies included readable files, not excluded content or an atomic filesystem snapshot."]},
            "findings": findings}


def exact_diff(root: Path, base: str, head: str) -> dict:
    if not git_root(root):
        raise ChatNoirError("diff requires a Git repository")
    def revision(ref: str) -> str:
        if not ref or ref.startswith("-"):
            raise ChatNoirError("invalid revision")
        return git(root, "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}").decode().strip()
    before, after = revision(base), revision(head)
    patch = git(root, "diff", "--no-ext-diff", "--no-textconv", "--binary", before, after, "--", ".")
    names = git(root, "diff", "--no-ext-diff", "--no-textconv", "--name-status", "--no-renames", "-z", before, after, "--", ".").split(b"\0")
    files = [{"status": os.fsdecode(names[i]), "path": os.fsdecode(names[i + 1])} for i in range(0, len(names) - 1, 2)]
    return {"format": "chatnoir.diff/v1", "base": before, "head": after,
            "patch_sha256": hashlib.sha256(patch).hexdigest(), "files": files,
            "note": "Committed comparison only; working-tree changes are not included. Read deleted files at base."}


def validate_report(report: dict) -> None:
    def require(condition: bool, message: str) -> None:
        if not condition:
            raise ChatNoirError(message)
    require(isinstance(report, dict) and report.get("format") == FORMAT, "unsupported report format")
    require(report.get("mode") in {"baseline", "repository", "diff", "deep", "triage", "verify"}, "invalid mode")
    require(isinstance(report.get("version"), str) and bool(report["version"]), "missing report version")
    if "executive_summary" in report:
        require(isinstance(report["executive_summary"], str) and bool(report["executive_summary"].strip()),
                "executive_summary must be nonempty review-authored text")
    target, coverage, findings = report.get("target"), report.get("coverage"), report.get("findings")
    require(isinstance(target, dict) and bool(re.fullmatch(r"[a-f0-9]{64}", str(target.get("snapshot_sha256", "")))), "missing snapshot digest")
    require(isinstance(coverage, dict) and type(coverage.get("complete")) is bool, "missing coverage state")
    require(isinstance(target.get("files"), list) and isinstance(target.get("skipped"), list), "missing target inventory")
    for item in target["files"]:
        require(isinstance(item, dict) and isinstance(item.get("path"), str) and safe_relative(item["path"]) and
                bool(re.fullmatch(r"[a-f0-9]{64}", str(item.get("sha256", "")))) and
                type(item.get("bytes")) is int and item["bytes"] >= 0, "invalid inventory entry")
    require(len({x["path"] for x in target["files"]}) == len(target["files"]), "duplicate inventory path")
    expected_digest = hashlib.sha256(json.dumps(target["files"], sort_keys=True, ensure_ascii=True).encode()).hexdigest()
    require(target["snapshot_sha256"] == expected_digest, "inventory digest mismatch")
    for key in ("reviewed", "deferred", "limitations"):
        require(isinstance(coverage.get(key), list), f"coverage.{key} must be an array")
    require(all(isinstance(x, str) and safe_relative(x) for x in coverage["reviewed"]), "invalid reviewed paths")
    require(all(isinstance(x, str) and bool(x.strip()) for x in coverage["limitations"]), "invalid coverage limitations")
    for item in coverage["deferred"] + target["skipped"]:
        require(isinstance(item, dict) and isinstance(item.get("path"), str) and safe_relative(item["path"]) and
                isinstance(item.get("reason"), str) and bool(item["reason"].strip()), "invalid coverage gap")
    require(not coverage["complete"] or (report["mode"] != "baseline" and not coverage["deferred"] and not target.get("skipped")), "complete coverage contradicts baseline, deferred or skipped files")
    require(isinstance(findings, list), "findings must be an array")
    ids = set()
    for item in findings:
        require(isinstance(item, dict), "finding must be an object")
        for key in ("id", "rule_id", "title", "path", "status", "severity", "confidence", "remediation"):
            require(isinstance(item.get(key), str) and bool(item[key].strip()), f"missing finding {key}")
        require(item["id"] not in ids, "duplicate finding id")
        ids.add(item["id"])
        require(safe_relative(item["path"]), "finding path must be repository-relative")
        require(type(item.get("line")) is int and item["line"] >= 1, "invalid finding line")
        require(item["status"] in {"candidate", "confirmed", "dismissed", "needs_review", "fixed", "still_vulnerable", "inconclusive"}, "invalid finding status")
        require(item["severity"] in {"critical", "high", "medium", "low", "info", "unknown"}, "invalid severity")
        require(item["confidence"] in {"high", "medium", "low", "unknown"}, "invalid confidence")
        for key in ("evidence", "attack_path", "counterevidence", "proof_gaps"):
            require(isinstance(item.get(key), list) and all(isinstance(x, str) and x.strip() for x in item[key]), f"invalid {key}")
        validation = item.get("validation")
        require(isinstance(validation, dict) and validation.get("method") in {"not_run", "static", "runtime"} and isinstance(validation.get("result"), str) and bool(validation["result"].strip()), "invalid validation")
        if item["status"] in {"confirmed", "fixed", "still_vulnerable"}:
            require(bool(item["evidence"]) and bool(item["attack_path"]) and not item["proof_gaps"] and validation["method"] != "not_run", "confirmed/fixed verdict needs evidence, attack path, validation and no decision-critical proof gaps")
        if item["status"] == "dismissed":
            require(bool(item["counterevidence"]), "dismissal requires counterevidence")


def render(report: dict) -> str:
    validate_report(report)
    # Encode punctuation before Markdown parsing; backslashes, autolinks and
    # embedded line breaks must not turn report data into active markup.
    def plain(value: object) -> str:
        text = " ".join(str(value).splitlines())
        return "".join(f"&#{ord(c)};" if c in string.punctuation else c if c >= " " else "?" for c in text)
    lines = ["# ChatNoir security review", "", f"Mode: {report['mode']} · coverage complete: {str(report['coverage']['complete']).lower()}",
             f"Snapshot: `{report['target']['snapshot_sha256']}`", "", "Pattern matches are review leads. A zero-candidate baseline is not a clean bill of health.", ""]
    for f in report["findings"]:
        lines += [f"## {plain(f['id'])}: {plain(f['title'])}", "", f"{plain(f['status'])} · {plain(f['severity'])} · {plain(f['path'])}:{f['line']}", ""]
        for label, key in (("Evidence", "evidence"), ("Attack path", "attack_path"), ("Counterevidence", "counterevidence"), ("Proof gaps", "proof_gaps")):
            if f[key]:
                lines += [f"{label}:", ""] + [f"- {plain(x)}" for x in f[key]] + [""]
        lines += [f"Validation ({f['validation']['method']}): {plain(f['validation']['result'])}", "", f"Remediation: {plain(f['remediation'])}", ""]
    lines += ["## Coverage and limitations", "", f"Reviewed by this mode: {len(report['coverage']['reviewed'])} files. Deferred: {len(report['coverage']['deferred'])}. Skipped: {len(report['target'].get('skipped', []))}.", ""]
    lines += [f"- {plain(x)}" for x in report["coverage"]["limitations"]]
    for item in report["coverage"]["deferred"] + report["target"].get("skipped", []):
        lines.append(f"- {plain(item['path'])}: {plain(item['reason'])}")
    return "\n".join(lines) + "\n"


def sarif(report: dict) -> dict:
    validate_report(report)
    results = []
    rules = {}
    for f in report["findings"]:
        if f["status"] in {"dismissed", "fixed"}:
            continue
        rules[f["rule_id"]] = {"id": f["rule_id"], "shortDescription": {"text": f["title"]}}
        confirmed = f["status"] in {"confirmed", "still_vulnerable"}
        results.append({"ruleId": f["rule_id"], "kind": "fail" if confirmed else "review",
                        "level": ("error" if f["severity"] in {"high", "critical"} else "warning") if confirmed else "note",
                        "message": {"text": f"[{f['status']}] {f['title']} — " + "; ".join(f["evidence"])},
                        "locations": [{"physicalLocation": {"artifactLocation": {"uri": quote(f["path"], safe="/"), "uriBaseId": "%SRCROOT%"}, "region": {"startLine": f["line"]}}}],
                        "properties": {"status": f["status"], "confidence": f["confidence"], "severity": f["severity"]}})
    return {"$schema": "https://json.schemastore.org/sarif-2.1.0.json", "version": "2.1.0", "runs": [{"tool": {"driver": {"name": "ChatNoir", "version": VERSION, "informationUri": "https://github.com/fhajjej-ship-it/ChatNoir", "rules": list(rules.values())}}, "results": results}]}


def load_report(path: str) -> dict:
    with open(path, "rb") as stream:
        raw = stream.read(16 * MAX_FILE + 1)
    if len(raw) > 16 * MAX_FILE:
        raise ChatNoirError("report size limit")
    return json.loads(raw)


def client_report(report: dict, output: Path, project: str, author: str) -> None:
    """Format reviewed data; exporting never performs or upgrades a review."""
    validate_report(report)
    if output.suffix.lower() != ".pdf":
        raise ChatNoirError("client-report output must have a .pdf extension")
    try:
        exporter = runpy.run_path(str(Path(__file__).with_name("client_report.py")))
        exporter["write_pdf"](report, output, project=project, author=author)
    except ImportError:
        raise ChatNoirError("PDF export requires ReportLab; install it with this Python's 'python3 -m pip install reportlab'. Other commands need no extra dependencies.") from None
    except FileExistsError:
        raise ChatNoirError("output already exists; choose a new PDF path") from None
    except ValueError as error:
        raise ChatNoirError(str(error)) from None


def main(argv: list[str] | None = None) -> int:
    if sys.version_info < (3, 10):
        print("chatnoir: helpers require Python 3.10+; source review can proceed without them", file=sys.stderr)
        return 2
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=VERSION)
    commands = parser.add_subparsers(dest="command", required=True)
    first = commands.add_parser("first-review", help="Check local setup and prepare a read-only source review")
    first.add_argument("target", type=Path)
    first.add_argument("--focus", choices=FIRST_REVIEW_SCOPES, help="Choose one bounded review scope")
    for name in ("inventory", "scan"):
        cmd = commands.add_parser(name)
        cmd.add_argument("target", type=Path)
        if name == "scan":
            cmd.add_argument("--fail-on-candidates", action="store_true")
    diff = commands.add_parser("diff")
    diff.add_argument("target", type=Path)
    diff.add_argument("--base", required=True)
    diff.add_argument("--head", required=True)
    for name in ("validate", "render", "sarif"):
        commands.add_parser(name).add_argument("report")
    pdf = commands.add_parser("client-report", help="Export existing review data to a client PDF (requires ReportLab)")
    pdf.add_argument("report")
    pdf.add_argument("--output", type=Path, required=True, help="New PDF path; existing files are never overwritten")
    pdf.add_argument("--project", required=True, help="Client-facing project name, not a private filesystem path")
    pdf.add_argument("--author", default="", help="Optional reviewer name")
    args = parser.parse_args(argv)
    try:
        if args.command == "first-review":
            print(render_first_review(first_review(args.target.resolve(), args.focus)), end="")
            return 0
        elif args.command == "inventory":
            output, _ = collect(args.target.resolve())
        elif args.command == "scan":
            output = baseline(args.target.resolve())
            validate_report(output)
        elif args.command == "diff":
            output = exact_diff(args.target.resolve(), args.base, args.head)
        else:
            report = load_report(args.report)
            validate_report(report)
            if args.command == "client-report":
                client_report(report, args.output, args.project, args.author)
                print(json.dumps({"output": str(args.output), "format": "pdf", "review_performed": False}))
                return 0
            if args.command == "render":
                print(render(report), end="")
                return 0
            output = sarif(report) if args.command == "sarif" else {"valid": True, "format": FORMAT}
        print(json.dumps(output, indent=2, ensure_ascii=True))
        return 1 if args.command == "scan" and args.fail_on_candidates and output["findings"] else 0
    except (ChatNoirError, OSError, ValueError, subprocess.SubprocessError) as error:
        message = str(error) if isinstance(error, ChatNoirError) else type(error).__name__
        print(f"chatnoir: {message}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
