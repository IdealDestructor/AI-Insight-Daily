#!/usr/bin/env python3
"""
在构建阶段清理每日 Markdown 文件中不需要的重复内容。

当前策略：
1. 删除包含“访问网页版”与“进群交流”链接的整行引用。
2. 删除“AI资讯日报语音版”段落以及其下方的语音播报表格。
"""

from __future__ import annotations

import argparse
import pathlib
from typing import Iterable


def strip_unwanted_sections(text: str) -> str:
    lines = text.splitlines()
    cleaned: list[str] = []
    i = 0
    total = len(lines)

    while i < total:
        line = lines[i]

        # 规则 1：删除推广引用行
        if "访问网页版" in line and "进群交流" in line:
            i += 1
            continue

        # 规则 2：删除语音版段落与表格
        if line.strip() == "## **AI资讯日报语音版**":
            i += 1
            # 跳过标题与表格之间的空行
            while i < total and not lines[i].strip():
                i += 1

            # 跳过表格 (以 | 开头的行) 以及包含表格图片的行
            while i < total and (
                lines[i].lstrip().startswith("|") or lines[i].lstrip().startswith("![")
            ):
                i += 1

            # 跳过表格后的空行，保持上下文整洁
            while i < total and not lines[i].strip():
                i += 1
            continue

        cleaned.append(line)
        i += 1

    return "\n".join(cleaned) + ("\n" if text.endswith("\n") else "")


def iter_markdown_files(target: pathlib.Path) -> Iterable[pathlib.Path]:
    for path in target.rglob("*.md"):
        if path.is_file():
            yield path


def process_path(target: pathlib.Path) -> None:
    if target.is_file() and target.suffix == ".md":
        files = [target]
    elif target.is_dir():
        files = list(iter_markdown_files(target))
    else:
        raise ValueError(f"无法处理路径: {target}")

    for file_path in files:
        original = file_path.read_text(encoding="utf-8")
        updated = strip_unwanted_sections(original)
        if updated != original:
            file_path.write_text(updated, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="移除 Markdown 中的推广引用和语音版段落内容"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="需要清理的文件或目录 (默认: 当前目录)",
    )
    args = parser.parse_args()
    process_path(pathlib.Path(args.path).resolve())


if __name__ == "__main__":
    main()

