# This file is part galatea_blog module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta

__all__ = ['Configuration']
__metaclass__ = PoolMeta


class Configuration:
    __name__ = 'galatea.configuration'
    blog_thumb_size = fields.Integer('Blog Thumb Size',
        help='Thumbnail Blog Image Size (width x height)')
    blog_thumb_crop = fields.Boolean('Blog Thumb Crop',
        help='Crop Thumb Blog Image')

    @staticmethod
    def default_blog_thumb_size():
        return 300
