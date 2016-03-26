# -*- coding=utf8 -*-
"""
    往队列发送消息
"""
import gevent
from retrying import retry
from kombu import Connection, Exchange
from kombu.pools import producers

from github_spider.settings import MESSAGE_BROKER_URI
from github_spider.const import MESSAGE_QUEUE_EXCHANGE

SYNC = 1
ASYNC = 2


class Producer(object):
    """
    生产者
    """
    def __init__(self, exchange_name, broker_url, mode=ASYNC):
        """初始化生产者

        Args:
            exchange_name (string): 路由名称
            broker_url (string): 连接地址
            mode (int): 发送
        """
        self.exchange_name = exchange_name
        self.broker_url = broker_url
        self.mode = mode

        self.exchange = Exchange(exchange_name, type='direct')
        self.connection = Connection(broker_url)

    @retry(stop_max_attempt_number=5)
    def _sync_send(self, payload, routing_key, **kwargs):
        """发送url至指定队列

        Args:
            payload (string): 消息内容
            routing_key (string)
        """
        with producers[self.connection].acquire(block=True) as p:
            p.publish(payload, exchange=self.exchange,
                      routing_key=routing_key, **kwargs)

    def _async_send(self, payload, routing_key, **kwargs):
        """发送url至指定队列

        Args:
            payload (string): 消息内容
            routing_key (string)
        """
        gevent.spawn(self._sync_send, payload, routing_key, **kwargs)
        gevent.sleep(0)

    def send_url(self, url, routing_key, **kwargs):
        """发送url至指定队列

        Args:
            url (string): url地址
            routing_key (string)
        """
        if self.mode == SYNC:
            self._sync_send(url, routing_key, **kwargs)
        elif self.mode == ASYNC:
            self._async_send(url, routing_key, **kwargs)

url_sender = Producer(MESSAGE_QUEUE_EXCHANGE, MESSAGE_BROKER_URI, ASYNC)
