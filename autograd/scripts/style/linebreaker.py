import re


def is_windows_break(line):
    return "\r\n" in line


def check(fname, print=print):
    print("> check line breaker")
    num = 0
    with open(fname, 'r', errors='ignore') as reader:
        for idx, line in enumerate(reader):
            if is_windows_break(line):
                num += 1
                print(f"{num}. windows line breaker found in line {idx+1}")
    print(f"> done with {num} errs")
    return num
