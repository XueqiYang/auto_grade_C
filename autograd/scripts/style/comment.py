import pdb
import re
from pycparser import c_ast, parse_file


def search_block_comments(lines):
    positions = []
    start = None
    for idx, line in enumerate(lines):
        # there could be issue when multiple
        # block comments exist in one lines
        # but we skip it for convenience
        if start is None and \
                re.match("^\s*/\*", line) is not None:
            start = idx
        if start is not None and \
                re.search("\*/\s*$", line) is not None:
            positions.append((start, idx))
            start = None
    return positions


def search_oneline_comment(lines):
    starts = []
    for idx, line in enumerate(lines):
        if re.search("//", line):
            starts.append(idx)
    return starts


class FuncDefVisitor(c_ast.NodeVisitor):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.linenos = []
        self.paramnos = []
        self.returns = []

    def visit_FuncDef(self, node):
        func = node.decl
        self.linenos.append(func.coord.line-1)
        self.paramnos.append(
            len(func.type.args.params) if
            func.type.args else 0)
        self.returns.append(
            func.type.type.type.names[0] != 'void')


def search_func_def(fname):
    ast = parse_file(fname, use_cpp=True,
                     cpp_path='gcc',
                     cpp_args=['-E', '-std=c99', '-nostdinc', r'-Iscripts/pycparser/utils/fake_libc_include'])
    # cpp_args=['-E', r'-Iscripts/pycparser/utils/fake_libc_include'])
    v = FuncDefVisitor()
    v.visit(ast)
    return v.linenos, v.paramnos, v.returns


def search_macro_def(lines):
    starts = []
    for idx, line in enumerate(lines):
        grps = re.match("^\s*#define", line)
        if grps is not None:
            starts.append(idx)
    return starts

# TODO
def is_blank_lines(lines):
    for line in lines:
        if not re.match("^\s+", line):
            return False
    return True


def is_contain_return_tag(lines):
    for line in lines:
        groups = re.search("@return", line)
        if groups:
            return True
    return False


def count_param_tag(lines):
    cnt = 0
    for line in lines:
        groups = re.search("@param", line)
        cnt += 1 if groups else 0
    return cnt


def validate_param_tag_before_func(func_start, func_paramno, blk_comment_pos, lines, print=print):
    # check if blk comment exists before func
    tag_param_err = 0
    for f_start, f_param in zip(func_start, func_paramno):
        c_pos = (-1, -1)
        # search the closest blk comment above func
        for c_start, c_end in blk_comment_pos:
            if c_end < f_start:
                c_pos = (c_start, c_end)
            else:
                break
        # if block comment not exist, skip
        c_start, c_end = c_pos
        if c_end == -1:
            continue
        # check if it really associated to the func
        if not is_blank_lines(lines[c_end + 1:f_start]):
            continue
        # now it is a valid block comment
        # and we go into tag checking
        lines_sel = lines[c_start:c_end+1]
        if f_param > count_param_tag(lines_sel):
            tag_param_err += 1
            print(f"{tag_param_err}. Insuffient @param tags in lines of {c_start+1}-{c_end+1} for function in line {f_start+1}")

    return tag_param_err


def validate_return_tag_before_func(func_start, func_return, blk_comment_pos, lines, print=print):
    # check if blk comment exists before func
    tag_return_err = 0
    for f_start, f_return in zip(func_start, func_return):
        c_pos = (-1, -1)
        # search the closest blk comment above func
        for c_start, c_end in blk_comment_pos:
            if c_end < f_start:
                c_pos = (c_start, c_end)
            else:
                break
        # if block comment not exist, skip
        c_start, c_end = c_pos
        if c_end == -1:
            continue
        # check if it really associated to the func
        if not is_blank_lines(lines[c_end + 1:f_start]):
            continue
        # now it is a valid block comment
        # and we go into tag checking
        lines_sel = lines[c_start:c_end+1]
        if f_return and not is_contain_return_tag(lines_sel):
            tag_return_err += 1
            print(f"{tag_return_err}. Insuffient @return tags in lines of {c_start+1}-{c_end+1} for function in line {f_start+1}")

    return tag_return_err


