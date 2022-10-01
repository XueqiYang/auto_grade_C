from glob import glob
from style import indent, comment, curlybracket, linebreaker, magicnumber_prj1
from dataclasses import dataclass
import os
import pdb
import pandas as pd
from utils import ConfigBase
import traceback
import sys


@dataclass
class Config(ConfigBase):
    uid_file: str = "unity.csv"
    project_dir: str = "Project-1"
    fname: str = "trig.c"
    report_file: str = "Project-1_grade.csv"
    resume: int = 0
    debug: bool = True


def read_uid(fn):
    uids = []
    with open(fn, 'r') as reader:
        for line in reader:
            uids.append(line.rstrip())
    return uids


def diagnose(action, config, mode='a'):
    uid2cnt = {}
    for idx, uid in enumerate(config.uids):
        if idx < config.resume-1:
            continue
        path = f"{config.project_dir}/{uid}/{config.fname}"
        if not os.path.exists(path):
            print(f"[{idx+1}/{len(config.uids)}] [Error] file not exists in {path}...")
            continue
        try:
            print(f"[{idx+1}/{len(config.uids)}] diagnosing {path}...")
            log_fn = os.path.splitext(path)[0] + ".log"
            with open(log_fn, mode) as writer:
                def write_helper(s):
                    writer.write(s + "\n")
                num_error = action(path, print=write_helper)
            uid2cnt[uid] = num_error
        except Exception as e:
            print(f"[{idx+1}/{len(config.uids)}] [Error] failed to parse file: {path}")
            traceback.print_exc()
            if config.debug:
                break

    return uid2cnt


if __name__ == "__main__":
    # prepare config
    config = Config().parse_args()
    config.uids = read_uid(config.uid_file)
    # generate report
    report = pd.DataFrame({"name": config.uids})

    # print(">> check indention")
    # uid2indent_err = diagnose(indent.check, config, mode='w')
    # report['indent_err'] = report['name'].map(uid2indent_err)

    # print(">> check curlybracket")
    # uid2cmt_curlybracket_err = diagnose(curlybracket.check, config)
    # report['comment_curlybracket_err'] = report['name'].map(uid2cmt_curlybracket_err)

    # print(">> check line breaker")
    # uid2cmt_linebreaker_err = diagnose(linebreaker.check, config)
    # report['comment_linebreaker_err'] = report['name'].map(uid2cmt_linebreaker_err)

    print(">> check magic number")
    uid2cmt_magicnumber_err = diagnose(magicnumber_prj1.check, config)
    report['comment_magicnumber_err'] = report['name'].map(uid2cmt_magicnumber_err)

    # print(">> check heading comments")
    # uid2cmt_head_err = diagnose(comment.check_filehead, config)
    # report['comment_head_err'] = report['name'].map(uid2cmt_head_err)

    # print(">> check comments for macro defination")
    # uid2cmt_macro_err = diagnose(comment.check_before_macro, config)
    # report['comment_macro_err'] = report['name'].map(uid2cmt_macro_err)

    # print(">> check comments for function defination")
    # uid2cmt_func_err = diagnose(comment.check_before_func, config)
    # report['comment_func_err'] = report['name'].map(uid2cmt_func_err)

    # print(">> check param tags inside function comments")
    # uid2cmt_tag_param_err = diagnose(comment.check_tag_param, config)
    # report['comment_tag_param_err'] = report['name'].map(uid2cmt_tag_param_err)

    # print(">> check return tag inside function comments")
    # uid2cmt_tag_return_err = diagnose(comment.check_tag_return, config)
    # report['comment_tag_return_err'] = report['name'].map(uid2cmt_tag_return_err)

    report.to_csv(config.report_file, index=False)
