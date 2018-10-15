#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Wizmann'
SITENAME = u"Maerlyn's Rainbow"
SITEURL = 'http://wizmann.tk'

PATH = 'content'

TIMEZONE = 'Asia/Shanghai'

DEFAULT_LANG = u'zhs'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = 'feeds/all.rss.xml'
CATEGORY_FEED_ATOM = 'feeds/%s.rss.xml'
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None


PYGMENTS_STYLE = "solarizedlight"

# Blogroll
LINKS =  (
             ('Pelican', 'http://getpelican.com/'),
         )

# Social widget
SOCIAL = (('github', 'https://github.com/wizmann'),
          ('rss', 'http://wizmann.tk/feeds/all.rss.xml'),
         )

DEFAULT_PAGINATION = 10

THEME = 'pelican-themes/pelican-bootstrap3'
DISQUS_SITENAME = u'wizmann'
DEFAULT_DATE_FORMAT = ('%Y-%m-%d')

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True

PLUGIN_PATH = ["pelican-plugins"]
PLUGINS = ["sitemap", "summary", 'tag_cloud', 'i18n_subsites']

JINJA_ENVIRONMENT = {
    'extensions': ['jinja2.ext.i18n'],
}

SITEMAP = {
    "format": "xml",
    "priorities": {
        "articles": 0.7,
        "indexes": 0.5,
        "pages": 0.3,
    },
    "changefreqs": {
        "articles": "monthly",
        "indexes": "daily",
        "pages": "monthly",
    }
}
