# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "playwright",
#     "PyPDF2",
#     "pillow",
#     "portend",
# ]
# ///

import subprocess
import sys
import tempfile
import time
from pathlib import Path

import portend

# Define constant for comparison instead of magic number
MIN_ARGS_COUNT = 3


def capture_individual_slides(page, temp_dir, is_reveal=True):
    """Capture individual slides by navigating through the presentation.

    Args:
        page: Playwright page object
        temp_dir: Directory to save individual slide PDFs
        is_reveal: Whether this is a reveal.js presentation

    Returns:
        List of paths to individual slide PDFs
    """
    slide_pdfs = []

    if is_reveal:
        # Get total number of slides from reveal.js
        total_slides = page.evaluate("Reveal.getTotalSlides()")

        # First reset to the beginning
        page.evaluate("Reveal.slide(0, 0)")
        time.sleep(0.5)  # Give time to transition

        for i in range(total_slides):
            # Capture current slide
            pdf_path = Path(temp_dir) / f"slide_{i:03d}.pdf"

            # Make sure slide has loaded completely
            time.sleep(0.5)

            # Take PDF of current slide
            page.pdf(
                path=str(pdf_path),
                format="Letter",
                print_background=True,
                landscape=True,
                margin={
                    "top": "0.4cm",
                    "right": "0.4cm",
                    "bottom": "0.4cm",
                    "left": "0.4cm",
                },
            )
            slide_pdfs.append(pdf_path)

            # Move to next slide if not the last one
            if i < total_slides - 1:
                # Navigate to next slide using right arrow key
                page.keyboard.press("ArrowRight")
                time.sleep(0.5)  # Wait for transition
    else:
        # For non-reveal.js, just take a single PDF of everything
        pdf_path = Path(temp_dir) / "slide_all.pdf"

        page.pdf(
            path=str(pdf_path),
            format="Letter",
            print_background=True,
            landscape=True,
            margin={
                "top": "0.5cm",
                "right": "0.5cm",
                "bottom": "0.5cm",
                "left": "0.5cm",
            },
        )
        slide_pdfs.append(pdf_path)

    return slide_pdfs


def merge_pdfs(pdf_files, output_path):
    """Merge multiple PDFs into a single file.

    Args:
        pdf_files: List of paths to PDF files
        output_path: Path for the merged PDF
    """
    from PyPDF2 import PdfWriter

    merger = PdfWriter()

    for pdf in pdf_files:
        merger.append(pdf)

    merger.write(output_path)
    merger.close()


def generate_reveal_pdf(page, output_pdf):
    """Generate PDF for a reveal.js presentation using print-pdf mode."""
    print("Detected reveal.js presentation")

    # Get slide count
    slide_count = page.evaluate("Reveal.getTotalSlides()")
    print(f"Detected {slide_count} slides")

    # Since we're using ?print-pdf=true, we can just generate
    # the entire PDF in one go (Reveal's print-pdf mode formats slides properly)
    print("Generating PDF using print-pdf mode...")
    page.pdf(
        path=output_pdf,
        format="Letter",
        print_background=True,
        landscape=True,
        margin={
            "top": "0.5cm",
            "right": "0.5cm",
            "bottom": "0.5cm",
            "left": "0.5cm",
        },
    )
    print(f"PDF created successfully at {output_pdf}")


def generate_standard_pdf(page, temp_dir, output_pdf):
    """Generate PDF for a non-reveal.js presentation."""
    # Try the individual slide capture approach first
    try:
        print("Capturing individual slides...")
        slide_pdfs = capture_individual_slides(page, temp_dir, is_reveal=False)

        print(f"Merging {len(slide_pdfs)} slides into final PDF")
        merge_pdfs(slide_pdfs, output_pdf)
        print(f"Created PDF with {len(slide_pdfs)} slides")

    except Exception as e:
        print(f"Error capturing individual slides: {e}")
        print("Falling back to standard PDF export...")

        # Generate PDF directly
        page.pdf(
            path=output_pdf,
            format="Letter",
            print_background=True,
            landscape=True,
            margin={
                "top": "0.5cm",
                "right": "0.5cm",
                "bottom": "0.5cm",
                "left": "0.5cm",
            },
        )


