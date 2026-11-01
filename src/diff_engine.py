# src/diff_engine.py
import difflib
from ingest import extract_text_from_pdf, chunk_text

def diff_two_pdfs(old_pdf: str, new_pdf: str):
    old_text = extract_text_from_pdf(old_pdf)
    new_text = extract_text_from_pdf(new_pdf)

    old_lines = [l.strip() for l in old_text.splitlines() if l.strip()]
    new_lines = [l.strip() for l in new_text.splitlines() if l.strip()]

    sm = difflib.SequenceMatcher(None, old_lines, new_lines)
    changes = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        changes.append({
            "type": tag,  # 'replace' | 'delete' | 'insert'
            "old": old_lines[i1:i2],
            "new": new_lines[j1:j2],
        })
    return changes


if __name__ == "__main__":
    changes = diff_two_pdfs("data/raw/notification_v1.pdf", "data/raw/notification_v2.pdf")
    for c in changes:
        print(f"\n[{c['type'].upper()}]")
        for line in c["old"]:
            print(f"  - {line}")
        for line in c["new"]:
            print(f"  + {line}")