import unittest

# import context


class TestMain(unittest.TestCase):
    def test_run(self):
        self.assertTrue(1 == 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