class PresentationServer:
    """Context manager for running the presentation server."""

    def __init__(self, html_file: str, port: int):
        self.filename = Path(html_file)
        self.sub_path = self.filename.with_suffix(".html").name
        self.port = port
        self.process = None
        self.host = f"0.0.0.0"

    def __enter__(self):
        """Start the server when entering the context."""
        print(f"Starting presentation server on port {self.port}...")
        self.process = subprocess.Popen(
            [
                "uv",
                "run",
                "mkslides",
                "serve",
                "--dev-addr",
                f"{self.host}:{self.port}",
                self.filename,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait for server to start
        time.sleep(2)  # Give time for server to start
        # check if the server is running
        if self.process.poll() is not None:
            print("Failed to start the presentation server.")
            print("Error:", self.process.stderr.read().decode())
            print("Output:", self.process.stdout.read().decode())
            self.process.terminate()  # Clean up
            sys.exit(1)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop the server when exiting the context."""
        if self.process:
            print("Shutting down presentation server...")
            self.process.terminate()  # Send SIGTERM
            try:
                self.process.wait(timeout=5)  # Wait for graceful termination
            except subprocess.TimeoutExpired:
                self.process.kill()  # Force kill if it doesn't terminate
                self.process.wait()
            print("Server stopped")

    @property
    def url(self):
        """Get the base URL for the server."""
        return f"http://{self.host}:{self.port}/?print-pdf=true#/"


def convert_html_to_pdf(html_file: str, output_pdf: str) -> None:
    """Convert HTML file to PDF using Playwright with a real browser.

    This function serves the presentation with mkslides and captures all slides
    by navigating to localhost with the print-pdf parameter.
    """
    from playwright.sync_api import sync_playwright

    # Create directory for output file if it doesn't exist
    output_path = Path(output_pdf)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Find an available port
    port = portend.find_available_local_port()

    # Use the context manager for server handling
    with PresentationServer(html_file, port) as server:
        # Build the localhost URL with print-pdf parameter
        localhost_url = f"{server.url}/"
        print(f"Navigating to: {localhost_url}")

        with tempfile.TemporaryDirectory() as temp_dir:
            with sync_playwright() as p:
                # Launch browser (with larger viewport for better slides)
                browser = p.chromium.launch(headless=True)

                # Create context with presentation-friendly viewport for slides
                context = browser.new_context(
                    viewport={"width": 1920, "height": 1920},
                    screen={"width": 1920, "height": 1920},
                    device_scale_factor=2.0,  # Higher resolution for better quality
                )

                page = context.new_page()

                # Navigate to the localhost presentation
                page.goto(localhost_url, wait_until="networkidle")

                # Wait for reveal.js to initialize
                page.wait_for_load_state("domcontentloaded")
                # Additional wait to ensure everything is loaded
                time.sleep(2)

                # Check if we're dealing with a reveal.js presentation
                is_reveal = page.evaluate(
                    """() => {
                    return typeof Reveal !== 'undefined';
                }"""
                )

                print(f"Processing presentation at {localhost_url}")

                # Generate PDF based on presentation type
                if is_reveal:
                    generate_reveal_pdf(page, output_pdf)
                else:
                    generate_standard_pdf(page, temp_dir, output_pdf)

                browser.close()


if __name__ == "__main__":
    if len(sys.argv) < MIN_ARGS_COUNT:
        print(f"Usage: {sys.argv[0]} input.html output.pdf")
        sys.exit(1)

    convert_html_to_pdf(sys.argv[1], sys.argv[2])
    print(f"Converted {sys.argv[1]} to {sys.argv[2]}")
