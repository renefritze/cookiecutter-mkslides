# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "weasyprint",
# ]
# ///

import sys
from pathlib import Path

# Define constant for comparison instead of magic number
MIN_ARGS_COUNT = 3


def convert_html_to_pdf(html_file: str, output_pdf: str) -> None:
    """Convert HTML file to PDF using WeasyPrint."""
    from weasyprint import HTML

    # Create directory for output file if it doesn't exist
    output_path = Path(output_pdf)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert HTML to PDF
    HTML(html_file).write_pdf(output_pdf)


if __name__ == "__main__":
    if len(sys.argv) < MIN_ARGS_COUNT:
        print(f"Usage: {sys.argv[0]} input.html output.pdf")
        sys.exit(1)

    convert_html_to_pdf(sys.argv[1], sys.argv[2])
    print(f"Converted {sys.argv[1]} to {sys.argv[2]}")
