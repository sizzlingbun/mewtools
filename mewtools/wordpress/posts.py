import json

from mylibtool.wordpress import files
from loguru import logger
from carehttp import Carehttp


def post_normal_article(cls, article, title, cat_id=1, feature_pic=None, post_type='posts'):
    """
    Rest api post article
    :param article: an addict param
    :return: (post id, post link)
    """
    if feature_pic:
        # upload if need feature pic
        wp_file = files.post_file(
            cls=cls,
            target_file=feature_pic,
            title=title
        )

        if not wp_file:
            logger.error(f'upload pic: {title} failed')
            return False

        file_id, file_url = wp_file

        article.featured_media = file_id

    try:
        # submit a post
        article.categories = cat_id
        json_data = submit(cls=cls, payload=article, post_type=post_type)

        if json_data and isinstance(json_data, dict):
            logger.success(f'Submit {title} succeed')
            return json_data['id']

    except Exception as e:
        logger.error(f'Submit {title} failed: {e}')
        return


def submit(cls, payload, status='publish', post_type='posts'):
    """
    Submit posts to WP
    """
    api_url = f'{cls.api_url}/{post_type}'

    # Add basic params to payload
    payload['status'] = status
    payload['author'] = cls.wp_user_id

    logger.debug(f"Submit Article: {payload['title']}")

    r = Carehttp(payload['title'], tries=8).post(url=api_url,
                                                 data=json.dumps(payload),
                                                 headers={'content-type': "Application/json"},
                                                 auth=(cls.wp_user, cls.api_key),
                                                 verify=cls.verify
                                                 )

    if r.status_code == 201:
        logger.success(f'Submit success: {r.status_code}')
        return r.json()
    else:
        logger.error(f'Submit failed: {r.status_code} - {r.text}')
        return False