def validate_block_comment_before_func(func_start, blk_comment_pos, lines, print=print):
    # check if blk comment exists before func
    blk_cmt_err = 0
    for f_start in func_start:
        c_pos = (-1, -1)
        # search the closest blk comment above func
        for c_start, c_end in blk_comment_pos:
            if c_end < f_start:
                c_pos = (c_start, c_end)
            else:
                break
        # if not exist, an error
        c_start, c_end = c_pos
        if c_end == -1:
            blk_cmt_err += 1
            print(f"{blk_cmt_err}. Lack of blockwsie comments for function in line {f_start+1}")
            continue
        # check if it really associated to the func
        if not is_blank_lines(lines[c_end + 1:f_start]):
            blk_cmt_err += 1
            print(f"{blk_cmt_err}. Lack of blockwsie comments for function in line {f_start+1}")
            continue
        # now it is a valid block comment
    return blk_cmt_err


def validate_comment_before_macro_def(blk_comment_pos, oneline_comment_pos, const_def_start, lines, print=print):
    cmt_err = 0
    for m_start in const_def_start:
        c_end = -1
        for cs, ce in blk_comment_pos:
            if ce <= m_start:
                c_end = ce
            else:
                break
        for ce in oneline_comment_pos:
            if ce <= m_start:
                c_end = max(c_end, ce)
            else:
                break
        if c_end == -1:
            cmt_err += 1
            print(f"{cmt_err}. Lack of comments for macro define in line {m_start+1}")
            continue
        # check if it really associated to the macro def
        if not is_blank_lines(lines[c_end + 1:m_start]):
            cmt_err += 1
            continue
        # now it is a valid comment before macro def
    return cmt_err


def check_before_func(fname, print=print):
    print(f"> check absence of block comments")
    func_start, _, _ = search_func_def(fname)
    lines = open(fname, 'r', errors='ignore').readlines()
    blk_comment_pos = search_block_comments(lines)
    cmt_err_func = validate_block_comment_before_func(
        func_start,
        blk_comment_pos,
        lines,
        print)
    print(f"> done with {cmt_err_func} errs")
    return cmt_err_func


def check_tag_return(fname, print=print):
    print(f"> check return tag absence in block comments")
    func_start, func_paramno, func_return = search_func_def(fname)
    lines = open(fname, 'r', errors='ignore').readlines()
    blk_comment_pos = search_block_comments(lines)
    tag_return_err = validate_return_tag_before_func(
        func_start,
        func_return,
        blk_comment_pos,
        lines,
        print)
    print(f"> done with {tag_return_err} errs")
    return tag_return_err


def check_tag_param(fname, print=print):
    print(f"> check param tag absence in block comments")
    func_start, func_paramno, func_return = search_func_def(fname)
    lines = open(fname, 'r', errors='ignore').readlines()
    blk_comment_pos = search_block_comments(lines)
    tag_param_err = validate_param_tag_before_func(
        func_start,
        func_paramno,
        blk_comment_pos,
        lines,
        print)
    print(f"> done with {tag_param_err} errs")
    return tag_param_err


def check_before_macro(fname, print=print):
    print(f"> check comment absence before macro define")
    lines = open(fname, 'r', errors='ignore').readlines()
    blk_comment_pos = search_block_comments(lines)
    const_def_start = search_macro_def(lines)
    oneline_comment_pos = search_oneline_comment(lines)
    cmt_err_macro = validate_comment_before_macro_def(
        blk_comment_pos,
        oneline_comment_pos,
        const_def_start,
        lines,
        print)
    print(f"> done with {cmt_err_macro} errs")
    return cmt_err_macro


def check_filehead(fname, print=print):
    print(f"> check comment absence in the begining of file")
    lines = open(fname, 'r', errors='ignore').readlines()
    blk_comment_pos = search_block_comments(lines)
    oneline_comment_pos = search_oneline_comment(lines)
    # if no comment return 1 err
    if len(blk_comment_pos) + len(oneline_comment_pos) == 0:
        print("lack of heading comment")
        return 1
    # else the comment is not in the beginning
    cs = min(blk_comment_pos[0][0] if blk_comment_pos else 0,
             oneline_comment_pos[0] if oneline_comment_pos else 0)
    if is_blank_lines(lines[:cs]):
        print(f"> done with 0 errs")
        return 0
    else:
        print("lack of heading comment")
        return 1
