import json
from loguru import logger
from carehttp import Carehttp


def create(cls, cat_name, cat_parent_id=0):
    """Create and return the category ID, if the category exists, return the category ID"""
    api_url = f'{cls.api_url}/categories'

    payload = {
        'name': cat_name,
        'parent': cat_parent_id,
    }

    headers = {'content-type': "Application/json"}

    r = Carehttp(f'Create {cat_name}').post(url=api_url,
                                            data=json.dumps(payload),
                                            headers=headers,
                                            auth=(cls.wp_user, cls.api_key),
                                            verify=False,
                                            )

    if r.status_code == 201:
        logger.debug(f'Create {cat_name} success: {r.status_code}')
        return r.json()['id']
    else:
        if r.status_code == 400 and 'term_exists' in r.text:
            logger.warning(f'{cat_name} category exists')
            return r.json()['data']['term_id']

        logger.error(f'Create {cat_name} failed: {r.status_code}')
        return False
