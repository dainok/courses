#!/usr/bin/env python3
"""Given a book descriptor, build ePub from Markdown."""

import os
import yaml

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

# Base command
base_cmd_epub = [
    "pandoc",
    "--from markdown-smart",
    "--to epub3",
    "--toc",
    f"--toc-depth={toc_depth}",
    "--css=../templates/common/css/fonts.css",
    "--css=../templates/common/css/common.css",
    "--css=../templates/common/css/epub.css",
    "--css=../templates/book/css/style.css",
    "--template=../templates/default.epub3",
]

print(f"Book {title}:")

# Build ePub metadata file
metadata = {
    "title": [
        {
            "type": "main",
            "text": title,
        },
    ],
    "creator": [{"role": "author", "text": author} for author in authors],
    "toc-title": toc_title,
    "belongs-to-collection": serie,
    "description": description,
    "rights": f"© {year} Andrea Dainese",
}

with open(f"metadata.yml", "w") as fh:
    yaml.dump(metadata, fh, allow_unicode=True, sort_keys=True)

# Create command
book_cmd_epub = base_cmd_epub.copy()
print(f" - Adding cover cover.jpg")
book_cmd_epub.append(f"--epub-cover-image='cover.jpg'")
print(f" - Output on {book_folder}.epub")
book_cmd_epub.append(f"--output '../{book_folder}.epub'")
print(f" - Adding metadata metadata.yml")
book_cmd_epub.append(f"--metadata-file='metadata.yml'")

# Add chapters
for chapter_file in chapter_files:
    chapter_lang_aware_file = f"{chapter_file}.md"
    print(f" - Adding chapter {chapter_file}.md")
    book_cmd_epub.append(f"'{chapter_lang_aware_file}'")
cmdline_epub = " ".join(book_cmd_epub)

print(" - Building ePub")
os.system(cmdline_epub)  # nosec
os.chdir("..")
