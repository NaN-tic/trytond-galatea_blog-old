#This file is part galatea_blog module for Tryton.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.
from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.cache import Cache
from .tools import slugify

__all__ = ['Post', 'Comment']


class Post(ModelSQL, ModelView):
    "Blog Post"
    __name__ = 'galatea.blog.post'
    name = fields.Char('Title', translate=True,
        required=True, on_change=['name', 'slug'])
    slug = fields.Char('slug', required=True, translate=True,
        help='Cannonical uri.')
    slug_langs = fields.Function(fields.Dict(None, 'Slug Langs'), 'get_slug_langs')
    description = fields.Text('Description', required=True, translate=True,
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
    blog_create_date = fields.Function(fields.Char('Create Date'),
        'get_blog_create_date')
    blog_write_date = fields.Function(fields.Char('Write Date'),
        'get_blog_write_date')
    create_uid = fields.Many2One('res.user', 'User Create', readonly=True)
    write_uid = fields.Many2One('res.user', 'Write Create', readonly=True)
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

    @classmethod
    def __setup__(cls):
        super(Post, cls).__setup__()
        cls._order.insert(0, ('create_date', 'DESC'))
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
    def copy(cls, posts, default=None):
        new_posts = []
        for post in posts:
            default['slug'] = '%s-copy' % post.slug
            new_post, = super(Post, cls).copy([post], default=default)
            new_posts.append(new_post)
        return new_posts

    @classmethod
    def delete(cls, posts):
        cls.raise_user_error('delete_posts')

    def get_slug_langs(self, name):
        '''Return dict slugs by all languaes actives'''
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

    @classmethod
    def get_blog_create_date(cls, records, name):
        """Returns create date of current blog"""
        res = {}
        DATE_FORMAT = '%s %s' % (Transaction().context['locale']['date'], '%H:%M:%S')
        for record in records:
            res[record.id] = record.create_date.strftime(DATE_FORMAT) or ''
        return res

    @classmethod
    def get_blog_write_date(cls, records, name):
        """Returns write date of current blog"""
        res = {}
        DATE_FORMAT = '%s %s' % (Transaction().context['locale']['date'], '%H:%M:%S')
        for record in records:
            res[record.id] = record.write_date and record.write_date.strftime(DATE_FORMAT) or ''
        return res


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
        """Returns create date of current blog"""
        res = {}
        DATE_FORMAT = '%s %s' % (Transaction().context['locale']['date'], '%H:%M:%S')
        for record in records:
            res[record.id] = record.create_date.strftime(DATE_FORMAT) or ''
        return res
