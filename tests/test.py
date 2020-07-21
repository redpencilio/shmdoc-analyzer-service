import unittest
from analyze.file_analyzer import analyze_file


# Unittests for files (csv, xml and json)
# Note: The tests are not seperated, since they are all getting reduced to a pandas frame

class TestFile(unittest.TestCase):

    def check_column(self, column, **kwargs):
        for key, value in kwargs.items():
            self.assertEqual(getattr(column, key), value)

    def test_basic_csv(self):
        result = analyze_file('../tests/data/basic.csv', 'csv')

        self.assertTrue(result is not None)
        self.assertEqual(len(result), 6)

        self.check_column(result[0],
                          name="my_str",
                          record_count=3,
                          data_type="http://www.w3.org/2001/XMLSchema#string",
                          min=4,
                          max=4,
                          median=4,
                          mean=4,
                          missing_count=1)

        self.check_column(result[1],
                          name="my_int",
                          record_count=3,
                          data_type="http://www.w3.org/2001/XMLSchema#integer",
                          min=0,
                          max=50,
                          median=20,
                          mean=70 / 3,
                          missing_count=0)

        self.check_column(result[2],
                          name="my_float",
                          record_count=3,
                          data_type="http://www.w3.org/2001/XMLSchema#float",
                          min=3.1415926535,
                          max=9.8,
                          median=6.47079632675,
                          mean=6.47079632675,
                          missing_count=1)

        self.check_column(result[3],
                          name="my_bool",
                          record_count=3,
                          # TODO: data_type="http://www.w3.org/2001/XMLSchema#boolean",
                          min=0,
                          max=1,
                          median=1,
                          mean=2 / 3,
                          missing_count=0)

        self.check_column(result[4],
                          name="my_date",
                          record_count=3,
                          data_type="http://www.w3.org/2001/XMLSchema#dateTime",
                          min=10,  # Is currently just the length (TODO: is it supposed to be the min/max date?)
                          max=10,
                          median=10,
                          mean=10,
                          missing_count=1)

        self.check_column(result[5],
                          name="my_uri",
                          record_count=3,
                          # TODO: data_type
                          missing_count=0)
