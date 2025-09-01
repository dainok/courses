#!/usr/bin/env python3
"""Given a book descriptor, build ePub from Markdown."""

import os
import yaml
import markdown
import weasyprint
import lxml.html  # nosec

# See https://python-markdown.github.io/extensions/
MARKDOWN_OPTIONS = {
    "extensions": [
        "markdown.extensions.fenced_code",
        "markdown.extensions.codehilite",
        "markdown.extensions.footnotes",
        "markdown.extensions.tables",
        "markdown_captions",
    ]
}

book_folder = "Sample Book"

print("#" * 78)
print(f"# Directory {book_folder}")
print("#" * 78)

os.chdir(book_folder)
with open("ebook.yml", "r") as fh:
    book_metadata = yaml.safe_load(fh)

# Parameters
title = book_metadata.get("title")
serie = book_metadata.get("serie")
description = book_metadata.get("description")
version = book_metadata.get("version")
chapter_files = book_metadata.get("chapters")
authors = book_metadata.get("authors")
year = book_metadata.get("year")
toc_title = book_metadata.get("toc_title")
toc_depth = book_metadata.get("toc_depth")

print(f"Book {title}:")

# Create HTML version
html_header = f"""<!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="author" content="{', '.join(authors)}">
"""
html_authors = ""
for author in authors:
    html_authors += f"<li>{author}</li>"
html_header += f"""
            <title>{title}</title>
        </head>
        <body>
            <section class="fullpage front-cover">
                <img src="cover.jpg" alt="Cover">
            </section>
            <section class="title-page">
                <div class="title">{title}</div>
                <div class="authors">
                    <ul>
                        {html_authors}
                    </ul>
                </div>
            </section>
"""
html_toc = f'<section><nav id="toc"><h1 id="toc-title">{toc_title}</h1><ol class="toc">'
html_body = ""
html_footer = """
            <div class="blank"/>
        </body>
    </html>
"""

# Add chapters
chapter_counter = 0
for chapter_file in chapter_files:
    # Reading the chapter
    chapter_counter += 1
    chapter_id = f"chapter-{chapter_counter}"
    chapter_lang_aware_file = f"{chapter_file}.md"
    print(f" - Adding chapter {chapter_file}.md")

    with open(chapter_lang_aware_file, "r") as fh:
        md_document = fh.read()
    html_chapter = markdown.markdown(md_document, **MARKDOWN_OPTIONS)
    html_body += f"""
        <section id="{chapter_id}" class="chapter">
            {html_chapter}
        </section>
    """
    # Update TOC
    lxml_root = lxml.html.fromstring(html_chapter)
    title = lxml_root.cssselect("h1")[0].text
    html_toc += f'<li><a href="#{chapter_id}" class="toctext"></a><a href="#{chapter_id}" class="tocpagenr"><span class="toclink">{title}</span></a></li>'

# Close TOC
html_toc += "</ol></nav></section>"

# Format the HTML and write to file
print(" - Building HTML")
html_document = html_header + html_toc + html_body + html_footer
with open(f"{book_folder}.html", "w") as fh:
    fh.write(html_document)

    # Font configuration
    font_config = weasyprint.text.fonts.FontConfiguration()

    # Writing PDF
    print(" - Building PDF")
    weasyprint.HTML(f"{book_folder}.html").write_pdf(
        f"../{book_folder}.pdf",
        stylesheets=[
            weasyprint.CSS(filename="../templates/common/css/fonts.css"),
            weasyprint.CSS(filename="../templates/common/css/common.css"),
            weasyprint.CSS(filename="../templates/book/css/paper_size.css"),
            weasyprint.CSS(filename="../templates/book/css/style.css"),
        ],
        font_config=font_config,
    )

os.chdir("..")
