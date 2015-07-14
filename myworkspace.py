#!/usr/bin/env python
# coding: utf-8

import sh
import os
from operator import getitem
from contextlib import contextmanager


class options:
    items_per_line = 3
    tab = 2


def get_node_type(name):
    if os.path.isdir(name):
        return 'dir'
    elif os.path.isfile(name):
        return 'file'
    else:
        raise TypeError('WTF is this %s' % name)


@contextmanager
def cdctx(path):
    os.chdir(path)
    yield
    os.chdir('..')


class Node(object):
    def __init__(self, name):
        if isinstance(name, unicode):
            name = name.encode('utf8')
        self.name = name
        self.type = get_node_type(name)
        self.is_git = None
        self.pushed = None

    def _ensure_type(self, type):
        if type != self.type:
            raise TypeError('Should be type %s to perform' % type)

    def check_git(self):
        self._ensure_type('dir')
        with cdctx(self.name):
            if os.path.exists('.git'):
                self.is_git = True
                uncleared = sh.git('status', '--porcelain').strip()
                if uncleared:
                    self.pushed = False
                else:
                    self.pushed = True
            else:
                self.is_git = False

    def __str__(self):
        is_git = 'git' if self.is_git is True else ''
        if self.pushed is True:
            pushed = 'pushed'
        elif self.pushed is False:
            pushed = 'not pushed'
        else:
            pushed = ''
        return '<{type} {name}, {is_git}, {pushed}>'.format(
            type=self.type, name=self.name,
            is_git=is_git, pushed=pushed
        )


class NodeList(object):
    def __init__(self, *paths):
        nodes = {}
        for path in paths:
            last_item = nodes
            for i in path.split('/'):
                last_item.setdefault(i, [])
        print nodes
        self.nodes = nodes

    @staticmethod
    def _getitem_by_path(d, path):
        return d


def list_nodes():
    for i in sh.ls('-1'):
        name = i.strip()
        yield Node(name)


def echo(s, indent=None, prefix=None):
    if prefix:
        s = prefix + s
    if indent:
        s = ' ' * indent + s

    if isinstance(s, unicode):
        s = s.encode('utf8')
    print s


def echo_nodes(nodes, indent=None, prefix='│ '):
    lines = []
    col_max_widths = [0 for x in xrange(options.items_per_line)]
    line_buf = []

    for i, node in enumerate(nodes):
        line_buf.append(node.name)

        pos = i % options.items_per_line
        text_len = len(node.name)
        if col_max_widths[pos] < text_len:
            col_max_widths[pos] = text_len

        if len(line_buf) >= options.items_per_line:
            #line = '\t'.join(line_buf)
            #echo(line, indent, prefix)
            lines.append(line_buf)
            line_buf = []

    if line_buf:
        # Fix line_buf length to be exact the same as items_per_line
        line_buf.extend((options.items_per_line - len(line_buf)) * [''])
        lines.append(line_buf)

    # Echo lines
    padding = 2
    line_tpl = ''.join('{:<%s}' % (i + padding) for i in col_max_widths)
    for line in lines:
        line_str = line_tpl.format(*line)
        echo(line_str, indent, prefix)

    #col_width = max(len(word) for line in lines for word in line) + 2  # 2 is padding
    #for line in lines:
    #    line_str = "".join(word.ljust(col_width) for word in line)
    #    echo(line_str, indent, prefix)

    #widths = [max(map(len, col)) for col in zip(*lines)]
    #for row in table:
        #print('  '.join((val.ljust(width) for val, width in zip(row, widths))))


def main():
    echo('Scanning..\n')
    nodes = {
        'file': [],
        'dir': {
            'git': {
                'pushed': [],
                '_': []
            },
            '_': []
        }
    }

    for node in list_nodes():
        if node.type == 'dir':
            node.check_git()

            if node.is_git:
                if node.pushed:
                    nodes['dir']['git']['pushed'].append(node)
                else:
                    nodes['dir']['git']['_'].append(node)
            else:
                nodes['dir']['_'].append(node)
        else:
            nodes['file'].append(node)

    # Show them all
    tab = options.tab

    current = nodes['file']
    echo('Files (%s):' % len(current))
    echo_nodes(current, tab)
    echo('')

    #
    echo('Directories:')
    # #
    echo('Git:', tab)
    # ##
    current = nodes['dir']['git']['pushed']
    echo('Pushed (%s):', tab * 2)
    echo_nodes(current, tab * 2)
    echo('')
    # ##
    echo('Not pushed', tab * 2)
    echo_nodes(nodes['dir']['git']['_'], tab * 2)
    echo('')
    # #
    echo('Normal:', tab)
    echo_nodes(nodes['dir']['_'], tab)


if __name__ == '__main__':
    main()
