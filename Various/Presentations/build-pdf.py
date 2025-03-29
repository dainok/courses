#!/usr/bin/env python
"""Given a book descriptor, build PDF from Markdown."""

import os
import glob
import jinja2
import yaml
import markdown
import weasyprint


templateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=templateLoader, autoescape=True)
template = templateEnv.get_template("slide_template.j2")

slide_folder = "Sample Presentation"
print("#" * 78)
print(f"# Directory {slide_folder}")
print("#" * 78)
os.chdir(slide_folder)
with open("presentation.yml", "r") as fh:
    presentation_metadata = yaml.safe_load(fh)

language = presentation_metadata["language"]
presentation_slides = glob.glob("*.md")
if presentation_slides:
    presentation_slides.sort()

main_logo = presentation_metadata.get("logo")
logos = presentation_metadata.get("logos")
rights = presentation_metadata.get("rights")
subtitle = presentation_metadata.get("subtitle")
footer = presentation_metadata.get("footer")
title = presentation_metadata["title"]
version = presentation_metadata["version"]
stylesheets = [
    "../templates/common/css/common.css",
    "../templates/slides/css/layouts.css",
    "../templates/slides/css/style.css",
]

base_fileame = f"{title} v{version} {language.upper()}"
base_fileame = base_fileame.replace("'", " ")

print(f"Presentation {title} [{language}]")

# Add chapters
slides = []
for slide in presentation_slides:
    slide_counter = int(slide.split(".")[0].split("-")[0])
    slide_id = f"slide-{slide_counter}"

    # Import slides
    print(f" - Adding slide {slide}")
    with open(slide, "r") as fh:
        md_document = fh.read()
    md = markdown.Markdown(extensions=[
            "markdown.extensions.meta",
            "markdown.extensions.fenced_code",
            "markdown.extensions.codehilite",
            "markdown.extensions.footnotes",
            "markdown.extensions.tables",
            "markdown.extensions.attr_list",
            "markdown.extensions.md_in_html",
            "markdown_captions",
            "pymdownx.tilde",
            "pymdownx.caret"
        ]
    )
    slide_body = md.convert(md_document)
    slide_meta = md.Meta

    # Storing logo
    logo_url = None
    slide_logo = None
    if main_logo:
        slide_logo = main_logo
    if "logo" in slide_meta:
        slide_logo = "".join(slide_meta["logo"])
    try:
        logo_url = logos[slide_logo]
    except KeyError:
        raise KeyError(f"ERROR: logo {slide_logo} is not defined.")

    slide_data = {
        "id": slide_id,
        "content": slide_body,
        "meta": {
            "layout": "".join(slide_meta["layout"]),
        },
        "logo": logo_url,
    }
    slides.append(slide_data)

# Dump HTML using Jinja template
print(" - Building HTML")
html_document = template.render(
    language=language,
    title=title,
    subtitle=subtitle,
    slides=slides,
    stylesheets=stylesheets,
    footer=footer,
)
with open("presentation.html", "w") as fh:
    fh.write(html_document)

# Font configuration
font_config = weasyprint.text.fonts.FontConfiguration()

# Render PDF
print(" - Rendering PDF")
weasyprint.HTML("presentation.html").write_pdf(
    "Sample Presentation.pdf",
    stylesheets=stylesheets,
    font_config=font_config,
    presentational_hints=True,
)

os.chdir("..")
