import unittest
import hashlib
import hmac
import json
from src.utils.common import genSign

class TestGenSign(unittest.TestCase):
    """
    測試 genSign 函數的功能。
    """

    def test_gen_sign_basic(self):
        """
        測試 genSign 函數的基本功能，使用預期的輸入和輸出。
        """
        salt_key = "test_salt_key"
        url = "https://example.com/api"
        request_body = {"param1": "value1", "param2": 123}
        timestamp = "1678886400"  # 2023-03-15 00:00:00 UTC
        secret_key = b"test_secret_key"

        # 預期簽名計算
        request_body_json = json.dumps(request_body, separators=(',', ':'))
        data_for_sign = salt_key + url + request_body_json + timestamp
        expected_sign = hmac.new(secret_key, data_for_sign.encode('utf-8'), hashlib.sha256).hexdigest()

        actual_sign = genSign(salt_key, url, request_body, timestamp, secret_key)
        self.assertEqual(actual_sign, expected_sign, "genSign 函數應返回正確的簽名")

    def test_gen_sign_empty_body(self):
        """
        測試 genSign 函數在 request_body 為空字典時的功能。
        """
        salt_key = "another_salt"
        url = "https://example.com/empty"
        request_body = {}
        timestamp = "1678886500"
        secret_key = b"empty_secret"

        request_body_json = json.dumps(request_body, separators=(',', ':'))
        data_for_sign = salt_key + url + request_body_json + timestamp
        expected_sign = hmac.new(secret_key, data_for_sign.encode('utf-8'), hashlib.sha256).hexdigest()

        actual_sign = genSign(salt_key, url, request_body, timestamp, secret_key)
        self.assertEqual(actual_sign, expected_sign, "genSign 函數在空 request_body 時應返回正確的簽名")

    def test_gen_sign_different_data_types(self):
        """
        測試 genSign 函數在 request_body 包含不同數據類型時的功能。
        """
        salt_key = "data_types_salt"
        url = "https://example.com/types"
        request_body = {"string": "hello", "number": 123, "boolean": True, "list": [1, 2, "three"]}
        timestamp = "1678886600"
        secret_key = b"types_secret"

        request_body_json = json.dumps(request_body, separators=(',', ':'))
        data_for_sign = salt_key + url + request_body_json + timestamp
        expected_sign = hmac.new(secret_key, data_for_sign.encode('utf-8'), hashlib.sha256).hexdigest()

        actual_sign = genSign(salt_key, url, request_body, timestamp, secret_key)
        self.assertEqual(actual_sign, expected_sign, "genSign 函數在不同數據類型時應返回正確的簽名")

    def test_gen_sign_special_characters(self):
        """
        測試 genSign 函數在輸入包含特殊字符時的功能。
        """
        salt_key = "special_chars_salt"
        url = "https://example.com/special?q=!@#$%^&*"
        request_body = {"key": "value with !@#$%^&*()_+-=[]{}|;:'\",.<>/?`~"}
        timestamp = "1678886700"
        secret_key = b"special_secret"

        request_body_json = json.dumps(request_body, separators=(',', ':'))
        data_for_sign = salt_key + url + request_body_json + timestamp
        expected_sign = hmac.new(secret_key, data_for_sign.encode('utf-8'), hashlib.sha256).hexdigest()

        actual_sign = genSign(salt_key, url, request_body, timestamp, secret_key)
        self.assertEqual(actual_sign, expected_sign, "genSign 函數在特殊字符時應返回正確的簽名")

if __name__ == '__main__':
    unittest.main()
