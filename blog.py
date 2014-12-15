# This file is part galatea_blog module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.cache import Cache
from .tools import slugify
from datetime import datetime

__all__ = ['Post', 'Comment']


class Post(ModelSQL, ModelView):
    "Blog Post"
    __name__ = 'galatea.blog.post'
    name = fields.Char('Title', translate=True,
        required=True, on_change=['name', 'slug'])
    slug = fields.Char('slug', required=True, translate=True,
        help='Cannonical uri.')
    slug_langs = fields.Function(fields.Dict(None, 'Slug Langs'), 'get_slug_langs')
    uri = fields.Function(fields.Char('Uri'), 'get_uri')
    description = fields.Text('Description', required=True, translate=True,
        help='You could write wiki markup to create html content. Formats text following '
        'the MediaWiki (http://meta.wikimedia.org/wiki/Help:Editing) syntax.')
    long_description = fields.Text('Long Description', translate=True,
        help='You could write wiki markup to create html content. Formats text following '
        'the MediaWiki (http://meta.wikimedia.org/wiki/Help:Editing) syntax.')
    metadescription = fields.Char('Meta Description', translate=True, 
        help='Almost all search engines recommend it to be shorter ' \
        'than 155 characters of plain text')
    metakeywords = fields.Char('Meta Keywords',  translate=True,
        help='Separated by comma')
    metatitle = fields.Char('Meta Title',  translate=True)
    template = fields.Char('Template', required=True)
    active = fields.Boolean('Active',
        help='Dissable to not show content post.')
    galatea_website = fields.Many2One('galatea.website', 'Website',
        domain=[('active', '=', True)], required=True)
    post_create_date = fields.DateTime('Create Date', readonly=True)
    post_write_date = fields.DateTime('Write Date', readonly=True)
    create_uid = fields.Many2One('res.user', 'User Create', readonly=True)
    write_uid = fields.Many2One('res.user', 'Write Create', readonly=True)
    gallery = fields.Boolean('Gallery', help='Active gallery attachments.')
    comment = fields.Boolean('Comment', help='Active comments.')
    comments = fields.One2Many('galatea.blog.comment', 'post', 'Comments')
    attachments = fields.One2Many('ir.attachment', 'resource', 'Attachments')
    _slug_langs_cache = Cache('galatea_blog_post.slug_langs')

    @staticmethod
    def default_active():
        return True

    @staticmethod
    def default_template():
        return 'blog-post.html'

    @classmethod
    def default_galatea_website(cls):
        Website = Pool().get('galatea.website')
        websites = Website.search([('active', '=', True)])
        if len(websites) == 1:
            return websites[0].id

    @staticmethod
    def default_gallery():
        return True

    @staticmethod
    def default_comment():
        return True

    @classmethod
    def __setup__(cls):
        super(Post, cls).__setup__()
        cls._order.insert(0, ('post_create_date', 'DESC'))
        cls._order.insert(1, ('id', 'DESC'))
        cls._error_messages.update({
            'delete_posts': ('You can not delete '
                'posts because you will get error 404 NOT Found. '
                'Dissable active field.'),
            })

    def on_change_name(self):
        res = {}
        if self.name and not self.slug:
            res['slug'] = slugify(self.name)
        return res

    @classmethod
    def create(cls, vlist):
        now = datetime.now()
        vlist = [x.copy() for x in vlist]
        for vals in vlist:
            vals['post_create_date'] = now
        return super(Post, cls).create(vlist)

    @classmethod
    def write(cls, *args):
        now = datetime.now()

        actions = iter(args)
        args = []
        for blogs, values in zip(actions, actions):
            values = values.copy()
            values['post_write_date'] = now
            args.extend((blogs, values))
        return super(Post, cls).write(*args)

    @classmethod
    def copy(cls, posts, default=None):
        new_posts = []
        for post in posts:
            default['slug'] = '%s-copy' % post.slug
            default['blog_create_date'] = None
            default['blog_write_date'] = None
            new_post, = super(Post, cls).copy([post], default=default)
            new_posts.append(new_post)
        return new_posts

    @classmethod
    def delete(cls, posts):
        cls.raise_user_error('delete_posts')

    def get_slug_langs(self, name):
        'Return dict slugs for each active languages'
        pool = Pool()
        Lang = pool.get('ir.lang')
        Post = pool.get('galatea.blog.post')

        post_id = self.id
        langs = Lang.search([
            ('active', '=', True),
            ('translatable', '=', True),
            ])

        slugs = {}
        for lang in langs:
            with Transaction().set_context(language=lang.code):
                post, = Post.read([post_id], ['slug'])
                slugs[lang.code] = post['slug']

        return slugs

    def get_uri(self, name):
        if self.galatea_website:
            locale = Transaction().context.get('language', 'en')
            return '%s%s/blog/%s' % (
                self.galatea_website.uri,
                locale[:2],
                self.slug,
                )
        return ''


class Comment(ModelSQL, ModelView):
    "Blog Comment Post"
    __name__ = 'galatea.blog.comment'
    post = fields.Many2One('galatea.blog.post', 'Post', required=True)
    user = fields.Many2One('galatea.user', 'User', required=True)
    description = fields.Text('Description', required=True,
        help='You could write wiki markup to create html content. Formats text following '
        'the MediaWiki (http://meta.wikimedia.org/wiki/Help:Editing) syntax.')
    active = fields.Boolean('Active',
        help='Dissable to not show content post.')
    comment_create_date = fields.Function(fields.Char('Create Date'),
        'get_comment_create_date')

    @classmethod
    def __setup__(cls):
        super(Comment, cls).__setup__()
        cls._order.insert(0, ('create_date', 'DESC'))
        cls._order.insert(1, ('id', 'DESC'))

    @staticmethod
    def default_active():
        return True

    @classmethod
    def default_user(cls):
        Website = Pool().get('galatea.website')
        websites = Website.search([('active', '=', True)])
        if len(websites) == 1:
            if websites[0].blog_anonymous_user:
                return websites[0].blog_anonymous_user.id

    @classmethod
    def get_comment_create_date(cls, records, name):
        'Created domment date'
        res = {}
        DATE_FORMAT = '%s %s' % (Transaction().context['locale']['date'], '%H:%M:%S')
        for record in records:
            res[record.id] = record.create_date.strftime(DATE_FORMAT) or ''
        return res
