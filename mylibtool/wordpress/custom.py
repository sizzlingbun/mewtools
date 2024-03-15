from carehttp import Carehttp


def check_exist_by_param(cls, check_param):
    """Check if already scraped"""
    api_url = f"{cls.wp_root_url}/exist_api.php?source={check_param}"

    r = Carehttp().get(api_url, timeout=30, allow_redirects=False, verify=cls.verify)
    if r.status_code == 200:
        if r.text == "aExist":
            return True
        elif r.text == "aNotExist":
            return False
        else:
            raise Exception("Invalid response")
    else:
        raise Exception(f"Status is {r.status_code}")