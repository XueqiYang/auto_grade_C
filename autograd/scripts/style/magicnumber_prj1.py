import re
from .comment import search_block_comments


def is_magic(line, seen):
    grps = re.search(r"(3\.14|0\.00\d)", line)
    if grps is None:
        return False
    num = float(grps.group(0))
    if num in seen:
        return False
    seen.add(num)
    macro_grps = re.match(r"^\s*#define", line)
    inline_comment_grps = re.search(r"//", line)
    return macro_grps is None and inline_comment_grps is None


def is_in_except(idx, excepts):
    for start, end in excepts:
        if start > idx:
            break
        if end >= idx:
            return True
    return False


def check(fname, print=print):
    print("> check magic number")
    seen = set()
    err = 0
    lines = open(fname, 'r', errors='ignore').readlines()
    excepts = search_block_comments(lines)
    for idx, line in enumerate(lines):
        if is_magic(line, seen) and not is_in_except(idx, excepts):
            err += 1
            print(f"{err}. magic number found in line {idx+1}")
            print(f" >> {line}")
    print(f"> done with {err} errs")
    return err


if __name__ == "__main__":
    check("Project-1/mtkosmal/trig.c")
