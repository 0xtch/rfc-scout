import unittest
from pathlib import Path

from chunker import clean_rfc_text, count_tokens, load_rfc_chunks, split_paragraphs

RFC4271 = Path("data/rfc/rfc4271.txt")
MAX_TOKENS = 400


class TestRfc4271(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = RFC4271.read_text(encoding="utf-8")
        cls.chunks = [c.text for c in load_rfc_chunks(RFC4271, MAX_TOKENS, 50)]

    def test_chunks_not_too_long(self):
        for chunk in self.chunks:
            self.assertLessEqual(count_tokens(chunk), MAX_TOKENS)

    def test_open_message_diagram_in_one_chunk(self):
        # find the OPEN message diagram in the cleaned text
        diagram = next(p for p in split_paragraphs(clean_rfc_text(self.raw))
                       if "My Autonomous System" in p and "+-+-+" in p)
        self.assertTrue(any(diagram in chunk for chunk in self.chunks))
