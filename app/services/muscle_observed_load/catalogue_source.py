"""Complete byte-attested JSON admission; only curation notes stay opaque.

The result is a projected view, never a replacement for the attested source.
No historical source code is executed and the generic JSON admission is unchanged.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass

from .limits import ReadLimits


@dataclass(frozen=True)
class CatalogueProjection:
    document: dict
    source_sha256: str
    omitted_paths: tuple[str, ...]


class _Scanner:
    def __init__(self, raw: bytes, limits: ReadLimits):
        self.text = raw.decode("utf-8", errors="strict")
        self.limits = limits
        self.index = 0
        self.tokens = 0
        self.omitted: list[str] = []

    def tick(self):
        # Same lexical accounting as bounded_json: strings, opens, commas, colons.
        self.tokens += 1
        if self.tokens > self.limits.max_tokens:
            raise ValueError("json_token_limit")

    def whitespace(self):
        while self.index < len(self.text) and self.text[self.index] in " \t\r\n":
            self.index += 1

    def unicode_escape(self):
        digits = self.text[self.index + 1 : self.index + 5]
        if len(digits) != 4 or any(c not in "0123456789abcdefABCDEF" for c in digits):
            raise ValueError("json_unicode_escape")
        code = int(digits, 16)
        self.index += 4
        if 0xD800 <= code <= 0xDBFF:
            if self.text[self.index + 1 : self.index + 3] != "\\u":
                raise ValueError("json_unpaired_surrogate")
            low = self.text[self.index + 3 : self.index + 7]
            if (
                len(low) != 4
                or any(c not in "0123456789abcdefABCDEF" for c in low)
                or not 0xDC00 <= int(low, 16) <= 0xDFFF
            ):
                raise ValueError("json_unpaired_surrogate")
            self.index += 6
        elif 0xDC00 <= code <= 0xDFFF:
            raise ValueError("json_unpaired_surrogate")

    def string(self, *, opaque=False):
        self.tick()
        start = self.index
        self.index += 1
        while self.index < len(self.text):
            char = self.text[self.index]
            if not opaque and self.index - start - 1 > self.limits.max_string:
                raise ValueError("json_string_limit")
            if char == '"':
                end = self.index
                self.index += 1
                if opaque:
                    return None
                literal = self.text[start + 1 : end]
                if len(literal.encode("utf-8")) > self.limits.max_string:
                    raise ValueError("json_string_limit")
                value = json.loads(self.text[start : self.index])
                if len(value.encode("utf-8", errors="strict")) > self.limits.max_string:
                    raise ValueError("json_string_limit")
                return value
            if ord(char) < 32:
                raise ValueError("json_control_character")
            if char == "\\":
                self.index += 1
                if self.index >= len(self.text):
                    raise ValueError("json_truncated_escape")
                escape = self.text[self.index]
                if escape == "u":
                    self.unicode_escape()
                elif escape not in '"\\/bfnrt':
                    raise ValueError("json_escape")
            self.index += 1
        raise ValueError("json_unterminated_string")

    @staticmethod
    def editorial(path):
        return (
            len(path) == 5
            and path[0] == "records"
            and type(path[1]) is int
            and path[2:] == ("exercise_operational", "curation", "notes")
        )

    def value(self, path=(), depth=0):
        self.whitespace()
        if self.index >= len(self.text):
            raise ValueError("json_truncated_value")
        char = self.text[self.index]
        if self.editorial(path):
            if char != '"':
                raise ValueError("editorial_notes_not_string")
            self.string(opaque=True)
            self.omitted.append("/" + "/".join(map(str, path)))
            return None
        if char == '"':
            return self.string()
        if char in "{[":
            return self.container(char, path, depth + 1)
        start = self.index
        while self.index < len(self.text) and self.text[self.index] not in ",]} \t\r\n":
            self.index += 1
        value = json.loads(self.text[start : self.index], parse_constant=self.no_constant)
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("json_nonfinite")
        return value

    @staticmethod
    def no_constant(_):
        raise ValueError("json_nonfinite")

    def container(self, opening, path, depth):
        if depth > self.limits.max_depth:
            raise ValueError("json_depth_limit")
        self.tick()
        self.index += 1
        self.whitespace()
        closing = "}" if opening == "{" else "]"
        result = {} if opening == "{" else []
        seen = set()
        if self.index < len(self.text) and self.text[self.index] == closing:
            self.index += 1
            return result
        while True:
            self.whitespace()
            if opening == "{":
                if self.index >= len(self.text) or self.text[self.index] != '"':
                    raise ValueError("json_object_key")
                key = self.string()
                if key in seen:
                    raise ValueError("json_duplicate_key")
                seen.add(key)
                self.whitespace()
                if self.index >= len(self.text) or self.text[self.index] != ":":
                    raise ValueError("json_colon")
                self.tick()
                self.index += 1
                child_path = path + (key,)
                child = self.value(child_path, depth)
                if not self.editorial(child_path):
                    result[key] = child
            else:
                result.append(self.value(path + (len(result),), depth))
            self.whitespace()
            if self.index >= len(self.text):
                raise ValueError("json_truncated_container")
            separator = self.text[self.index]
            self.index += 1
            if separator == closing:
                return result
            if separator != ",":
                raise ValueError("json_separator")
            self.tick()

    def parse(self):
        result = self.value()
        self.whitespace()
        if self.index != len(self.text):
            raise ValueError("json_trailing_data")
        if (
            type(result) is not dict
            or type(result.get("catalogue_header")) is not dict
            or type(result.get("records")) is not list
            or any(type(row) is not dict for row in result["records"])
        ):
            raise ValueError("catalogue_shape_invalid")
        return result


def project_catalogue(
    raw: bytes, expected_digest: str, limits: ReadLimits = ReadLimits()
) -> CatalogueProjection:
    if len(raw) > limits.source_total:
        raise ValueError("source_byte_limit")
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected_digest:
        raise ValueError("source_digest_mismatch")
    scanner = _Scanner(raw, limits)
    return CatalogueProjection(scanner.parse(), actual, tuple(scanner.omitted))
