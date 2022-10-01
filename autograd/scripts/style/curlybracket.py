import re
from pycparser import c_ast, parse_file


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


def check(fname, print=print):
    print("> check bracket placement")
    lines = open(fname, 'r', errors='ignore').readlines()
    func_start, _, _ = search_func_def(fname)
    err = 0
    for f_start in func_start:
        if '{' in lines[f_start]:
            err += 1
            print(f"{err}. bracket mis-placement in the same line of func def in line {f_start+1}")
    print(f"> done with {err} errs")
    return err
