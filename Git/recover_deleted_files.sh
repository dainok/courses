#!/bin/bash

# Find deleted files
git log --diff-filter D --pretty="format:" --name-only | sed '/^$/d' > deleted_files.txt

# Find the associated commit
while read line; do git rev-list HEAD -n 1 -- $line | tr '\n' ' '; echo $line; done < deleted_files.txt > deleted_commits.txt

# Restore files
while read line; do git checkout $(echo $line | cut -d" " -f1)^  $(echo $line | cut -d" " -f2); done < deleted_commits.txt
