"""Fast stdlib tests. These do not load a model or access the corpus."""
import json
import threading
import unittest
from http.client import HTTPConnection
from http.server import HTTPServer
from serve_semantic import make_handler, validate_payload


class FakeEmbedder:
    model = None
    def __init__(self):
        self.calls = 0
    def embed(self, query, documents):
        self.calls += 1
        return {'fixture': True}


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.embedder = FakeEmbedder()
        self.server = HTTPServer(('127.0.0.1', 0), make_handler(self.embedder, {'http://127.0.0.1:5173'}))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def request(self, method, path, body=None, headers=None):
        connection = HTTPConnection('127.0.0.1', self.server.server_port, timeout=5)
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        status, headers, payload = response.status, dict(response.getheaders()), response.read()
        connection.close()
        return status, headers, payload

    def test_health_does_not_load_model(self):
        status, _, payload = self.request('GET', '/health')
        self.assertEqual(status, 200)
        self.assertFalse(json.loads(payload)['loaded'])
        self.assertEqual(self.embedder.calls, 0)

    def test_allowed_origin_and_preflight(self):
        status, headers, _ = self.request('OPTIONS', '/embed', headers={'Origin': 'http://127.0.0.1:5173'})
        self.assertEqual(status, 204)
        self.assertEqual(headers['Access-Control-Allow-Origin'], 'http://127.0.0.1:5173')
        payload = json.dumps({'query': 'Measure rain clouds with a compact radar.', 'documents': ['Rainfall radar demonstration.']})
        status, headers, _ = self.request('POST', '/embed', payload, {'Origin': 'http://127.0.0.1:5173', 'Content-Type': 'application/json'})
        self.assertEqual(status, 200)
        self.assertEqual(headers['Cache-Control'], 'no-store')
        self.assertEqual(self.embedder.calls, 1)

    def test_remote_origins_and_wrong_paths_blocked(self):
        status, headers, _ = self.request('POST', '/embed', '{}', {'Origin': 'https://untrusted.example', 'Content-Type': 'application/json'})
        self.assertEqual(status, 403)
        self.assertNotIn('Access-Control-Allow-Origin', headers)
        self.assertEqual(self.request('GET', '/anything')[0], 404)
        self.assertEqual(self.request('GET', '/health', headers={'Host': 'rebound.example:8767'})[0], 403)
        self.assertEqual(self.embedder.calls, 0)

    def test_bad_payloads_do_not_call_embedder(self):
        self.assertEqual(self.request('POST', '/embed', '{}', {'Content-Type': 'text/plain'})[0], 415)
        self.assertEqual(self.request('POST', '/embed', '{}', {'Content-Type': 'application/json'})[0], 400)
        self.assertEqual(self.request('POST', '/embed', '{', {'Content-Type': 'application/json'})[0], 400)
        self.assertEqual(self.embedder.calls, 0)

    def test_model_failure_is_unavailable_without_echoing_text(self):
        def fail(*_args):
            raise RuntimeError('Sensitive query or local path should never be echoed.')
        self.embedder.embed = fail
        payload = json.dumps({'query': 'Measure rain clouds with a compact radar.', 'documents': ['Rain radar.']})
        status, _, body = self.request('POST', '/embed', payload, {'Content-Type': 'application/json'})
        self.assertEqual(status, 503)
        self.assertNotIn(b'Sensitive', body)
        self.assertNotIn(b'Measure rain', body)

    def test_payload_bounds(self):
        for payload in [None, {}, {'query': 'x' * 2001, 'documents': ['example']}, {'query': 'x' * 30, 'documents': ['x'] * 13}, {'query': 'x' * 30, 'documents': ['x' * 2001]}]:
            with self.assertRaises(ValueError):
                validate_payload(payload)


if __name__ == '__main__':
    unittest.main()
