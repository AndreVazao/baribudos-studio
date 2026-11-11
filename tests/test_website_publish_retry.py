from __future__ import annotations

import json
import unittest
from io import BytesIO
from urllib.error import HTTPError
from unittest.mock import patch

from studio_core.services import website_publisher_service as publisher


class FakeResponse:
    def __init__(self, body: bytes) -> None:
        self.body = body

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        return False

    def read(self) -> bytes:
        return self.body


def retryable_conflict(retry_after: str = "1") -> HTTPError:
    body = json.dumps({
        "ok": False,
        "error": "retryable_transaction_conflict",
        "retryable": True,
    }).encode("utf-8")
    return HTTPError(
        "https://website.example/api/studio/publish",
        409,
        "Conflict",
        {"Retry-After": retry_after},
        BytesIO(body),
    )


class WebsitePublisherRetryTests(unittest.TestCase):
    def test_retries_explicit_conflict_with_identical_frozen_body(self) -> None:
        body = b'{"publication_id":"pub-1","checksum":"abc123"}'
        requests = []

        def fake_urlopen(http_request, timeout):
            requests.append(http_request)
            if len(requests) == 1:
                raise retryable_conflict("0")
            return FakeResponse(b'{"ok":true,"publication_id":"pub-1"}')

        with patch.object(publisher.request, "urlopen", side_effect=fake_urlopen):
            with patch.object(publisher.time, "sleep") as sleep:
                result = publisher._post_frozen_envelope(
                    "https://website.example/api/studio/publish",
                    "test-api-key",
                    body,
                )

        self.assertTrue(result["ok"])
        self.assertEqual(len(requests), 2)
        self.assertEqual([item.data for item in requests], [body, body])
        sleep.assert_called_once_with(0.0)

    def test_does_not_retry_other_http_errors_or_unrelated_conflicts(self) -> None:
        body = b'{"publication_id":"pub-1"}'
        unrelated = HTTPError(
            "https://website.example/api/studio/publish",
            409,
            "Conflict",
            {"Retry-After": "0"},
            BytesIO(b'{"error":"version_conflict","retryable":true}'),
        )

        with patch.object(publisher.request, "urlopen", side_effect=unrelated) as urlopen:
            with patch.object(publisher.time, "sleep") as sleep:
                with self.assertRaises(publisher.WebsitePublishHTTPError) as raised:
                    publisher._post_frozen_envelope(
                        "https://website.example/api/studio/publish",
                        "test-api-key",
                        body,
                    )

        self.assertEqual(raised.exception.status_code, 409)
        urlopen.assert_called_once()
        sleep.assert_not_called()

    def test_caps_retry_count_and_retry_after_delay(self) -> None:
        body = b'{"publication_id":"pub-1"}'

        def always_conflict(*args, **kwargs):
            raise retryable_conflict("30")

        with patch.object(publisher.request, "urlopen", side_effect=always_conflict) as urlopen:
            with patch.object(publisher.time, "sleep") as sleep:
                with self.assertRaises(publisher.WebsitePublishHTTPError):
                    publisher._post_frozen_envelope(
                        "https://website.example/api/studio/publish",
                        "test-api-key",
                        body,
                    )

        self.assertEqual(urlopen.call_count, publisher.MAX_RETRYABLE_CONFLICT_RETRIES + 1)
        self.assertEqual(sleep.call_count, publisher.MAX_RETRYABLE_CONFLICT_RETRIES)
        self.assertTrue(all(call.args == (publisher.MAX_RETRY_AFTER_SECONDS,) for call in sleep.call_args_list))


if __name__ == "__main__":
    unittest.main()
