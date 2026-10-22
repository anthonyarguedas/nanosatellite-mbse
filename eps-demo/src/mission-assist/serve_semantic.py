#!/usr/bin/env python3
"""Optional loopback-only Qwen embedding service. Never reads the paper index.

Run in an environment with torch and sentence-transformers. The pinned model
must already exist in HF_HOME. No model downloads or billable APIs are used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

MODEL = 'Qwen/Qwen3-Embedding-0.6B'
REVISION = '97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3'
QUERY_PROMPT = 'Instruct: Given a mission concept of operations, retrieve descriptions of analogous space missions.\nQuery: '


def validate_payload(payload):
    if not isinstance(payload, dict) or set(payload) != {'query', 'documents'}:
        raise ValueError('Expected query and documents only.')
    query, documents = payload['query'], payload['documents']
    if not isinstance(query, str) or not 24 <= len(query) <= 2000:
        raise ValueError('Query must contain 24 to 2000 characters.')
    if not isinstance(documents, list) or not 1 <= len(documents) <= 12:
        raise ValueError('Expected 1 to 12 reviewed mission descriptions.')
    if any(not isinstance(document, str) or not 1 <= len(document) <= 2000 for document in documents):
        raise ValueError('Each description must contain 1 to 2000 characters.')
    return query, documents


class LocalEmbedder:
    def __init__(self, device='auto'):
        self.device = device
        self.model = None
        self.document_cache = {}

    def load(self):
        if self.model is not None:
            return
        # Set before importing Hugging Face. Missing models fail explicitly.
        os.environ['HF_HUB_OFFLINE'] = '1'
        os.environ['TRANSFORMERS_OFFLINE'] = '1'
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'
        import torch
        from sentence_transformers import SentenceTransformer
        device = self.device
        if device == 'auto':
            device = 'cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu'
        self.model = SentenceTransformer(
            MODEL, revision=REVISION, device=device, local_files_only=True,
            model_kwargs={'dtype': torch.bfloat16 if device == 'mps' else torch.float32, 'attn_implementation': 'sdpa'},
            processor_kwargs={'padding_side': 'right'},
        )
        self.model.max_seq_length = 768

    def embed(self, query, documents):
        self.load()
        key = hashlib.sha256(json.dumps(documents, ensure_ascii=False).encode()).hexdigest()
        if key not in self.document_cache:
            vectors = self.model.encode(documents, batch_size=4, normalize_embeddings=True, show_progress_bar=False)
            # Bound the in-memory cache. Only catalogue vectors are cached.
            if len(self.document_cache) >= 4:
                self.document_cache.clear()
            self.document_cache[key] = vectors.tolist()
        query_vector = self.model.encode([query], prompt=QUERY_PROMPT, normalize_embeddings=True, show_progress_bar=False)[0].tolist()
        return {'model': MODEL, 'revision': REVISION, 'queryVector': query_vector, 'documentVectors': self.document_cache[key]}


def make_handler(embedder, allowed_origins):
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(30)

        def origin_allowed(self):
            # Host validation also blocks DNS rebinding to this loopback service.
            hosts = {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
            origin = self.headers.get('Origin')
            return self.headers.get('Host') in hosts and (origin is None or origin in allowed_origins)

        def send_json(self, status, value):
            body = json.dumps(value, allow_nan=False).encode()
            self.send_response(status)
            origin = self.headers.get('Origin')
            if origin in allowed_origins:
                self.send_header('Access-Control-Allow-Origin', origin)
                self.send_header('Vary', 'Origin')
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self):
            if not self.origin_allowed() or self.path != '/embed':
                return self.send_json(403, {'error': 'Origin or path not allowed.'})
            self.send_response(204)
            self.send_header('Access-Control-Allow-Origin', self.headers.get('Origin', ''))
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Access-Control-Allow-Private-Network', 'true')
            self.send_header('Vary', 'Origin')
            self.end_headers()

        def do_GET(self):
            if not self.origin_allowed():
                return self.send_json(403, {'error': 'Origin not allowed.'})
            if self.path != '/health':
                return self.send_json(404, {'error': 'Unknown path.'})
            self.send_json(200, {'model': MODEL, 'revision': REVISION, 'loaded': embedder.model is not None})

        def do_POST(self):
            if not self.origin_allowed():
                return self.send_json(403, {'error': 'Origin not allowed.'})
            if self.path != '/embed':
                return self.send_json(404, {'error': 'Unknown path.'})
            if self.headers.get_content_type() != 'application/json':
                return self.send_json(415, {'error': 'Use application/json.'})
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 65536:
                    return self.send_json(413, {'error': 'Request exceeds the bounded demo limit.'})
                payload = json.loads(self.rfile.read(size))
                query, documents = validate_payload(payload)
            except (ValueError, UnicodeDecodeError) as error:
                return self.send_json(400, {'error': str(error)})
            try:
                result = embedder.embed(query, documents)
            except Exception:
                # Do not echo user text, local paths, environment, or model errors.
                return self.send_json(503, {'error': 'Local model unavailable. Check the pinned model cache and Python dependencies.'})
            self.send_json(200, result)

        def log_message(self, *_args):
            pass  # ConOps text is never written to a request log.
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8767)
    parser.add_argument('--hf-home', help='Existing Hugging Face cache root (the directory containing hub).')
    parser.add_argument('--device', default='auto', choices=['auto', 'cpu', 'mps', 'cuda'])
    parser.add_argument('--allow-origin', action='append', default=[])
    args = parser.parse_args()
    if args.hf_home:
        os.environ['HF_HOME'] = os.path.abspath(args.hf_home)
        sentence_cache = os.path.join(os.environ['HF_HOME'], 'sentence-transformers')
        if os.path.isdir(sentence_cache):
            os.environ.setdefault('SENTENCE_TRANSFORMERS_HOME', sentence_cache)
    origins = set(args.allow_origin or ['http://127.0.0.1:5173', 'http://localhost:5173'])
    for origin in origins:
        parsed = urlparse(origin)
        if parsed.scheme != 'http' or parsed.hostname not in {'127.0.0.1', 'localhost'} or parsed.path:
            parser.error('Allowed origins must be local HTTP development origins.')
    server = HTTPServer(('127.0.0.1', args.port), make_handler(LocalEmbedder(args.device), origins))
    print(f'Local Qwen embedding service: http://127.0.0.1:{args.port} (offline model cache, no paper index)', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
