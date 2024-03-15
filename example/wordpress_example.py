from addict import Dict
from mylibtool.wordpress.core import WpApi
from loguru import logger


def custom_post_procedure(wp_cls, article, post_status):
    result = wp_cls.post_file(
        target_file='http://contentcms-bj.cdn.bcebos.com/cmspic/96f103748be3b5b845fedf61f758401a.jpeg',
        title=article.title
    )

    if not result:
        logger.error(f'upload pic: {article.title} failed')
        return False

    file_id, file_url = result

    try:
        article.featured_media = file_id
        article.categories = '1'

        status = wp_cls.submit(article, status=post_status, post_type="posts")
    except Exception as e:
        logger.error(f'Submit {article.title} failed: {e}')
        return


if __name__ == '__main__':
    wp_cls = WpApi(
        wp_url='https://test.com/',
        wp_user='admin',
        api_key='CWa1 MHkn mnra DBgY T84b Uu74',
        verify=False,  # Verify has to be false if your ssl has no certificate
    )

    article = Dict()
    article.title = 'test title english'
    article.content = 'They hear gunfire. They take rounds. They move back, get cover," Escalon said. "And during that time, they approach where the suspect is at.'

    article.metadata.source = 'https://developers.writesonic.com/'
    article.metadata.site = 'writesonic'

    wp_cls.post_normal_article(article, article.title)
    # custom_post_procedure(wp_cls, article, 'pending')
    custom_post_procedure(wp_cls, article, 'pending')
