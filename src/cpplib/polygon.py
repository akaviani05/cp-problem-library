"""Documented Polygon API only. Signed request bodies never enter logs."""

import hashlib
import json
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request

from .util import Error, require


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        return None


def signed_parameters(method, parameters, key, secret, timestamp=None, nonce=None):
    values = {name: str(value).lower() if isinstance(value, bool) else str(value)
              for name, value in parameters.items()}
    values.update(apiKey=key, time=str(int(time.time()) if timestamp is None else timestamp))
    canonical = "&".join(f"{name}={value}" for name, value in sorted(values.items()))
    nonce = nonce or secrets.token_hex(3)
    values["apiSig"] = nonce + hashlib.sha512(f"{nonce}/{method}?{canonical}#{secret}".encode()).hexdigest()
    return values


class Polygon:
    def __init__(self, config):
        self.key = config["api_key"]
        self.secret = config["api_secret"]
        require(self.key and self.secret, "Run 'cppl config init' or set POLYGON_API_KEY/POLYGON_API_SECRET.")
        self.opener = urllib.request.build_opener(NoRedirect())
        self.calls = 0

    def redact(self, message):
        return str(message).replace(self.key, "[API KEY]").replace(self.secret, "[API SECRET]")

    def call(self, method, parameters=None, *, raw=False):
        values = signed_parameters(method, parameters or {}, self.key, self.secret)
        request = urllib.request.Request("https://polygon.codeforces.com/api/" + method,
                                         data=urllib.parse.urlencode(values).encode(),
                                         headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                                                  "User-Agent": "cp-problem-library/0.1"})
        self.calls += 1
        try:
            with self.opener.open(request, timeout=270 if method == "problem.renderStatements" else 60) as response:
                payload = response.read()
        except urllib.error.HTTPError as error:
            try:
                comment = json.loads(error.read()).get("comment", f"HTTP {error.code}")
            except (ValueError, AttributeError):
                comment = f"HTTP {error.code} (non-JSON response)"
            raise Error(f"{method}: {self.redact(comment)}") from None
        except (urllib.error.URLError, TimeoutError, OSError):
            raise Error(f"{method}: network failure; retry the CLI command. Uploads reconcile uncertain writes.") from None
        try:
            result = json.loads(payload)
        except (ValueError, UnicodeDecodeError):
            require(raw, f"{method}: unexpected non-JSON response.")
            return payload
        if isinstance(result, dict) and result.get("status") == "FAILED":
            raise Error(f"{method}: {self.redact(result.get('comment', 'failed'))}")
        if raw:
            return payload
        require(isinstance(result, dict) and result.get("status") == "OK", f"{method}: malformed API response.")
        return result.get("result")

    def problem(self, state, method, **parameters):
        return self.call(method, {"problemId": state["id"], **parameters})
