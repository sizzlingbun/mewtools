import time
import filetype

from addict import Dict
from loguru import logger
from carehttp import Carehttp
from requests_toolbelt.multipart.encoder import MultipartEncoder


def post_file(cls, target_file, title):
    """
    Download and upload picture to WP
    :param cls: wordpress object
    :param target_file: file url or local path
    :param title:
    :return: (file_id, file_wp_url)
    """
    file_content = None

    # if remote pic, download it, if local path, read it
    if target_file.startswith('http'):
        try:
            # download file
            r_download = fetch_pic(url=target_file)
            if r_download.status_code != 200:
                logger.error(f'Download {target_file} failed: {r_download.status_code}')
                return

            file_content = r_download.content
        except Exception as e:
            logger.error(f'Download {target_file} failed: {e}')
            return
    else:
        try:
            # open local file
            with open(target_file, 'rb') as f:
                file_content = f.read()
        except Exception as e:
            logger.error(f"Open file {target_file} failed: {e}")
            return

    try:
        # get file's mine and suffix
        kind = filetype.guess(file_content)
        if kind is None:
            raise

    except:
        logger.error(f"Can not guess file type")
        return

    try:
        new_file = {
            'title': title,
            'file_name': f'autoPost_{str(round(time.time() * 1000))}.{kind.extension}',  # random a new file name
            'mine': kind.mime,
            'file_content': file_content,
        }
        r_upload = upload2wp(cls=cls, file_obj=new_file)
    except Exception as e:
        logger.error(f'Upload {target_file} failed: {e}')
        return

    if r_upload.status_code != 201:
        logger.error(f'Upload {target_file} failed:  {r_upload.status_code}')
        return

    json_data = r_upload.json()

    return json_data['id'], json_data['source_url']


def fetch_pic(url):
    header = {
        'Connection': 'close',
        'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'accept-encoding': 'gzip,deflate,br',
        'user-agent': 'Mozilla/5.0(WindowsNT10.0;Win64;x64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/95.0.4638.69Safari/537.36',
    }

    logger.debug(f"Download: {url}")
    r = Carehttp(tries=6).get(url, headers=header, timeout=60, allow_redirects=False)
    return r


def upload2wp(cls, file_obj):
    """
    Upload picture to WP
    :param cls: class object
    :param file_obj: dict - {title, file_name, mine, file_content}
    :return: Json/None
    """
    api_url = f'{cls.api_url}/media'

    multipart_data = MultipartEncoder(
        fields={
            # a file upload field
            'file': (file_obj['file_name'], file_obj['file_content'], file_obj['mine']),
            # plain text fields
            'caption': file_obj['title'],
        }
    )

    r = Carehttp(file_obj['file_name']).post(url=api_url,
                                             data=multipart_data,
                                             headers={'Content-Type': multipart_data.content_type},
                                             auth=(cls.wp_user, cls.api_key),
                                             verify=cls.verify
                                             )

    return r
