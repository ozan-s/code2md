#SECTION: Unit Tests
import os
import unittest
import tempfile
import shutil
from code2md import parse_gitignore, collect_files, get_language_identifier

class TestFileCombiner(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

        # Create some test files
        self.create_test_file("test1.py", "print('Hello')")
        self.create_test_file("test2.js", "console.log('World')")
        self.create_test_file(".gitignore", "*.log")
        self.create_test_file("ignored.log", "This should be ignored")

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    def create_test_file(self, filename, content):
        with open(os.path.join(self.test_dir, filename), 'w') as f:
            f.write(content)

    def test_parse_gitignore(self):
        patterns = parse_gitignore(self.test_dir)
        self.assertEqual(patterns, ["*.log"])

    def test_collect_files(self):
        files = list(collect_files(self.test_dir))
        self.assertIn(os.path.join(self.test_dir, "test1.py"), files)
        self.assertIn(os.path.join(self.test_dir, "test2.js"), files)
        self.assertNotIn(os.path.join(self.test_dir, "ignored.log"), files)

    def test_get_language_identifier(self):
        self.assertEqual(get_language_identifier("test.py"), "python")
        self.assertEqual(get_language_identifier("test.js"), "javascript")
        self.assertEqual(get_language_identifier("test.unknown"), "")

if __name__ == "__main__":
    unittest.main()