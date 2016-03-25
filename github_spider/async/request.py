# -*- coding=utf8 -*-
"""
    异步请求方法
"""
import logging
import requests
import grequests

LOGGER = logging.getLogger(__name__)


def exception_handler(request, exception):
    """
    操作错误
    """
    LOGGER.error('request url:{} failed'.format(request.url))
    LOGGER.exception(exception)


def async_get(urls):
    """
    异步请求数据
    """
    rs = (grequests.get(u) for u in urls)
    result = grequests.map(rs, exception_handler=exception_handler)
    return [x.json() for x in result if x]


def sync_get(urls):
    """
    同步请求数据
    """
    result = []
    for url in urls:
        try:
            result.append(requests.get(url).json())
        except Exception as exc:
            LOGGER.error('get {} fail'.format(url))
            LOGGER.exception(exc)
            continue
    return result
