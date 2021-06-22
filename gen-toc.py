"""Generate TOC for index page"""
import os

__HERE__ = os.path.dirname(os.path.realpath(__file__))

def gen_toc(mkdocsyml):
    nav = False
    indent = None
    out = ['## Table of Contents', '']
    with open(mkdocsyml) as fyml:
        for line in fyml:
            if line.strip() == 'nav:':
                nav = True
            elif line[:1] not in (' ', '\t'):
                nav = False
            elif nav and indent is None:
                indent = line.split('-', 1)[0]

            if nav and line.startswith(f'{indent}-'):
                title, mdfile = line[len(indent)+1:].strip().split(':', 1)
                title = title.strip().strip('\'"')
                mdfile = mdfile.strip().strip('\'"')
                if title == 'Home':
                    continue
                url = f'https://pwwang.github.io/datar-blog/{mdfile[:-3]}.html'
                mdfile = os.path.join(__HERE__, 'posts', mdfile)
                out.append(f'- [{title}]({url})')
    return out

if __name__ == '__main__':
    mkdocsyml = os.path.join(__HERE__, 'mkdocs.yml')
    toc = gen_toc(mkdocsyml)
    print('\n'.join(toc) + '\n')
