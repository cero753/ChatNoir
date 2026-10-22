"""Optional client PDF formatter. Input validation belongs to chatnoir.py.

Report text is untrusted data: never interpret its markup or load its resources.
This module neither scans source nor calls a model, browser or network service.
"""
from collections import Counter
from datetime import date
from html import escape
from io import BytesIO
import os
from pathlib import Path
import unicodedata


def write_pdf(report: dict, output: Path, *, project: str, author: str = "") -> None:
    from reportlab import __file__ as reportlab_file
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak,
    )

    if not project.strip():
        raise ValueError("project name must not be empty")
    # Fonts ship with ReportLab; no OS-specific paths or remote assets.
    fonts = Path(reportlab_file).parent / "fonts"
    for name, filename in (("CNBody", "Vera.ttf"), ("CNBold", "VeraBd.ttf")):
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(fonts / filename)))
    glyphs = pdfmetrics.getFont("CNBody").face.charToGlyph

    def plain(value):
        value = unicodedata.normalize("NFC", str(value))
        # Preserve unsupported characters visibly rather than printing missing glyphs.
        return "".join(c if ord(c) in glyphs else f"[U+{ord(c):04X}]"
                       for c in " ".join(value.split()))

    def data(value):
        return escape(plain(value), quote=False)

    ink, muted, line = colors.HexColor("#242424"), colors.HexColor("#606060"), colors.HexColor("#cccccc")
    styles = {
        "title": ParagraphStyle("title", fontName="Times-Roman", fontSize=24, leading=28, spaceAfter=12, textColor=ink),
        "project": ParagraphStyle("project", fontName="CNBold", fontSize=12, leading=17, spaceAfter=9, textColor=ink),
        "h1": ParagraphStyle("h1", fontName="Times-Bold", fontSize=15, leading=19, spaceBefore=14, spaceAfter=10, keepWithNext=True, textColor=ink),
        "h2": ParagraphStyle("h2", fontName="CNBold", fontSize=9.7, leading=14, spaceBefore=10, spaceAfter=5, keepWithNext=True, textColor=ink),
        "body": ParagraphStyle("body", fontName="CNBody", fontSize=9, leading=13.5, spaceAfter=9, textColor=ink),
        "small": ParagraphStyle("small", fontName="CNBody", fontSize=7.8, leading=11.3, spaceAfter=7, textColor=muted),
        "cell": ParagraphStyle("cell", fontName="CNBody", fontSize=8, leading=11.5, textColor=ink),
        "head": ParagraphStyle("head", fontName="CNBold", fontSize=8, leading=11.5, textColor=ink),
    }
    story, width = [], 499.28

    def paragraph(value, style="body"):
        return Paragraph(data(value), styles[style])

    def add(value, style="body"):
        story.append(paragraph(value, style))

    def table(rows, widths):
        cells = [[paragraph(v, "head" if i == 0 else "cell") for v in row] for i, row in enumerate(rows)]
        t = Table(cells, colWidths=widths, repeatRows=1, splitInRow=1, hAlign="LEFT")
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LINEABOVE", (0, 0), (-1, 0), .7, ink),
            ("LINEBELOW", (0, 0), (-1, 0), .4, line),
            ("LINEBELOW", (0, -1), (-1, -1), .7, ink),
        ]))
        t.spaceAfter = 9
        story.append(t)

    coverage, target, findings = report["coverage"], report["target"], report["findings"]
    unresolved = {"candidate", "needs_review", "inconclusive"}
    open_status = {"confirmed", "still_vulnerable"}
    counts = Counter(f["status"] for f in findings)
    status_names = {
        "candidate": "Unverified candidate", "confirmed": "Confirmed open",
        "dismissed": "Dismissed", "needs_review": "Further review needed",
        "fixed": "Fix verified within stated scope", "still_vulnerable": "Still vulnerable",
        "inconclusive": "Inconclusive",
    }
    method_names = {
        "baseline": "Automated baseline", "repository": "Source review", "diff": "Change review",
        "deep": "Detailed source review", "triage": "Finding assessment", "verify": "Fix verification",
    }
    incident = report.get("incident_review")
    if incident:
        method_names = {**method_names, "triage": "Incident exposure assessment", "verify": "Incident response verification"}
    open_count = sum(counts[s] for s in open_status)
    unknown_count = sum(counts[s] for s in unresolved)
    today = date.today().strftime("%d %B %Y").lstrip("0")
    add("Incident exposure review" if incident else "Application security review", "title")
    add(project, "project")
    add(f"Prepared {today} | {method_names[report['mode']]}", "small")
    if author.strip():
        add(f"Reviewer: {author}", "small")
    add("1. Executive summary", "h1")
    if report.get("executive_summary"):
        add(report["executive_summary"])
    noun = "finding" if len(findings) == 1 else "findings"
    open_label = f"{open_count} confirmed open, " if open_count else ""
    add(f"Recorded results: {len(findings)} {noun}; {open_label}"
        f"{unknown_count} unresolved, {counts['fixed']} fixed and {counts['dismissed']} dismissed.", "small")
    if not open_count:
        add("No open vulnerability has been confirmed in the supplied findings. "
            "This is not an all-clear; review unresolved items and coverage gaps.", "small")
    if incident:
        asset_counts = Counter(x["status"] for x in incident["assets"])
        action_counts = Counter(x["status"] for x in incident["actions"])
        add(f"Incident ledger: {asset_counts['potentially_affected']} potentially affected, "
            f"{asset_counts['not_affected']} outside the named advisory conditions, "
            f"{asset_counts['undetermined']} undetermined; {action_counts['verified']} actions verified "
            f"and {action_counts['blocked']} blocked.", "small")
    if report["mode"] == "baseline":
        add("AUTOMATED BASELINE ONLY. Pattern matches are candidates, not confirmed vulnerabilities. "
            "This PDF is not a completed security assessment.")
    elif not findings:
        add("No findings are recorded in this scope. This does not establish that the application is secure.")
    if unknown_count:
        add("Unresolved items need further investigation. Their assigned severity does not make them confirmed issues.")
    next_actions = [f for f in findings if f["status"] in unresolved | open_status]
    if next_actions and report["mode"] != "baseline":
        add("Next actions", "h2")
        add("Recommendations only; these changes and follow-up checks have not been performed by exporting this report. "
            "Resolve the detailed proof gaps before closing an item.", "small")
        table([["Finding / status", "Recommended action and verification"]] + [
            [f"{f['id']}: {status_names[f['status']]}", f["remediation"]]
            for f in next_actions
        ], [143, width - 143])
    add("2. Scope and method", "h1")
    table([
        ["Review coverage", "Recorded scope"],
        ["Reviewed files", len(coverage["reviewed"])],
        ["Deferred / skipped files", f"{len(coverage['deferred'])} / {len(target['skipped'])}"],
        ["Coverage status", "Declared scope completed" if coverage["complete"] else "Limited review; see assessment boundaries below"],
        ["Review method", method_names[report["mode"]] + "; evidence and verification are described below."],
    ], [143, width - 143])
    if coverage["limitations"]:
        add("Declared scope and limitations", "h2")
        for text in coverage["limitations"]:
            add(text, "small")
    for kind, items in (("Deferred", coverage["deferred"]), ("Skipped", target["skipped"])):
        for item in items:
            add(f"{kind}: {item['path']} - {item['reason']}", "small")
    add("Conclusions apply only to the recorded scope and evidence. No overall application security grade is assigned. "
        "This document presents supplied review results; generating it performs no additional testing.", "small")
    if "incident_review" in report:
        incident = report["incident_review"]
        add("Incident exposure and actions", "h1")
        add("Recorded observations only. Export does not check advisories, deployments or credentials. "
            "A potentially affected service is not proof of exploitation; not affected applies only to the named advisory.", "small")
        for item in incident["advisories"]:
            add(f"{item['id']}: {item['title']}", "h2")
            add(f"Reference: {item['url']} | Checked: {item['checked_at']}", "small")
        for item in incident["assets"]:
            add(f"{item['id']}: {item['name']}", "h2")
            add(f"{item['environment']} | {item['status']} | Observed: {item['observed_at'] or 'Not observed'}", "small")
            add("Advisories: " + ", ".join(item["advisory_ids"]), "small")
            for label, key in (("Evidence", "evidence"), ("Gap", "proof_gaps")):
                for value in item[key]:
                    add(f"{label}: {value}")
        for item in incident["actions"]:
            add(f"Action {item['id']}: {item['status']} | Asset: {item['asset_id']}", "h2")
            add(item["description"])
            add(f"Checked: {item['checked_at'] or 'Not checked'} | Verification: {item['verification']['method']}", "small")
            add(item["verification"]["result"])
    if findings or not incident:
        story.append(PageBreak())
    add("3. Detailed findings", "h1")
    if not findings:
        add("No findings were supplied. Review the scope limitations and deferred work before deciding the next assessment step.")
    for finding in findings:
        add(f"{finding['id']}: {finding['title']}", "h2")
        add(f"{status_names[finding['status']]} | Severity: {finding['severity'].capitalize()} | "
            f"Evidence confidence: {finding['confidence'].capitalize()}", "small")
        add(f"Source location: {finding['path']}:{finding['line']}", "small")
        if finding.get("cwe"):
            add(f"Classification: {finding['cwe']}", "small")
        for label, key in (("Evidence", "evidence"), ("Failure path and impact", "attack_path"),
                           ("Controls and limits on impact", "counterevidence"), ("Unresolved questions", "proof_gaps")):
            if not finding[key]:
                continue
            add(label, "h2")
            for i, value in enumerate(finding[key], 1):
                add(f"{i}. {value}")
        add("Recommended remedy", "h2")
        add(finding["remediation"])
    if findings or not incident:
        story.append(PageBreak())
    add("4. Verification and remaining work", "h1")
    for finding in findings:
        add(f"{finding['id']}: {status_names[finding['status']]}", "h2")
        validation_name = {"runtime": "Executed local test", "static": "Source inspection", "not_run": "Not executed"}
        add(f"Verification method: {validation_name[finding['validation']['method']]}", "small")
        add(finding["validation"]["result"])
        if finding["status"] in unresolved:
            add("Next step: resolve the recorded proof gaps before presenting this item as confirmed.", "small")
        elif finding["status"] in open_status:
            add("Next step: apply the recommended remedy, then retest the original trigger and legitimate behavior.", "small")
        elif finding["status"] == "fixed":
            add("The recorded verification supports this fix only within the stated test conditions. "
                "Deployment and broader security coverage require separate confirmation.", "small")
    if not findings:
        add("No finding-level verification was supplied.")
    add("Evidence reference", "h2")
    add("The identifiers below bind these results to the reviewed source snapshot. "
        "They support reproduction and do not establish assessment completeness.", "small")
    add(f"Report data version: ChatNoir {report['version']}", "small")
    add(f"Source inventory SHA-256: {target['snapshot_sha256']}", "small")
    if target.get("git_head"):
        add(f"Recorded Git revision: {target['git_head']}", "small")
    dirty = target.get("dirty")
    state = "Not recorded" if dirty is None else ("Uncommitted changes present; file digests identify reviewed content" if dirty else "No uncommitted changes recorded")
    add(f"Source checkout: {state}", "small")
    for item in target["files"]:
        add(f"{item['path']} | {item['bytes']} bytes | SHA-256 {item['sha256']}", "small")
    add("This is a point-in-time, scoped review record, not a security certification. "
        "Review confidential report contents before sharing.", "small")

    # Build in memory first. Failed layout cannot leave a misleading partial PDF.
    payload = BytesIO()
    doc = SimpleDocTemplate(payload, pagesize=(595.28, 841.89), leftMargin=48, rightMargin=48,
                            topMargin=67, bottomMargin=57, title=plain(project) + " - Security review",
                            author=plain(author), pageCompression=0)

    def frame(canvas, current):
        canvas.saveState()
        canvas.setFillColor(ink)
        canvas.setFont("CNBold", 8.3)
        # Bound header length; full project/author values remain on the first page.
        canvas.drawString(48, 808, plain(author or "ChatNoir")[:50])
        canvas.setFont("CNBody", 7)
        canvas.drawRightString(547.28, 808, "Security review")
        canvas.setStrokeColor(line)
        canvas.setLineWidth(.5)
        canvas.line(48, 797, 547.28, 797)
        canvas.line(48, 42, 547.28, 42)
        canvas.setFillColor(muted)
        canvas.drawString(48, 27, "ChatNoir | Prepared " + today)
        canvas.drawRightString(547.28, 27, str(current.page))
        canvas.restoreState()

    doc.build(story, onFirstPage=frame, onLaterPages=frame)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(output, flags, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload.getvalue())
    except BaseException:
        output.unlink(missing_ok=True)
        raise
