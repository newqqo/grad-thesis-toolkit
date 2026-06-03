from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOCX = ROOT / "deliverables" / "docx" / "thesis_render_latest.docx"
DEFAULT_OUTPUT = ROOT / "deliverables" / "pdf" / "thesis_render_latest.pdf"

WORD_EXPORT_SCRIPT = r"""
param(
    [Parameter(Mandatory = $true)][string]$DocxPath,
    [Parameter(Mandatory = $true)][string]$PdfPath
)

$ErrorActionPreference = 'Stop'
$word = $null
$document = $null

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Open($DocxPath, $false, $true)
    $wdExportFormatPDF = 17
    $document.ExportAsFixedFormat($PdfPath, $wdExportFormatPDF)
}
finally {
    if ($document -ne $null) {
        $document.Close($false) | Out-Null
    }
    if ($word -ne $null) {
        $word.Quit() | Out-Null
    }
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}
"""


def run_powershell(script: str, args: list[str]) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".ps1", delete=False, encoding="utf-8") as handle:
        handle.write(script)
        temp_script = Path(handle.name)
    try:
        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(temp_script),
                *args,
            ],
            check=True,
        )
    finally:
        temp_script.unlink(missing_ok=True)


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


def export_docx_to_pdf(docx_path: Path, pdf_path: Path) -> None:
    if not docx_path.exists():
        raise SystemExit(f"docx not found: {docx_path}")
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    run_powershell(WORD_EXPORT_SCRIPT, ["-DocxPath", str(docx_path), "-PdfPath", str(pdf_path)])


def cmd_export(args: argparse.Namespace) -> None:
    export_docx_to_pdf(Path(args.docx), Path(args.output))


def cmd_check_word(_: argparse.Namespace) -> None:
    if not word_available():
        raise SystemExit("Microsoft Word COM automation is not available on this machine.")
    print("WORD_COM_OK")


def main() -> None:
    parser = argparse.ArgumentParser(description="export thesis DOCX deliverables to PDF with Microsoft Word")
    sub = parser.add_subparsers(dest="command", required=True)

    export = sub.add_parser("export", help="export a DOCX to PDF via local Microsoft Word")
    export.add_argument("--docx", default=str(DEFAULT_DOCX))
    export.add_argument("--output", default=str(DEFAULT_OUTPUT))
    export.set_defaults(func=cmd_export)

    check = sub.add_parser("check-word", help="verify that Microsoft Word COM automation is available")
    check.set_defaults(func=cmd_check_word)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
