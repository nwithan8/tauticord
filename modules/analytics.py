import requests
import uuid
import urllib


def _time_uuid():
    return uuid.uuid1()


def _random_uuid():
    return uuid.uuid4()


def _generate_uuid(random=False):
    if random:
        return _random_uuid()
    return _time_uuid()


def _verify_params(params_needed, **included_params):
    for needed_param in params_needed:
        if needed_param not in included_params.keys() or included_params.get(needed_param):
            return False
    return True


def _make_url(params_dict):
    base_url = "https://www.google-analytics.com/collect"
    args = urllib.parse.urlencode(params_dict)
    return f"{base_url}?{args}"


class GoogleAnalytics:
    def __init__(self, analytics_id: str, anonymous_ip: bool = False, do_not_track: bool = False):
        self.analytics_id = analytics_id
        self.version = '1'
        self.anonymize_ip = anonymous_ip
        self.do_not_track = do_not_track

    def _send(self, final_params):
        if self.do_not_track:
            return True
        url = _make_url(params_dict=final_params)
        try:
            if requests.post(url=url):
                return True
        except:
            pass
        return False

    def event(self, event_category: str, event_action: str,
              event_label: str = None, event_value: int = None, user_id: str = None,
              anonymize_ip: bool = False, random_uuid_if_needed: bool = False):
        if self.do_not_track:
            return True
        if not user_id:
            user_id = str(_generate_uuid(random=random_uuid_if_needed))
        final_params = {'v': self.version, 'tid': self.analytics_id, 't': 'event', 'cid': user_id}
        if anonymize_ip or self.anonymize_ip:
            final_params['aip'] = 0
        final_params['ec'] = event_category
        final_params['ea'] = event_action
        if event_label:
            final_params['el'] = event_label
        if event_value:
            final_params['ev'] = event_value
        return self._send(final_params=final_params)

    def pageview(self, visited_page: str,
                 page_title: str = None, user_id: str = None,
                 anonymize_ip: bool = False, random_uuid_if_needed: bool = False):
        if self.do_not_track:
            return True
        if not user_id:
            user_id = str(_generate_uuid(random=random_uuid_if_needed))
        final_params = {'v': self.version, 'tid': self.analytics_id, 't': 'pageview', 'cid': user_id}
        if anonymize_ip or self.anonymize_ip:
            final_params['aip'] = 0
        if not visited_page.startswith('/'):
            visited_page = f"/{visited_page}"
        final_params['dl'] = visited_page
        if page_title:
            final_params['dt'] = page_title
        return self._send(final_params=final_params)
