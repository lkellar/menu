import dominate
from dominate.tags import *
from dominate.util import raw
from datetime import datetime


def genHTML(data, urlRoot, date):

    keys = sorted(data.keys())
    menus = sorted(data.values(), key=lambda x: x[0])

    today = keys.index(date.strftime('%Y-%m-%d'))

    before = menus[:today]
    current = [menus[today]]
    after = menus[today+1:]

    keys = keys[:today+1] + keys[today+1:][::-1]

    doc = dominate.document('Menu')

    menuLists = {'before': before, 'current': current, 'after': after}

    with doc.head:
        link(rel='stylesheet', href='{}static/style.css'.format(urlRoot), type='text/css')

    with doc:
        link(rel='stylesheet', href='{}static/style.css'.format(urlRoot), type='text/css')
        img(_class='arrow', id='left', src='{}static/assets/left.svg'.format(urlRoot))
        img(_class='arrow', id='right', src='{}static/assets/right.svg'.format(urlRoot))
        with div(id='main'):
            iteration = 0
            for x in ['before', 'current', 'after']:
                for i in menuLists[x]:
                    with div(_class='day {}'.format(x)):
                        h2(datetime.strptime(keys[iteration], '%Y-%m-%d').strftime('%A, %B %d, %Y'))
                        with ul():
                            for z in i:
                                if z.startswith('\n'):
                                    h3(z)
                                else:
                                    li(z)
                    iteration += 1
        footer(raw(
            '<p>Arrows made by <a href="https://fontawesome.com">Font Awesome</a>.\n<a href="https://fontawesome.com/license/free">License</a>. No changes to images were made.'))
        script(type='text/javascript', src='{}static/script.js'.format(urlRoot))
    return doc.render()
