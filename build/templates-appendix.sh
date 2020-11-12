#!/bin/bash
# Uses sed command to strip Markdown frontmatter from
# https://stackoverflow.com/questions/28221779/how-to-remove-yaml-frontmatter-from-markdown-files

appendix=content/96-template-appendix.md

echo "Adding diagnostics template to appendix"
echo -e "## Appendix B {.page_break_before}\nContributors were asked to complete this template to summarize and evaluate new papers related to diagnostics.\n" > $appendix
sed '1{/^---$/!q;};1,/^---$/d' .github/ISSUE_TEMPLATE/new-diag-study-template.md | sed 's/^#*\ //' >> $appendix

echo "Adding therapeutics template to appendix"
echo -e "\n## Appendix C {.page_break_before}\nContributors were asked to complete this template to summarize and evaluate new papers related to therapeutics.\n" >> $appendix
sed '1{/^---$/!q;};1,/^---$/d' .github/ISSUE_TEMPLATE/new-therapy-study-template.md | sed 's/^#*\ //' >> $appendix

echo "Adding general paper template to appendix"
echo -e "\n## Appendix D {.page_break_before}\nContributors were asked to complete this template to summarize and evaluate new papers related to topics besides therapeutics and diagnostics.\n" >> $appendix
sed '1{/^---$/!q;};1,/^---$/d' .github/ISSUE_TEMPLATE/new-paper-template.md | sed 's/^#*\ //' >> $appendix
