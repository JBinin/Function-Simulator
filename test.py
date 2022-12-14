import unittest

test_dir = "./Test"
discover = unittest.defaultTestLoader.discover(test_dir, pattern="test_*.py")

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(discover)