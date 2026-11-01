"""Offline HTTP boundary tests through urllib's real opener/response stack.

Only the final HTTP transport is synthetic. Redirect processing, proxy handling,
HTTPError generation and the public tts.post entry point remain real stdlib code.
No provider, socket, external process or real credential is used.
"""
import contextlib
import email.message
import importlib.util
import http.client
import io
import os
from pathlib import Path
import socket
import traceback
import unittest
from unittest import mock
import urllib.request
import urllib.response

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("tts_redirect_subject", ROOT / "tools" / "tts.py")
tts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tts)

KEY = "fixture-credential-canary"
URL_MARKER = "fixture-url-canary"
QUERY_MARKER = "fixture-query-canary"
BODY_MARKER = "fixture-provider-body-canary"
REASON_MARKER = "fixture-reason-canary"
FORBIDDEN = (KEY, URL_MARKER, QUERY_MARKER, BODY_MARKER, REASON_MARKER)


class TrackedBody(io.BytesIO):
    def __init__(self, content, close_error=None):
        super().__init__(content)
        self.close_error = close_error
        self.reads = 0
        self.was_closed = False

    def read(self, *args, **kwargs):
        self.reads += 1
        return super().read(*args, **kwargs)

    def close(self):
        self.was_closed = True
        super().close()
        error, self.close_error = self.close_error, None
        if error is not None:
            raise error


class SyntheticHTTP(urllib.request.BaseHandler):
    # ProxyHandler (100) runs first; the real HTTP(S) network handlers (500)
    # run after this synthetic transport. HTTPErrorProcessor (1000) is real.
    handler_order = 499

    def __init__(self, statuses=(200,), location=None, error=None, close_error=None):
        self.statuses = list(statuses)
        self.location = location
        self.error = error
        self.close_error = close_error
        self.requests = []
        self.bodies = []

    def open(self, req):
        self.requests.append({
            "url": req.full_url,
            "host": req.host,
            "method": req.get_method(),
            "headers": dict(req.header_items()),
            "data": req.data,
        })
        if self.error is not None:
            raise self.error
        status = self.statuses.pop(0) if self.statuses else 200
        headers = email.message.Message()
        if self.location is not None and status in (301, 302, 303, 307, 308):
            headers["Location"] = self.location
        body = TrackedBody((BODY_MARKER + " " + KEY).encode(), self.close_error)
        self.bodies.append(body)
        response = urllib.response.addinfourl(body, headers, req.full_url, status)
        response.msg = REASON_MARKER
        return response

    def http_open(self, req):
        return self.open(req)

    def https_open(self, req):
        return self.open(req)


