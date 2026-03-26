#!/usr/bin/env python3
"""Build LaTeX documents to PDF with auto-incrementing version numbers."""

import subprocess
import shutil
import sys
import re
from pathlib import Path


def find_latex_compiler():
    """Find an available LaTeX compiler."""
    compilers = ["tectonic", "pdflatex", "xelatex", "latexmk"]
    for compiler in compilers:
        if shutil.which(compiler):
            return compiler
    return None


def get_next_version(pdf_dir: Path, base_name: str) -> int:
    """Get the next version number by scanning existing PDFs."""
    if not pdf_dir.exists():
        return 1
    
    pattern = re.compile(rf"^{re.escape(base_name)}_(\d+)\.pdf$")
    max_version = 0
    
    for pdf_file in pdf_dir.glob(f"{base_name}_*.pdf"):
        match = pattern.match(pdf_file.name)
        if match:
            version = int(match.group(1))
            max_version = max(max_version, version)
    
    return max_version + 1


def build_pdf(tex_file: Path, compiler: str = None):
    """Build a PDF from a LaTeX file with versioned output."""
    if compiler is None:
        compiler = find_latex_compiler()
    
    if compiler is None:
        print("ERROR: No LaTeX compiler found.")
        print("Install one of: tectonic, pdflatex (MacTeX), xelatex, latexmk")
        print("")
        print("Quick install options:")
        print("  brew install tectonic          # Lightweight, recommended")
        print("  brew install --cask mactex     # Full MacTeX (~4GB)")
        print("")
        sys.exit(1)
    
    print(f"Using compiler: {compiler}")
    print(f"Building: {tex_file}")
    
    # Create pdf subdirectory
    source_dir = tex_file.parent
    pdf_dir = source_dir / "pdf"
    pdf_dir.mkdir(exist_ok=True)
    
    # Get folder name for PDF naming (e.g., "data_mesh")
    folder_name = source_dir.name
    
    # Get next version number
    version = get_next_version(pdf_dir, folder_name)
    versioned_name = f"{folder_name}_{version:02d}.pdf"
    
    print(f"Output: {pdf_dir / versioned_name}")
    
    # Build to temp location first, then move
    temp_pdf = source_dir / (tex_file.stem + ".pdf")
    
    if compiler == "tectonic":
        cmd = ["tectonic", str(tex_file)]
    elif compiler == "latexmk":
        cmd = ["latexmk", "-pdf", str(tex_file)]
    else:
        cmd = [compiler, str(tex_file)]
    
    try:
        result = subprocess.run(cmd, cwd=source_dir, capture_output=True, text=True)
        if result.returncode == 0:
            # Move and rename to versioned output
            final_pdf = pdf_dir / versioned_name
            if temp_pdf.exists():
                shutil.move(str(temp_pdf), str(final_pdf))
                print(f"SUCCESS: {final_pdf}")
                
                # Clean up auxiliary files
                for ext in [".aux", ".log", ".out", ".toc", ".fls", ".fdb_latexmk"]:
                    aux_file = source_dir / (tex_file.stem + ext)
                    if aux_file.exists():
                        aux_file.unlink()
                
                return final_pdf
            else:
                print(f"ERROR: PDF not created at {temp_pdf}")
                sys.exit(1)
        else:
            print(f"FAILED:")
            print(result.stderr)
            print(result.stdout)
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        default_file = Path(__file__).parent.parent / "data_mesh" / "KDP_DE_strategy.tex"
        if default_file.exists():
            tex_file = default_file
        else:
            print("Usage: uv run build-pdf <path/to/file.tex>")
            print("   or: python scripts/build.py <path/to/file.tex>")
            sys.exit(1)
    else:
        tex_file = Path(sys.argv[1])
    
    if not tex_file.exists():
        print(f"ERROR: File not found: {tex_file}")
        sys.exit(1)
    
    build_pdf(tex_file.resolve())


if __name__ == "__main__":
    main()
