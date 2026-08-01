import re

HUNK_HEADER_RE = re.compile(r"^@@ -(\d+),(\d+) \+(\d+),(\d+) @@")


def parse_last_diff_line(git_diff: str) -> dict:
    """Find the last hunk header in a unified diff and compute the last old/new line numbers."""
    cleaned = git_diff.replace("\n\\ No newline at end of file", "")
    diff_lines = cleaned.rstrip().split("\n")
    if not diff_lines:
        return {"old_line": None, "new_line": None}

    last_line_first_char = diff_lines[-1][:1] if diff_lines[-1] else ""

    last_hunk = ""
    for line in reversed(diff_lines):
        if HUNK_HEADER_RE.match(line):
            last_hunk = line
            break

    match = HUNK_HEADER_RE.match(last_hunk)
    if not match:
        return {"old_line": None, "new_line": None}

    old_start, old_count, new_start, new_count = (int(g) for g in match.groups())
    last_old_line_count = old_start + old_count
    last_new_line_count = new_start + new_count

    old_line = None if last_line_first_char == "+" else last_old_line_count - 1
    new_line = None if last_line_first_char == "-" else last_new_line_count - 1

    return {"old_line": old_line, "new_line": new_line}


def split_diff_code(git_diff: str) -> dict:
    """Split a unified diff into the 'original' (removed/context) and 'new' (added/context) code."""
    original_lines = []
    new_lines = []
    for line in git_diff.rstrip().split("\n"):
        if line.startswith("-"):
            original_lines.append(line)
        elif line.startswith("+"):
            new_lines.append(line)
        else:
            original_lines.append(line)
            new_lines.append(line)
    return {"original_code": "\n".join(original_lines), "new_code": "\n".join(new_lines)}
