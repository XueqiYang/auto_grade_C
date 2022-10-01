import re


def is_tab(line):
    grps = re.match("^\s+", line)
    return grps is not None and '\t' in grps[0]


def check(fname, print=print):
    print("> check indent")
    num = 0
    with open(fname, 'r', errors='ignore') as reader:
        for idx, line in enumerate(reader):
            if is_tab(line):
                num += 1
                print(f"{num}. leading tab found in line {idx+1}")
    print(f"> done with {num} errs")
    return num