class PublicPostBoundaryTests(unittest.TestCase):
    def call_post(self, transport, url=None, headers=None, env=None):
        real_build = urllib.request.build_opener
        stdout, stderr = io.StringIO(), io.StringIO()
        outcome = {"value": None, "error": None, "rendered_error": ""}

        def build_with_transport(*handlers):
            return real_build(transport, *handlers)

        # _opener=None also exercises the original implementation's urlopen
        # through this same real stdlib stack for regression comparison.
        with mock.patch.dict(os.environ, env or {}, clear=True), \
                mock.patch.object(urllib.request, "_opener", None), \
                mock.patch.object(urllib.request, "getproxies", urllib.request.getproxies_environment), \
                mock.patch.object(urllib.request, "proxy_bypass", return_value=False), \
                mock.patch.object(urllib.request, "build_opener", side_effect=build_with_transport), \
                mock.patch.object(socket, "create_connection", side_effect=AssertionError("real network forbidden")), \
                contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                outcome["value"] = tts.post(
                    url or "https://provider.invalid/" + URL_MARKER + "?token=" + QUERY_MARKER,
                    headers or {"Authorization": "Bearer " + KEY},
                    b"explicit-fictional-script",
                    timeout=1,
                )
            except BaseException as error:
                outcome["error"] = error
                outcome["rendered_error"] = "".join(traceback.format_exception(error))
        outcome["stdout"], outcome["stderr"] = stdout.getvalue(), stderr.getvalue()
        return outcome

    def assert_no_sensitive_error_output(self, outcome):
        self.assertIsInstance(outcome["error"], SystemExit)
        exposed = str(outcome["error"]) + outcome["rendered_error"] + outcome["stdout"] + outcome["stderr"]
        for marker in FORBIDDEN:
            self.assertNotIn(marker, exposed)
        self.assertEqual(outcome["stdout"], "")
        self.assertEqual(outcome["stderr"], "")

    def assert_redirect_is_not_followed(self, status):
        for header in ("Authorization", "xi-api-key", "Ocp-Apim-Subscription-Key", "X-Goog-Api-Key"):
            with self.subTest(status=status, credential_header=header):
                transport = SyntheticHTTP((status, 200), "https://other.invalid/final?token=" + QUERY_MARKER)
                result = self.call_post(transport, headers={header: KEY})
                self.assert_no_sensitive_error_output(result)
                self.assertIn(str(status), str(result["error"]))
                self.assertEqual(len(transport.requests), 1, "redirect issued a second credential-bearing request")
                self.assertEqual(transport.requests[0]["method"], "POST")
                self.assertEqual(transport.requests[0]["data"], b"explicit-fictional-script")
                self.assertEqual(len(transport.bodies), 1)
                self.assertEqual(transport.bodies[0].reads, 0)
                self.assertTrue(transport.bodies[0].was_closed)

    def test_301_stops_before_second_request(self):
        self.assert_redirect_is_not_followed(301)

    def test_302_stops_before_second_request(self):
        self.assert_redirect_is_not_followed(302)

    def test_303_stops_before_second_request(self):
        self.assert_redirect_is_not_followed(303)

    def test_307_stops_before_second_request(self):
        self.assert_redirect_is_not_followed(307)

    def test_308_stops_before_second_request(self):
        self.assert_redirect_is_not_followed(308)

    def test_same_origin_redirect_also_does_not_replay_paid_request(self):
        transport = SyntheticHTTP((302, 200), "/final")
        result = self.call_post(transport)
        self.assert_no_sensitive_error_output(result)
        self.assertEqual(len(transport.requests), 1)
        self.assertEqual(transport.bodies[0].reads, 0)
        self.assertTrue(transport.bodies[0].was_closed)

    def test_redirect_without_location_still_does_not_expose_error_body(self):
        transport = SyntheticHTTP((302,), None)
        result = self.call_post(transport)
        self.assert_no_sensitive_error_output(result)
        self.assertEqual(len(transport.requests), 1)
        self.assertEqual(transport.bodies[0].reads, 0)
        self.assertTrue(transport.bodies[0].was_closed)

    def test_http_errors_do_not_read_or_expose_provider_body_or_url(self):
        for status in (400, 401, 403, 404, 429, 500, 503):
            with self.subTest(status=status):
                transport = SyntheticHTTP((status,))
                result = self.call_post(transport)
                self.assert_no_sensitive_error_output(result)
                self.assertIn(str(status), str(result["error"]))
                self.assertEqual(len(transport.requests), 1)
                self.assertEqual(transport.bodies[0].reads, 0)
                self.assertTrue(transport.bodies[0].was_closed)

    def test_transport_exception_details_do_not_surface(self):
        details = URL_MARKER + "?token=" + QUERY_MARKER + " " + KEY
        for error in (urllib.error.URLError(details), OSError(details), ValueError(details), UnicodeError(details),
                      http.client.BadStatusLine(details), http.client.InvalidURL(details)):
            with self.subTest(error_type=type(error).__name__):
                transport = SyntheticHTTP(error=error)
                result = self.call_post(transport)
                self.assert_no_sensitive_error_output(result)
                self.assertEqual(len(transport.requests), 1)

    def test_http_error_close_failure_cannot_bypass_error_redaction(self):
        transport = SyntheticHTTP((401,), close_error=OSError(KEY + " " + REASON_MARKER))
        result = self.call_post(transport)
        self.assert_no_sensitive_error_output(result)
        self.assertEqual(len(transport.requests), 1)
        self.assertEqual(transport.bodies[0].reads, 0)
        self.assertTrue(transport.bodies[0].was_closed)

    def test_success_keeps_audio_response_and_single_request(self):
        transport = SyntheticHTTP((200,))
        result = self.call_post(transport)
        self.assertIsNone(result["error"])
        self.assertEqual(result["value"], (BODY_MARKER + " " + KEY).encode())
        self.assertEqual(len(transport.requests), 1)
        self.assertEqual(transport.bodies[0].reads, 1)
        self.assertTrue(transport.bodies[0].was_closed)

    def test_loopback_http_ignores_ambient_proxy_even_without_no_proxy(self):
        transport = SyntheticHTTP((200,))
        result = self.call_post(transport, url="http://127.0.0.1:8765/speech", env={"http_proxy": "http://proxy.invalid:8123"})
        self.assertIsNone(result["error"])
        self.assertEqual(len(transport.requests), 1)
        self.assertEqual(transport.requests[0]["host"], "127.0.0.1:8765")
        self.assertEqual(transport.requests[0]["url"], "http://127.0.0.1:8765/speech")

    def test_remote_https_keeps_explicit_enterprise_proxy_configuration(self):
        transport = SyntheticHTTP((200,))
        result = self.call_post(transport, env={"https_proxy": "http://proxy.invalid:8123"})
        self.assertIsNone(result["error"])
        self.assertEqual(len(transport.requests), 1)
        self.assertEqual(transport.requests[0]["host"], "proxy.invalid:8123")


if __name__ == "__main__":
    unittest.main()
