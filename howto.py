import os
import sys
import shutil
import hashlib
import argparse

import xapian

class SyntaxError(Exception):
    pass

def parse_notes(fname):
    state = 'closed'
    title, content = None, None
    notes = []
    
    for lineno, line in enumerate(open(fname)):
        line = line.rstrip()
        if state == 'closed':
            if title and content:
                notes.append((title, content, (start, end)))
            title = []
            if line.startswith('*'):
                title.append(line[1:].strip())
                state = 'saw_title'
                start = lineno
            elif not line: # multi blank lines between notes
                pass
            else:
                raise SyntaxError("lineno:%d:expect title" % (lineno+1))
        elif state == 'saw_title':
            if line.startswith('*'):
                title.append(line[1:].strip())
            else:
                content = [line]
                state = 'saw_content'
        elif state == 'saw_content':
            if line:
                content.append(line)
            else: # a blank line will close a note
                state = 'closed'
                end = lineno

    if title and content:
        end = lineno + 1
        notes.append((title, content, (start, end)))

    return notes


def make_index(dbpath, notes):
    db = xapian.WritableDatabase(dbpath, xapian.DB_CREATE_OR_OPEN)

    termgenerator = xapian.TermGenerator()
    termgenerator.set_stemmer(xapian.Stem("en"))

    for title, content, (start, end) in notes:
        doc = xapian.Document()
        termgenerator.set_document(doc)

        text = ' '.join(title) + ' '.join(content)
        termgenerator.index_text(text)

        doc.set_data('%d,%d' % (start, end))

        id_ = hashlib.md5(text).hexdigest()
        idterm = u"Q" + id_
        doc.add_boolean_term(idterm)
        db.replace_document(idterm, doc)


def search(dbpath, notespath, querystring, offset=0, count=1):
    db = xapian.Database(dbpath)

    queryparser = xapian.QueryParser()
    queryparser.set_stemmer(xapian.Stem("en"))
    queryparser.set_stemming_strategy(queryparser.STEM_SOME)

    query = queryparser.parse_query(querystring)

    enquire = xapian.Enquire(db)
    enquire.set_query(query)

    notes = open(notespath).readlines()
    for match in enquire.get_mset(offset, count):
        pos = match.document.get_data()
        start, end = [ int(i) for i in pos.split(',', 1) ]
        print '[{}:{}] {}'.format(start, end, notespath)
        print ''.join([ i for i in notes[start:end] if i.strip() ])


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--rebuild-index', action='store_true')
    parser.add_argument('-d', '--db-path',
                        default=os.path.expanduser('~/.howto/db'))
    parser.add_argument('-N', '--notes-path',
                        default=os.path.expanduser('~/.howto/notes.txt'))
    parser.add_argument('-y', '--yes', action='store_true')
    parser.add_argument('-n', '--number', default=1, type=int)
    parser.add_argument('keywords', nargs='*')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    if args.rebuild_index:
        if os.path.exists(args.db_path):
            if args.yes or \
                    raw_input('db exists, delete it first (N/y)? ').lower() in ('y', 'yes'):
                shutil.rmtree(args.db_path)
            else:
                print 'please handle it manually, exiting...'
                sys.exit(0)
        make_index(args.db_path, parse_notes(args.notes_path))
    else:
        search(args.db_path, args.notes_path, ' '.join(args.keywords), count=args.number)
