import unittest

from html_renderer import MERMAID_SCRIPT_URL, render_mermaid_html


class HtmlRendererTests(unittest.TestCase):
    def test_generates_basic_html_document(self):
        result = render_mermaid_html("mindmap\n  root((Topics))")

        self.assertIn("<!doctype html>", result)
        self.assertIn('<html lang="en">', result)
        self.assertIn('<pre class="mermaid">', result)
        self.assertIn("</html>", result)

    def test_includes_mermaid_definition_and_script(self):
        definition = "mindmap\n  root((Topics))"

        result = render_mermaid_html(definition)

        self.assertIn(definition, result)
        self.assertIn(MERMAID_SCRIPT_URL, result)
        self.assertIn("mermaid.initialize", result)

    def test_escapes_special_characters_safely(self):
        definition = 'mindmap\n  root((<script>alert("x")</script>))'

        result = render_mermaid_html(definition)

        self.assertIn("&lt;script&gt;alert(\"x\")&lt;/script&gt;", result)
        self.assertNotIn("<script>alert(\"x\")</script>", result)


if __name__ == "__main__":
    unittest.main()
