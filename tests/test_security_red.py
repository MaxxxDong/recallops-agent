import unittest

from tests.red_vulnerable_fixture import render


class DeliberateRedFixture(unittest.TestCase):
    def test_vulnerable_renderer_must_not_emit_active_markup(self):
        payload = "<img src=x onerror=globalThis.pwned=1>"
        self.assertNotIn("<img", render(payload))


if __name__ == "__main__":
    unittest.main()
