# coding=utf-8
from mylibtool.wordpress import custom
from mylibtool.wordpress import files
from mylibtool.wordpress import posts
from mylibtool.wordpress import category


class WpApi:
    def __init__(self, wp_url, wp_user, api_key, wp_user_id=1, default_cat=1, verify=True):
        if wp_url.endswith('/'):
            wp_url = wp_url[:-1]

        self.wp_root_url = wp_url
        self.wp_user = wp_user
        self.wp_user_id = wp_user_id
        self.api_url = f"{wp_url}/wp-json/wp/v2"
        self.api_key = api_key
        self.default_cat_id = default_cat
        self.verify = verify

    def post_file(self, target_file, title):
        return files.post_file(cls=self, target_file=target_file, title=title)

    def post_normal_article(self, article, title, cat_id=1, feature_pic=None, post_type='posts'):
        """
        Rest api post article
        :return:
        """
        return posts.post_normal_article(cls=self, article=article, title=title, cat_id=cat_id, feature_pic=feature_pic, post_type=post_type)

    def submit(self, payload, status='publish', post_type='posts'):
        """
        Submit news to WP
        :param payload: Api data, Can be dict or Addict
        :param status: Post status, publish, pending, draft
        :param post_type: Default is posts, you can post videos, pages, custom post type
        :return: Json/False
        """
        return posts.submit(cls=self, payload=payload, status=status, post_type=post_type)

    def cat_create(self, cat_name, cat_parent_id=0):
        """
        Create a category
        :return: category id
        """
        return category.create(cls=self, cat_name=cat_name, cat_parent_id=cat_parent_id)

    def is_post_exist(self, check_param):
        """Check if already scraped"""
        return custom.check_exist_by_param(self, check_param)
