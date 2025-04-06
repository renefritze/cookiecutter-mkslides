# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "playwright",
#     "PyPDF2",
#     "pillow",
# ]
# ///

import sys
import time
import asyncio
import tempfile
from pathlib import Path


# Define constant for comparison instead of magic number
MIN_ARGS_COUNT = 3


async def capture_individual_slides(page, temp_dir, is_reveal=True):
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
        total_slides = await page.evaluate("Reveal.getTotalSlides()")

        # First reset to the beginning
        await page.evaluate("Reveal.slide(0, 0)")
        await asyncio.sleep(0.5)  # Give time to transition

        for i in range(total_slides):
            # Capture current slide
            pdf_path = Path(temp_dir) / f"slide_{i:03d}.pdf"

            # Make sure slide has loaded completely
            await asyncio.sleep(0.5)

            # Take PDF of current slide - correct syntax for Playwright
            await page.pdf(
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
                await page.keyboard.press("ArrowRight")
                await asyncio.sleep(0.5)  # Wait for transition
    else:
        # For non-reveal.js, just take a single PDF of everything
        pdf_path = Path(temp_dir) / "slide_all.pdf"

        await page.pdf(
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


async def convert_html_to_pdf(html_file: str, output_pdf: str) -> None:
    """Convert HTML file to PDF using Playwright with a real browser.

    This function opens the HTML file in a headless browser and captures all slides
    by automatically navigating through the presentation using right arrow key presses.
    """
    from playwright.async_api import async_playwright

    # Create directory for output file if it doesn't exist
    output_path = Path(output_pdf)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert to file URL format for local files
    file_url = f"file://{Path(html_file).resolve()}"

    with tempfile.TemporaryDirectory() as temp_dir:
        async with async_playwright() as p:
            # Launch browser (with larger viewport for better slides)
            browser = await p.chromium.launch(headless=True)

            # Create context with presentation-friendly viewport for slides
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                screen={"width": 1920, "height": 1080},
                device_scale_factor=2.0,  # Higher resolution for better quality
            )

            page = await context.new_page()

            # Navigate to the presentation
            await page.goto(file_url, wait_until="networkidle")

            # Wait for reveal.js to initialize
            await page.wait_for_load_state("domcontentloaded")
            # Additional wait to ensure everything is loaded
            await asyncio.sleep(2)

            # Check if we're dealing with a reveal.js presentation
            is_reveal = await page.evaluate(
                """() => {
                return typeof Reveal !== 'undefined';
            }"""
            )

            print(f"Processing presentation at {html_file}")

            if is_reveal:
                print("Detected reveal.js presentation")

                # Get slide count
                slide_count = await page.evaluate("Reveal.getTotalSlides()")
                print(f"Detected {slide_count} slides")

                # Try the individual slide capture approach first
                try:
                    print("Capturing individual slides...")
                    slide_pdfs = await capture_individual_slides(
                        page, temp_dir, is_reveal=True
                    )

                    print(f"Merging {len(slide_pdfs)} slides into final PDF")
                    merge_pdfs(slide_pdfs, output_pdf)
                    print(f"Created PDF with {len(slide_pdfs)} slides")

                except Exception as e:
                    print(f"Error capturing individual slides: {e}")
                    print("Falling back to standard PDF export...")

                    # Configure reveal.js for printing
                    await page.evaluate(
                        """() => {
                        // Configure reveal for printing
                        Reveal.configure({
                            pdfMaxPagesPerSlide: 1,
                            pdfSeparateFragments: false
                        });
                    }"""
                    )

                    # Generate single PDF with correct parameters
                    await page.pdf(
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
            else:
                print("Using generic presentation capture approach")

                # Try to detect slides based on common selectors
                slide_elements = await page.evaluate(
                    """() => {
                    return document.querySelectorAll('.slide, section, .slide-content').length;
                }"""
                )

                print(f"Detected approximately {slide_elements} slide elements")

                # Generate PDF directly
                await page.pdf(
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

            await browser.close()


if __name__ == "__main__":
    if len(sys.argv) < MIN_ARGS_COUNT:
        print(f"Usage: {sys.argv[0]} input.html output.pdf")
        sys.exit(1)

    asyncio.run(convert_html_to_pdf(sys.argv[1], sys.argv[2]))
    print(f"Converted {sys.argv[1]} to {sys.argv[2]}")
