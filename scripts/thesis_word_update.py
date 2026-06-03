#!/usr/bin/env python3
"""
thesis_word_update.py — 用 Word COM 自動更新 DOCX 欄位（TOC 頁碼等）

用法：
    python scripts/thesis_word_update.py update-fields --docx path.docx
    python scripts/thesis_word_update.py check-word

流程：
    1. 用 PowerShell 呼叫 Word COM Automation
    2. 開啟 DOCX → 更新所有欄位（含 TOC、PAGEREF 等）→ 存檔關閉
    3. TOC 頁碼、標題、表目錄、圖目錄全部自動刷新
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOCX = ROOT / "deliverables" / "docx" / "thesis_render_latest.docx"

# PowerShell script: open Word, update all fields (TOC, cross-refs, etc.), save
WORD_UPDATE_FIELDS_SCRIPT = r"""
param(
    [Parameter(Mandatory = $true)][string]$DocxPath
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$OutputEncoding = [Console]::OutputEncoding
$word = $null
$document = $null

function Get-CleanParagraphText {
    param([object]$Paragraph)
    if ($null -eq $Paragraph) { return "" }
    $text = $Paragraph.Range.Text
    $text = $text -replace "[`r`a]", ""
    return $text.Trim()
}

function Find-HeadingIndex {
    param(
        [object]$Document,
        [string]$HeadingText,
        [int]$StartIndex = 1
    )
    for ($i = $StartIndex; $i -le $Document.Paragraphs.Count; $i++) {
        $para = $Document.Paragraphs.Item($i)
        if ($para.Range.Style -eq "Heading 1" -and (Get-CleanParagraphText $para) -eq $HeadingText) {
            return $i
        }
    }
    return 0
}

function Get-AppendixCaptionEntries {
    param(
        [object]$Document,
        [string]$Prefix
    )
    $entries = @()
    for ($i = 1; $i -le $Document.Paragraphs.Count; $i++) {
        $para = $Document.Paragraphs.Item($i)
        if ($para.Range.Style -ne "Caption") { continue }
        $text = Get-CleanParagraphText $para
        if ($text -notmatch ("^{0}\d+" -f [regex]::Escape($Prefix))) { continue }
        $entries += [pscustomobject]@{
            Text = $text
            Page = [int]$para.Range.Information(3)
        }
    }
    return $entries
}

function Remove-AppendixDirectoryRegion {
    param(
        [object]$Document,
        [int]$StartIndex,
        [int]$EndIndex,
        [string]$MainPrefix,
        [string]$AppendixPrefix
    )
    $lastMain = 0
    for ($i = $StartIndex; $i -lt $EndIndex; $i++) {
        $text = Get-CleanParagraphText ($Document.Paragraphs.Item($i))
        if ($text.StartsWith($MainPrefix)) {
            $lastMain = $i
        }
    }
    if ($lastMain -eq 0) { return }
    for ($i = $EndIndex - 1; $i -gt $lastMain; $i--) {
        $para = $Document.Paragraphs.Item($i)
        $text = Get-CleanParagraphText $para
        if ($text -eq "" -or $text.StartsWith($AppendixPrefix)) {
            $para.Range.Delete()
        }
    }
}

function Get-DirectoryTabPosition {
    param(
        [object]$Document,
        [int]$HeadingIndex
    )
    for ($i = $HeadingIndex + 1; $i -le $Document.Paragraphs.Count; $i++) {
        $para = $Document.Paragraphs.Item($i)
        $text = Get-CleanParagraphText $para
        if ($text -match "^[表圖]\s*\d+") {
            if ($para.Range.ParagraphFormat.TabStops.Count -ge 1) {
                return $para.Range.ParagraphFormat.TabStops.Item(1).Position
            }
        }
    }
    return 425.25
}

function Format-DirectoryParagraph {
    param(
        [object]$Paragraph,
        [float]$TabPosition
    )
    $Paragraph.Range.Style = "table of figures"
    $Paragraph.Range.Font.Bold = $false
    $pf = $Paragraph.Range.ParagraphFormat
    $pf.LeftIndent = 0
    $pf.FirstLineIndent = 0
    $pf.SpaceBefore = 0
    $pf.SpaceAfter = 0
    $pf.TabStops.ClearAll()
    $null = $pf.TabStops.Add($TabPosition, 2, 1)
}

function Insert-AppendixDirectoryEntries {
    param(
        [object]$Document,
        [int]$AnchorIndex,
        [array]$Entries,
        [float]$TabPosition,
        [string]$Prefix
    )
    if ($Entries.Count -eq 0) { return }
    $anchor = $Document.Paragraphs.Item($AnchorIndex).Range
    $lines = @()
    foreach ($entry in $Entries) {
        $lines += ("{0}`t{1}" -f $entry.Text, $entry.Page)
    }
    $anchor.InsertBefore(($lines -join "`r") + "`r")

    for ($i = 1; $i -le $Document.Paragraphs.Count; $i++) {
        $para = $Document.Paragraphs.Item($i)
        $text = Get-CleanParagraphText $para
        if ($text.StartsWith($Prefix)) {
            Format-DirectoryParagraph $para $TabPosition
        }
    }
}

function Sync-AppendixDirectories {
    param([object]$Document)

    $tableHeading = Find-HeadingIndex -Document $Document -HeadingText "表目錄"
    $figureHeading = Find-HeadingIndex -Document $Document -HeadingText "圖目錄" -StartIndex ($tableHeading + 1)
    if ($tableHeading -eq 0 -or $figureHeading -eq 0) { return }

    $nextMainHeading = 0
    for ($i = $figureHeading + 1; $i -le $Document.Paragraphs.Count; $i++) {
        $para = $Document.Paragraphs.Item($i)
        if ($para.Range.Style -eq "Heading 1" -and (Get-CleanParagraphText $para) -ne "圖目錄") {
            $nextMainHeading = $i
            break
        }
    }
    if ($nextMainHeading -eq 0) { return }

    $appendixTables = Get-AppendixCaptionEntries -Document $Document -Prefix "附表"
    $appendixFigures = Get-AppendixCaptionEntries -Document $Document -Prefix "附圖"

    $tableTab = Get-DirectoryTabPosition -Document $Document -HeadingIndex $tableHeading
    $figureTab = Get-DirectoryTabPosition -Document $Document -HeadingIndex $figureHeading

    Remove-AppendixDirectoryRegion -Document $Document -StartIndex ($tableHeading + 1) -EndIndex $figureHeading -MainPrefix "表 " -AppendixPrefix "附表"
    $figureHeading = Find-HeadingIndex -Document $Document -HeadingText "圖目錄" -StartIndex ($tableHeading + 1)
    Insert-AppendixDirectoryEntries -Document $Document -AnchorIndex $figureHeading -Entries $appendixTables -TabPosition $tableTab -Prefix "附表"

    $figureHeading = Find-HeadingIndex -Document $Document -HeadingText "圖目錄" -StartIndex ($tableHeading + 1)
    $nextMainHeading = 0
    for ($i = $figureHeading + 1; $i -le $Document.Paragraphs.Count; $i++) {
        $para = $Document.Paragraphs.Item($i)
        if ($para.Range.Style -eq "Heading 1" -and (Get-CleanParagraphText $para) -ne "圖目錄") {
            $nextMainHeading = $i
            break
        }
    }
    if ($nextMainHeading -eq 0) { return }

    Remove-AppendixDirectoryRegion -Document $Document -StartIndex ($figureHeading + 1) -EndIndex $nextMainHeading -MainPrefix "圖 " -AppendixPrefix "附圖"
    $insertBefore = $nextMainHeading
    for ($i = $nextMainHeading - 1; $i -gt $figureHeading; $i--) {
        $text = Get-CleanParagraphText ($Document.Paragraphs.Item($i))
        if ($text -eq "") {
            $insertBefore = $i
            break
        }
    }
    Insert-AppendixDirectoryEntries -Document $Document -AnchorIndex $insertBefore -Entries $appendixFigures -TabPosition $figureTab -Prefix "附圖"
}

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0

    $document = $word.Documents.Open($DocxPath, $false, $false)

    # Update all fields in the main document body
    $document.Fields | ForEach-Object { $_.Update() | Out-Null }

    # Update fields in all story ranges (headers, footers, etc.)
    foreach ($story in $document.StoryRanges) {
        $story.Fields | ForEach-Object { $_.Update() | Out-Null }
    }

    # Update TOC specifically
    foreach ($toc in $document.TablesOfContents) {
        $toc.Update()
    }

    # Update table of figures (表目錄, 圖目錄)
    foreach ($tof in $document.TablesOfFigures) {
        $tof.Update()
    }

    $document.Save()
    Write-Output "FIELDS_UPDATED_OK"
}
finally {
    if ($document -ne $null) {
        $document.Close($false) | Out-Null
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($document)
        $document = $null
    }
    if ($word -ne $null) {
        $word.Quit() | Out-Null
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)
        $word = $null
    }
}
"""

WORD_UPDATE_TOC_ONLY_SCRIPT = r"""
param(
    [Parameter(Mandatory = $true)][string]$DocxPath
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$OutputEncoding = [Console]::OutputEncoding
$word = $null
$document = $null

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0

    $document = $word.Documents.Open($DocxPath, $false, $false)

    # Safer mode for v2 pipeline: only refresh TOC field results and avoid
    # full field/story updates that may rewrite numbering chains.
    foreach ($toc in $document.TablesOfContents) {
        $toc.Update()
    }

    $document.Save()
    Write-Output "TOC_UPDATED_OK"
}
finally {
    if ($document -ne $null) {
        $document.Close($false) | Out-Null
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($document)
        $document = $null
    }
    if ($word -ne $null) {
        $word.Quit() | Out-Null
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)
        $word = $null
    }
}
"""

WORD_EXPORT_APPENDIX_DIRECTORY_DATA_SCRIPT = r"""
param(
    [Parameter(Mandatory = $true)][string]$DocxPath
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$OutputEncoding = [Console]::OutputEncoding
$word = $null
$document = $null

function Get-CleanParagraphText {
    param([object]$Paragraph)
    if ($null -eq $Paragraph) { return "" }
    $text = $Paragraph.Range.Text
    $text = $text -replace "[`r`a]", ""
    return $text.Trim()
}

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0

    $document = $word.Documents.Open($DocxPath, $false, $true)

    $tables = @()
    $figures = @()
    for ($i = 1; $i -le $document.Paragraphs.Count; $i++) {
        $para = $document.Paragraphs.Item($i)
        if ($para.Range.Style -ne "Caption") { continue }
        $text = Get-CleanParagraphText $para
        if ($text -match "^附表\d+") {
            $tables += [pscustomobject]@{
                text = $text
                page = [int]$para.Range.Information(3)
            }
        }
        elseif ($text -match "^附圖\d+") {
            $figures += [pscustomobject]@{
                text = $text
                page = [int]$para.Range.Information(3)
            }
        }
    }

    $payload = [pscustomobject]@{
        tables = $tables
        figures = $figures
    }
    $payload | ConvertTo-Json -Depth 5 -Compress
}
finally {
    if ($document -ne $null) {
        $document.Close($false) | Out-Null
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($document)
        $document = $null
    }
    if ($word -ne $null) {
        $word.Quit() | Out-Null
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)
        $word = $null
    }
}
"""


def run_powershell(script: str, args: list[str]) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".ps1", delete=False, encoding="utf-8-sig") as handle:
        handle.write(script)
        temp_script = Path(handle.name)
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(temp_script),
                *args,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            raise RuntimeError(
                "PowerShell field update failed.\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}"
            )
        return result.stdout.strip()
    finally:
        temp_script.unlink(missing_ok=True)


def list_winword_pids() -> set[int]:
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    pids: set[int] = set()
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.isdigit():
            pids.add(int(line))
    return pids


def stop_processes(pids: set[int]) -> None:
    if not pids:
        return
    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            f"Stop-Process -Id {','.join(str(pid) for pid in sorted(pids))} -Force",
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def file_is_released(path: Path) -> bool:
    try:
        with path.open("rb+"):
            return True
    except PermissionError:
        return False
    except OSError:
        return False


def wait_for_file_release(path: Path, timeout_s: float = 15.0, poll_s: float = 0.5) -> bool:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if file_is_released(path):
            return True
        time.sleep(poll_s)
    return file_is_released(path)


def word_available() -> bool:
    probe = (
        "$word = $null; "
        "try { $word = New-Object -ComObject Word.Application; Write-Output 'WORD_COM_OK' } "
        "finally { if ($word -ne $null) { $word.Quit() | Out-Null } }"
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", probe],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0 and "WORD_COM_OK" in result.stdout


def update_fields(docx_path: Path, mode: str = "all") -> None:
    if not docx_path.exists():
        raise SystemExit(f"DOCX not found: {docx_path}")
    abs_path = str(docx_path.resolve())
    last_error: Exception | None = None

    for attempt in range(2):
        before_pids = list_winword_pids()
        try:
            script = WORD_UPDATE_FIELDS_SCRIPT if mode == "all" else WORD_UPDATE_TOC_ONLY_SCRIPT
            output = run_powershell(script, ["-DocxPath", abs_path])
        except Exception as exc:
            last_error = exc
            after_pids = list_winword_pids()
            spawned = after_pids - before_pids
            stop_processes(spawned)
            wait_for_file_release(docx_path, timeout_s=8.0)
            if attempt == 0:
                continue
            raise

        after_pids = list_winword_pids()
        spawned = after_pids - before_pids
        if not wait_for_file_release(docx_path, timeout_s=8.0):
            stop_processes(spawned)
            if attempt == 0:
                wait_for_file_release(docx_path, timeout_s=8.0)
                continue
            raise RuntimeError(f"Word field update left the DOCX locked: {docx_path}")

        expected_ok = "FIELDS_UPDATED_OK" if mode == "all" else "TOC_UPDATED_OK"
        if expected_ok in output:
            if mode == "all":
                print(f"Fields updated: {docx_path}")
            else:
                print(f"TOC updated: {docx_path}")
        else:
            print(f"Warning: unexpected output: {output}", file=sys.stderr)
        return

    if last_error is not None:
        raise last_error


def cmd_update_fields(args: argparse.Namespace) -> None:
    update_fields(Path(args.docx), mode=args.mode)


def export_appendix_directory_data(docx_path: Path, json_path: Path | None = None) -> None:
    if not docx_path.exists():
        raise SystemExit(f"DOCX not found: {docx_path}")
    abs_path = str(docx_path.resolve())
    output = run_powershell(WORD_EXPORT_APPENDIX_DIRECTORY_DATA_SCRIPT, ["-DocxPath", abs_path])
    if json_path is not None:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(output, encoding="utf-8")
        print(f"Appendix directory data exported: {json_path}")
    else:
        print(output)


def cmd_export_appendix_directory_data(args: argparse.Namespace) -> None:
    json_path = Path(args.json) if args.json else None
    export_appendix_directory_data(Path(args.docx), json_path)


def cmd_check_word(_: argparse.Namespace) -> None:
    if not word_available():
        raise SystemExit("Microsoft Word COM automation is not available on this machine.")
    print("WORD_COM_OK")


def main() -> None:
    parser = argparse.ArgumentParser(description="Update Word fields (TOC, page refs) via COM automation")
    sub = parser.add_subparsers(dest="command", required=True)

    update = sub.add_parser("update-fields", help="Open DOCX in Word and update fields")
    update.add_argument("--docx", default=str(DEFAULT_DOCX))
    update.add_argument("--mode", choices=["all", "toc-only"], default="all")
    update.set_defaults(func=cmd_update_fields)

    export = sub.add_parser(
        "export-appendix-directory-data",
        help="Read appendix table/figure caption pages from Word and export JSON",
    )
    export.add_argument("--docx", default=str(DEFAULT_DOCX))
    export.add_argument("--json", help="Write JSON payload to this path instead of stdout")
    export.set_defaults(func=cmd_export_appendix_directory_data)

    check = sub.add_parser("check-word", help="Verify Word COM is available")
    check.set_defaults(func=cmd_check_word)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
