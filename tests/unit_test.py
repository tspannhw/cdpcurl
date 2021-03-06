#!/usr/bin/env python

import datetime
import logging
import os
import sys

from datetime import timezone

from unittest import TestCase

from mock import patch

from cdpcurl.cdpcurl import make_request

from requests.exceptions import SSLError

import pytest
__author__ = 'cloudera'


def my_mock_get():
    class Object():
        pass

    def ss(*args, **kargs):
        print("in mock")
        response = Object()
        response.status_code = 200
        response.text = 'some text'
        return response

    return ss


def my_mock_send_request():
    class Object():
        pass

    def ss(*args, **kargs):
        print("in mock")
        response = Object()
        response.status_code = 200
        response.text = 'some text'
        return response

    return ss


def my_mock_send_request_verify():
    class Object():
        pass

    def ss(uri, data, headers, method, verify, **kargs):
        print("in mock")
        if not verify:
            raise SSLError
        response = Object()
        response.status_code = 200
        response.text = 'some text'

        return response

    return ss


def my_mock_utcnow():
    class Object():
        pass

    def ss(*args, **kargs):
        print("in mock")
        return datetime.datetime.fromtimestamp(0, tz=timezone.utc)

    return ss


class TestMakeRequest(TestCase):
    maxDiff = None

    @patch('requests.get', new_callable=my_mock_get)
    @patch('cdpcurl.cdpcurl.__send_request', new_callable=my_mock_send_request)
    @patch('cdpcurl.cdpcurl.__now', new_callable=my_mock_utcnow)
    def test_make_request(self, *args, **kvargs):
        headers = {'content-type': 'application/json'}
        params = {'method': 'GET',
                  'uri': 'https://user:pass@host:123/path/?a=b&c=d',
                  'headers': headers,
                  'data': '',
                  'access_key': 'ABC',
                  'private_key': 'Mzjg58S93/qdg0HuVP6PsLSRDTe+fQZ5++v/mkUUx4k=',
                  'data_binary': False}
        make_request(**params)

        expected = {'content-type': 'application/json',
                    'x-altus-date': 'Thu, 01 Jan 1970 00:00:00 GMT',
                    'x-altus-auth': 'eyJhY2Nlc3Nfa2V5X2lkIjogIkFCQyIsICJhdXRoX21ldGhvZCI6ICJlZDI1NTE5djEifQ==.bej2viXTt1s2fhCwl65y10TiOdduxAyCRm1APvVj1qhTYzaTn3L-4xnlCj_UeTt_nFFUHa0rj03RPdzwBjvQCQ=='}

        self.assertEqual(expected, headers)

        pass


class TestMakeRequestVerifyBadPrivateKeyRaises(TestCase):
    maxDiff = None

    @patch('cdpcurl.cdpcurl.__send_request', new_callable=my_mock_send_request_verify)
    @patch('cdpcurl.cdpcurl.__now', new_callable=my_mock_utcnow)
    def test_make_request(self, *args, **kvargs):
        headers = {'content-type': 'application/json'}
        params = {'method': 'GET',
                  'uri': 'https://user:pass@host:123/path/?a=b&c=d',
                  'headers': headers,
                  'data': '',
                  'access_key': 'ABC',
                  'private_key': 'NOPE',
                  'data_binary': False,
                  'verify': False}

        with pytest.raises(Exception):
            make_request(**params)

        pass

