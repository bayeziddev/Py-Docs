#!/usr/bin/env python
"""Update test expected output files based on current implementation."""

import os
import sys
import markdown
import difflib
from tests import util

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

CSS_LINK = '<link rel="stylesheet" type="text/css" href="%s"/>'
WRAPPER = '''<!DOCTYPE html>
<head>
<meta charset="utf-8">
%s
</head>
<body>
<div class="markdown-body">
%%s
</div>
</body>
'''


def check_markdown(testfile, extension, extension_config, wrapper):
    """Check and update the markdown expected output."""
    expected_html = os.path.splitext(testfile)[0] + '.html'
    with open(testfile, 'r', encoding='utf-8') as f:
        source = f.read()

    results = wrapper % markdown.Markdown(
        extensions=extension, extension_configs=extension_config
    ).convert(source)

    print(f'Updating: {expected_html}')
    with open(expected_html, 'w', encoding='utf-8') as f:
        f.write(results)


def compare_results(cfg, testfile):
    """Compare and update test results."""
    extension = []
    extension_config = {}
    wrapper = "%s"
    for k, v in cfg['extensions'].items():
        extension.append(k)
        if v:
            extension_config[k] = v
    if 'css' in cfg and len(cfg['css']):
        wrapper = WRAPPER % '\n'.join([CSS_LINK % css for css in cfg['css']])

    check_markdown(testfile, extension, extension_config, wrapper)


def gather_test_params():
    """Gather the test parameters."""
    test_dir = os.path.join(CURRENT_DIR, 'tests')
    for base, dirs, files in os.walk(test_dir):
        [dirs.remove(d) for d in dirs[:] if d.startswith('_')]
        cfg_path = os.path.join(base, 'tests.yml')
        if os.path.exists(cfg_path):
            files.remove('tests.yml')
            [files.remove(file) for file in files[:] if not file.endswith('.txt')]
            with open(cfg_path, 'r', encoding='utf-8') as f:
                cfg = util.yaml_load(f.read())
            for testfile in files:
                key = os.path.splitext(testfile)[0]
                test_cfg = {}
                test_cfg.update(cfg.get('__default__', {}))
                if 'extensions' not in test_cfg:
                    test_cfg['extensions'] = util.OrderedDict()
                if 'css' not in test_cfg:
                    test_cfg['css'] = []
                for k, v in cfg.get(key, util.OrderedDict()).items():
                    if k == 'css':
                        for css in v:
                            test_cfg[k].append(css)
                        continue
                    if k not in test_cfg:
                        test_cfg[k] = {}
                    for k1, v1 in v.items():
                        if v1 is not None:
                            for k2, v2 in v1.items():
                                if isinstance(v2, str):
                                    v1[k2] = v2.replace(
                                        '{{BASE}}', base
                                    ).replace(
                                        '{{RELATIVE}}', test_dir
                                    )
                                elif k2 == 'base_path' and isinstance(v2, list):
                                    for i, v3 in enumerate(v2, 0):
                                        v1[k2][i] = v3.replace(
                                            '{{BASE}}', base
                                        ).replace(
                                            '{{RELATIVE}}', test_dir
                                        )
                        test_cfg[k][k1] = v1
                yield test_cfg, os.path.join(base, testfile)


if __name__ == '__main__':
    print("Updating all test expected output files...")
    for test_cfg, testfile in gather_test_params():
        try:
            compare_results(test_cfg, testfile)
        except Exception as e:
            print(f"Error processing {testfile}: {e}")
    print("Done!")
