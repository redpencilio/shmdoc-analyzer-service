import unittest

try:
    from .analyze.file_analyzer import analyze_file
except ImportError:
    from analyze.file_analyzer import analyze_file


# Unittests for files (csv, xml and json)

class ShmdocTest(unittest.TestCase):
    def check_column(self, column, **kwargs):
        for key, value in kwargs.items():
            self.assertEqual(getattr(column, key), value)


class TestCsv(ShmdocTest):

    def test_basic(self):
        # TODO: Dit is een veel te vage test, elke test zou op 1 specifiek ding moeten testen
        #  in dit geval zou ik dan de focus van deze test op het inlezen ven meerdere kolommen bij csv's leggen
        # http endpointjs /jobs/id/run, /jobs/tests
        result = analyze_file('tests/data/csv/basic.csv', 'csv')

        self.assertTrue(result is not None)
        self.assertEqual(len(result), 7)

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
                          data_type="http://www.w3.org/2001/XMLSchema#boolean",
                          min=0,
                          max=1,
                          median=1,
                          mean=2/3,
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
                          name="my_ref",
                          record_count=3,
                          missing_count=2)

        self.check_column(result[6],
                          name="my_uri",
                          record_count=3,
                          data_type="http://www.w3.org/2001/XMLSchema#anyURI",
                          missing_count=1)

    def test_empty(self):
        result = analyze_file('tests/data/csv/empty.csv', 'csv')
        self.check_column(result[0], missing_count=3, null_count=0,
                          disable_processing=True)  # All empty, so processing should be disabled
        self.check_column(result[1], missing_count=0, null_count=0, disable_processing=False)

    def test_uri(self):
        result = analyze_file('tests/data/csv/uri.csv', 'csv')
        self.check_column(result[0], data_type="http://www.w3.org/2001/XMLSchema#anyURI")

    def test_int(self):
        result = analyze_file('tests/data/csv/int.csv', 'csv')
        self.check_column(result[1], data_type="http://www.w3.org/2001/XMLSchema#integer", median=44.5, mean=44.5, min=19, max=70)

    def test_bool(self):
        result = analyze_file('tests/data/csv/bool.csv', "csv")
        self.check_column(result[0], data_type="http://www.w3.org/2001/XMLSchema#boolean", median=1.0, mean=2/3,
                          min=0, max=1)

    def test_missing_data(self):
        result = analyze_file('tests/data/csv/missing_data.csv', "csv")
        self.check_column(result[0], data_type="http://www.w3.org/2001/XMLSchema#integer", median=5, mean=5,
                          min=5, max=5, missing_count=1)
        self.check_column(result[1], data_type="http://www.w3.org/2001/XMLSchema#string", median=8, mean=8,
                          min=4, max=12, missing_count=1)
        self.check_column(result[2], data_type="http://www.w3.org/2001/XMLSchema#boolean", median=1, mean=1,
                          min=1, max=1, missing_count=1)


class TestXml(ShmdocTest):
    def test_basic_xml(self):
        # http endpointjs /jobs/id/run, /jobs/tests
        result = analyze_file('tests/data/xml/basic.xml', 'xml')
        self.assertEqual(len(result), 5)

    def test_empty(self):
        # http endpointjs /jobs/id/run, /jobs/tests
        result = analyze_file('tests/data/xml/empty.xml', 'xml')
        self.assertEqual(len(result), 4)
        self.check_column(result[1], missing_count=0, null_count=0)
        self.check_column(result[2], missing_count=2, null_count=0)
        self.check_column(result[3], missing_count=0, null_count=3)

    def test_uri(self):
        result = analyze_file('tests/data/xml/uri.xml', 'xml')
        self.check_column(result[0], data_type="http://www.w3.org/2001/XMLSchema#anyURI")

    def test_int(self):
        result = analyze_file('tests/data/xml/int.xml', 'xml')
        self.check_column(result[0], data_type="http://www.w3.org/2001/XMLSchema#integer", min=6, max=9, mean=7.5, median=7.5)

    def test_bool(self):
        result = analyze_file('tests/data/xml/bool.xml', "xml")
        self.check_column(result[0], data_type="http://www.w3.org/2001/XMLSchema#boolean", median=0.5, mean=0.5,
                          min=0, max=1)
        self.check_column(result[1], data_type="http://www.w3.org/2001/XMLSchema#boolean", median=0.5, mean=0.5,
                          min=0, max=1)

class TestJson(ShmdocTest):

    def test_basic_json(self):
        # http endpointjs /jobs/id/run, /jobs/tests
        result = analyze_file('tests/data/json/basic.json', 'json')
        self.assertEqual(len(result), 7)

        self.check_column(result[0], name="my_str", record_count=4, missing_count=0)
        self.check_column(result[6], name="my_ref", record_count=4, missing_count=2)

    def test_null_vs_empty(self):
        # http endpointjs /jobs/id/run, /jobs/tests
        result = analyze_file('tests/data/json/null_vs_empty.json', 'json')
        self.assertEqual(len(result), 2)
        self.check_column(result[1], missing_count=1, null_count=1, record_count=4)

    def test_uri(self):
        result = analyze_file('tests/data/json/uri.json', 'json')
        self.check_column(result[0], data_type="http://www.w3.org/2001/XMLSchema#anyURI")

    def test_bool(self):
        result = analyze_file('tests/data/json/bool.json', "json")
        self.check_column(result[0], data_type="http://www.w3.org/2001/XMLSchema#boolean", median=0.5, mean=0.5,
                          min=0, max=1)
        self.check_column(result[1], data_type="http://www.w3.org/2001/XMLSchema#boolean", median=0.5, mean=0.5,
                          min=0, max=1)

if __name__ == '__main__':
    unittest.main()
