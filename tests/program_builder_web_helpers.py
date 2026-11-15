"""Existing SSR consumers submit the actual token rendered by an owned GET."""

import re
from urllib.parse import urlencode


def post_program(client, url, **kwargs):
    match = re.search(r"/programs/(\d+)", str(url))
    if match:
        root = "/programs/" + match.group(1)
        suffix = (
            "/publish"
            if str(url).endswith("/publish")
            else "/generate"
            if str(url).endswith("/generate")
            else ""
        )
        page = client.get(root + suffix, follow_redirects=False)
    elif str(url) == "/programs/from-weekly-plan":
        page = client.get("/plan", follow_redirects=False)
    else:
        page = client.get("/programs/new", follow_redirects=False)
    token = re.search(r'name="source_digest" value="([0-9a-f]{64})"', page.text)
    if token is None:
        token = re.search(r'data-source-digest="([0-9a-f]{64})"', page.text)
    # Foreign/missing/auth and immutable root pages may intentionally expose no
    # mutation form; the production route still enforces their original 404/401.
    original = kwargs.pop("data", {}) or {}
    if isinstance(original, list):
        pairs = list(original)
        if token:
            pairs.append(("source_digest", token.group(1)))
        headers = {**kwargs.pop("headers", {}), "Content-Type": "application/x-www-form-urlencoded"}
        return client.post(url, content=urlencode(pairs), headers=headers, **kwargs)
    data = dict(original)
    if token:
        data["source_digest"] = token.group(1)
    return client.post(url, data=data, **kwargs)
