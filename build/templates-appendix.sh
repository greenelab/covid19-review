#!/bin/bash
# Uses sed command to strip Markdown frontmatter from
# https://stackoverflow.com/questions/28221779/how-to-remove-yaml-frontmatter-from-markdown-files

appendix=content/96-template-appendix.md

echo "Adding diagnostics template to appendix"
echo -e "## Appendix B {.page_break_before}\n" > $appendix
sed '1{/^---$/!q;};1,/^---$/d' .github/ISSUE_TEMPLATE/new-diag-study-template.md | sed 's/^#*\ //' >> $appendix

echo "Adding therapeutics template to appendix"
echo -e "\n## Appendix C {.page_break_before}\n" >> $appendix
sed '1{/^---$/!q;};1,/^---$/d' .github/ISSUE_TEMPLATE/new-therapy-study-template.md | sed 's/^#*\ //' >> $appendix

echo "Adding general paper template to appendix"
echo -e "\n## Appendix D {.page_break_before}\n" >> $appendix
sed '1{/^---$/!q;};1,/^---$/d' .github/ISSUE_TEMPLATE/new-paper-template.md | sed 's/^#*\ //' >> $appendix
