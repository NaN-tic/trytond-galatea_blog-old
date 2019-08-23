# This file is part galatea_blog module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from mimetypes import guess_type
from datetime import datetime
import os
import hashlib
from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.cache import Cache
from trytond.config import config
from trytond.modules.galatea.tools import slugify, IMAGE_TYPES, thumbly

__all__ = ['Post', 'Comment']


class Post(ModelSQL, ModelView):
    "Blog Post"
    __name__ = 'galatea.blog.post'
    name = fields.Char('Title', translate=True,
        required=True)
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
    visibility = fields.Selection([
            ('public','Public'),
            ('register','Register'),
            ('manager','Manager'),
            ], 'Visibility', required=True)
    galatea_website = fields.Many2One('galatea.website', 'Website',
        domain=[('active', '=', True)], required=True)
    post_create_date = fields.DateTime('Create Date', readonly=True)
    post_write_date = fields.DateTime('Write Date', readonly=True)
    post_published_date = fields.DateTime('Published Date', required=True)
    user = fields.Many2One('galatea.user', 'User', required=True)
    gallery = fields.Boolean('Gallery', help='Active gallery attachments.')
    comment = fields.Boolean('Comment', help='Active comments.')
    comments = fields.One2Many('galatea.blog.comment', 'post', 'Comments')
    total_comments = fields.Function(fields.Integer("Total Comments"),
        'get_totalcomments')
    attachments = fields.One2Many('ir.attachment', 'resource', 'Attachments')
    thumb = fields.Function(fields.Binary('Thumb', filename='thumb_filename'),
        'get_thumb', setter='set_thumb')
    thumb_filename = fields.Char('File Name',
        help='Thumbnail File Name')
    thumb_path = fields.Function(fields.Char('Thumb Path'), 'get_thumb_path')
    _slug_langs_cache = Cache('galatea_blog_post.slug_langs')

    @staticmethod
    def default_active():
        return True

    @staticmethod
    def default_template():
        return 'blog-post.html'

    @staticmethod
    def default_visibility():
        return 'public'

    @classmethod
    def default_galatea_website(cls):
        Website = Pool().get('galatea.website')
        websites = Website.search([('active', '=', True)])
        if len(websites) == 1:
            return websites[0].id

    @classmethod
    def default_user(cls):
        Website = Pool().get('galatea.website')
        websites = Website.search([('active', '=', True)], limit=1)
        if not websites:
            return None
        website, = websites
        if website.blog_anonymous_user:
            return website.blog_anonymous_user.id
        return None

    @staticmethod
    def default_gallery():
        return True

    @staticmethod
    def default_comment():
        return True

    @staticmethod
    def default_post_create_date():
        return datetime.now()

    @staticmethod
    def default_post_published_date():
        return datetime.now()

    @classmethod
    def __setup__(cls):
        super(Post, cls).__setup__()
        cls._order.insert(0, ('post_published_date', 'DESC'))
        cls._order.insert(1, ('name', 'ASC'))
        cls._error_messages.update({
            'delete_posts': ('You can not delete '
                'posts because you will get error 404 NOT Found. '
                'Dissable active field.'),
            'not_file_mime': ('Not know file mime "%(file_name)s"'),
            'not_file_mime_image': ('"%(file_name)s" file mime is not an image ' \
                '(jpg, png or gif)'),
            'image_size': ('Thumb "%(file_name)s" size is larger than "%(size)s"Kb'),
            })

    @fields.depends('name', 'slug')
    def on_change_name(self):
        if self.name and not self.slug:
            self.slug = slugify(self.name)

    @fields.depends('slug')
    def on_change_slug(self):
        if self.slug:
            self.slug = slugify(self.slug)

    @classmethod
    def create(cls, vlist):
        for values in vlist:
            values = values.copy()
            if values.get('slug'):
                slug = slugify(values.get('esale_slug'))
                values['slug'] = slug
        return super(Post, cls).create(vlist)

    @classmethod
    def write(cls, *args):
        now = datetime.now()

        actions = iter(args)
        args = []
        for blogs, values in zip(actions, actions):
            values = values.copy()
            values['post_write_date'] = now
            if values.get('slug'):
                slug = slugify(values.get('slug'))
                values['slug'] = slug
            args.extend((blogs, values))
        return super(Post, cls).write(*args)

    @classmethod
    def copy(cls, posts, default=None):
        new_posts = []
        for post in posts:
            default['slug'] = '%s-copy' % post.slug
            default['blog_create_date'] = datetime.now()
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

    def get_totalcomments(self, name):
        return len(self.comments)

    def get_thumb(self, name):
        db_name = Transaction().database.name
        filename = self.thumb_filename
        if not filename:
            return None
        filename = os.path.join(config.get('database', 'path'), db_name,
            'galatea', 'blog', filename[0:2], filename[2:4], filename)

        value = None
        try:
            with open(filename, 'rb') as file_p:
                value = fields.Binary.cast(file_p.read())
        except IOError:
            pass
        return value

    def get_thumb_path(self, name):
        filename = self.thumb_filename
        if not filename:
            return None
        return '%s/%s/%s' % (filename[:2], filename[2:4], filename)

    @classmethod
    def set_thumb(cls, posts, name, value):
        if value is None:
            return

        Config = Pool().get('galatea.configuration')
        galatea_config = Config(1)
        size = galatea_config.blog_thumb_size or 300
        crop = galatea_config.blog_thumb_crop
        db_name = Transaction().database.name
        galatea_dir = os.path.join(
            config.get('database', 'path'), db_name, 'galatea', 'blog')

        for post in posts:
            file_name = post['thumb_filename']

            file_mime, _ = guess_type(file_name)
            if not file_mime:
                cls.raise_user_error('not_file_mime', {
                        'file_name': file_name,
                        })
            if file_mime not in IMAGE_TYPES:
                cls.raise_user_error('not_file_mime_image', {
                        'file_name': file_name,
                        })

            _, ext = file_mime.split('/')
            digest = '%s.%s' % (hashlib.md5(value).hexdigest(), ext)
            subdir1 = digest[0:2]
            subdir2 = digest[2:4]
            directory = os.path.join(galatea_dir, subdir1, subdir2)
            filename = os.path.join(directory, digest)

            thumb = thumbly(directory, filename, value, size, crop)
            if not thumb:
                cls.raise_user_error('not_file_mime_image', {
                        'file_name': file_name,
                        })
            cls.write([post], {
                'thumb_filename': digest,
                })


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
    comment_create_date = fields.DateTime('Create Date', readonly=True)

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
        websites = Website.search([('active', '=', True)], limit=1)
        if not websites:
            return None
        website, = websites
        if website.blog_anonymous_user:
            return website.blog_anonymous_user.id
        return None

    @staticmethod
    def default_comment_create_date():
        return datetime.now()

    @classmethod
    def copy(cls, comments, default=None):
        default['comment_create_date'] = None
        return super(Comment, cls).copy(comments, default=default)
