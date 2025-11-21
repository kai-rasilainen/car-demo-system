#!/usr/bin/env python3
"""
Simple helper: read an AI analysis markdown report and emit one task file per known component.

Usage:
  scripts/create-component-tasks.py <analysis_md> <output_dir>

This script is intentionally conservative: it does not post to GitHub or create issues.
It creates local markdown files under <output_dir> that a developer or another script can
turn into issues/PRs later.
"""
import argparse
import os
import re
import sys

COMPONENTS = ["A1","A2","B1","B2","B3","B4","C1","C2","C5"]


def excerpt_for_component(text_lines, token, context=5):
    matches = []
    for i, line in enumerate(text_lines):
        if token in line:
            start = max(0, i - context)
            end = min(len(text_lines), i + context + 1)
            excerpt = "".join(text_lines[start:end]).strip()
            matches.append((i, excerpt))
    # fall back: if no direct match, try word-boundary search
    if not matches:
        pattern = re.compile(r"\b" + re.escape(token) + r"\b")
        for i, line in enumerate(text_lines):
            if pattern.search(line):
                start = max(0, i - context)
                end = min(len(text_lines), i + context + 1)
                excerpt = "".join(text_lines[start:end]).strip()
                matches.append((i, excerpt))
    return matches


def main():
    p = argparse.ArgumentParser(description="Create per-component task markdown files from analysis report")
    p.add_argument('analysis_md', help='Path to the AI analysis markdown file')
    p.add_argument('out_dir', help='Directory to write component task files')
    args = p.parse_args()

    if not os.path.isfile(args.analysis_md):
        print(f"[ERROR] Analysis file not found: {args.analysis_md}")
        return 2

    os.makedirs(args.out_dir, exist_ok=True)

    with open(args.analysis_md, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    created = 0
    for comp in COMPONENTS:
        matches = excerpt_for_component(lines, comp)
        filename = os.path.join(args.out_dir, f"task-{comp}.md")
        with open(filename, 'w', encoding='utf-8') as out:
            out.write(f"# Task: {comp}\n\n")
            out.write(f"Generated from analysis: `{os.path.basename(args.analysis_md)}`\n\n")
            if matches:
                out.write("## Analysis Excerpt\n\n```")
                # include up to 3 matches
                for idx, (lineno, excerpt) in enumerate(matches[:3]):
                    out.write(excerpt)
                    if idx != min(2, len(matches)-1):
                        out.write('\n---\n')
                out.write("\n```")
            else:
                out.write("No direct excerpt found for component. Please review the analysis and add details.\n\n")

            out.write('\n## Suggested Subtasks\n\n')
            out.write('- [ ] Investigate required interface changes (APIs, events, DB)\n')
            out.write('- [ ] Produce small, well-scoped PR implementing the change\n')
            out.write('- [ ] Add/adjust tests for the changed component\n')
            out.write('- [ ] Create CI/CD/deployment notes if needed\n')

            out.write('\n## Notes\n\n')
            out.write(f'- Component: {comp}\n')
            out.write('- Effort: _(estimate)_\n')
            out.write('- Dependencies: _(list upstream/downstream components)_\n')

        created += 1

    print(f"[OK] Created {created} task files in {args.out_dir}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
