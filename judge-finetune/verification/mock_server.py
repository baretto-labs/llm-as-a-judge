#!/usr/bin/env python3
"""Mock OpenAI-compatible server simulating 4 judge variants with known behaviours."""
import json
import random
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

GOLDEN = {}
for line in open(sys.argv[2], encoding="utf-8"):
    ex = json.loads(line)
    GOLDEN[ex["messages"][1]["content"]] = ex
rng = random.Random(0)


def flip(text):
    return text.replace('"verdict": "PASS"', '"verdict": "TMP"').replace('"verdict": "FAIL"', '"verdict": "PASS"').replace('"verdict": "TMP"', '"verdict": "FAIL"')


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        ex = GOLDEN[body["messages"][1]["content"]]
        gold = ex["messages"][2]["content"]
        model = body["model"]
        if model == "oracle":          # perfect, stable, strict format
            text = gold
        elif model == "verbose-biased":  # always PASS on verbose answers
            text = gold.replace('"verdict": "FAIL"', '"verdict": "PASS"') if ex["meta"]["verbeux"] else gold
        elif model == "noisy":         # 25% random flips, loose format (fenced JSON, no thinking)
            text = flip(gold) if rng.random() < 0.25 else gold
            if rng.random() < 0.5:
                text = "Voici mon avis :\n```json\n" + text.split("</thinking>\n", 1)[1] + "\n```"
        elif model == "broken":        # unparseable
            text = "Je pense que c'est correct."
        else:
            self.send_response(404); self.end_headers(); return
        payload = {"choices": [{"message": {"role": "assistant", "content": text}}],
                   "usage": {"prompt_tokens": 500, "completion_tokens": len(text) // 4}}
        data = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


HTTPServer(("127.0.0.1", int(sys.argv[1])), H).serve_forever()