class TestMakeRequestVerifySSLPass(TestCase):
    maxDiff = None

    @patch('cdpcurl.cdpcurl.__send_request', new_callable=my_mock_send_request_verify)
    @patch('cdpcurl.cdpcurl.__now', new_callable=my_mock_utcnow)
    def test_make_request(self, *args, **kvargs):
        headers = {'content-type': 'application/json'}
        params = {'method': 'GET',
                  'uri': 'https://user:pass@host:123/path/?a=b&c=d',
                  'headers': headers,
                  'data': '',
                  'access_key': 'ABC',
                  'private_key': 'Mzjg58S93/qdg0HuVP6PsLSRDTe+fQZ5++v/mkUUx4k=',
                  'data_binary': False,
                  'verify': True}
        make_request(**params)

        expected = {'content-type': 'application/json',
                    'x-altus-date': 'Thu, 01 Jan 1970 00:00:00 GMT',
                    'x-altus-auth': 'eyJhY2Nlc3Nfa2V5X2lkIjogIkFCQyIsICJhdXRoX21ldGhvZCI6ICJlZDI1NTE5djEifQ==.bej2viXTt1s2fhCwl65y10TiOdduxAyCRm1APvVj1qhTYzaTn3L-4xnlCj_UeTt_nFFUHa0rj03RPdzwBjvQCQ=='}

        self.assertEqual(expected, headers)

        pass


class TestMakeRequestWithBinaryData(TestCase):
  maxDiff = None

  @patch('requests.get', new_callable=my_mock_get)
  @patch('cdpcurl.cdpcurl.__send_request', new_callable=my_mock_send_request)
  @patch('cdpcurl.cdpcurl.__now', new_callable=my_mock_utcnow)
  def test_make_request(self, *args, **kvargs):
    headers = {'content-type': 'application/json'}
    params = {'method': 'GET',
              'uri': 'https://user:pass@host:123/path/?a=b&c=d',
              'headers': headers,
              'data': b'C\xcfI\x91\xc1\xd0\tw<\xa8\x13\x06{=\x9b\xb3\x1c\xfcl\xfe\xb9\xb18zS\xf4%i*Q\xc9v',
              'access_key': 'ABC',
              'private_key': 'Mzjg58S93/qdg0HuVP6PsLSRDTe+fQZ5++v/mkUUx4k=',
              'data_binary': True}
    make_request(**params)

    expected = {'content-type': 'application/json',
                'x-altus-date': 'Thu, 01 Jan 1970 00:00:00 GMT',
                'x-altus-auth': 'eyJhY2Nlc3Nfa2V5X2lkIjogIkFCQyIsICJhdXRoX21ldGhvZCI6ICJlZDI1NTE5djEifQ==.bej2viXTt1s2fhCwl65y10TiOdduxAyCRm1APvVj1qhTYzaTn3L-4xnlCj_UeTt_nFFUHa0rj03RPdzwBjvQCQ=='}

    self.assertEqual(expected, headers)

    pass


class TestHostFromHeaderUsedInCanonicalHeader(TestCase):
    maxDiff = None

    @patch('requests.get', new_callable=my_mock_get)
    @patch('cdpcurl.cdpcurl.__send_request', new_callable=my_mock_send_request)
    @patch('cdpcurl.cdpcurl.__now', new_callable=my_mock_utcnow)
    def test_make_request(self, *args, **kvargs):
        headers = {'host': 'some.other.host.address.com',
                   'content-type': 'application/json'}
        params = {'method': 'GET',
                  'uri': 'https://user:pass@host:123/path/?a=b&c=d',
                  'headers': headers,
                  'data': '',
                  'access_key': 'ABC',
                  'private_key': 'Mzjg58S93/qdg0HuVP6PsLSRDTe+fQZ5++v/mkUUx4k=',
                  'data_binary': False}
        make_request(**params)

        expected = {'host': 'some.other.host.address.com',
                    'content-type': 'application/json',
                    'x-altus-date': 'Thu, 01 Jan 1970 00:00:00 GMT',
                    'x-altus-auth': 'eyJhY2Nlc3Nfa2V5X2lkIjogIkFCQyIsICJhdXRoX21ldGhvZCI6ICJlZDI1NTE5djEifQ==.bej2viXTt1s2fhCwl65y10TiOdduxAyCRm1APvVj1qhTYzaTn3L-4xnlCj_UeTt_nFFUHa0rj03RPdzwBjvQCQ=='}

        self.assertEqual(expected, headers)

        pass
