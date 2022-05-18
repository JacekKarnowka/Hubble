import unittest

from app import get_coordinates, generate_net, get_distance

class TestApp(unittest.TestCase):
    
    # Get coordinates tests
    def test_get_coordinates(self):
        self.assertEqual(get_coordinates("7 Russell Rd, London W14 8JA"), [51.58037, -0.127807])

    def test_for_empty_string_get_coordinates(self):
        with self.assertRaises(TypeError):
            get_coordinates("")

    # Generate net tests
    def test_generate_net_wrong_corners_format(self):
        with self.assertRaises(TypeError):
            generate_net([[1]], [[0], [1]], [[0], [1]], [[0], [1]])
    
    def test_generate_net_for_numbers(self):
        with self.assertRaises(TypeError):
            generate_net([[1], ["test"]], [[0], [1]], [[0], [1]], [[0], [1]])

    # Calculate distance tests
    def test_get_distance(self):
        self.assertEqual(get_distance(51.516865, -0.118092, 51.4953, -0.1426), 2.93721)

    def test_get_distance_for_numbers(self):
        with self.assertRaises(TypeError):
            self.assertEqual(get_distance("test", -0.118092, 51.4953, -0.1426))

if __name__ == '__main__':
    unittest.main()