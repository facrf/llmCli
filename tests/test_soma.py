import unittest
from src.soma import somar
class TestSoma(unittest.TestCase):
    def test_somar(self):
        self.assertEqual(somar(1, 2), 3)
if __name__ == '__main__':
    unittest.main()
