import shutil, tempfile
from os import path
import unittest
from input import Schema, Input


def create_csv_file(file_name):
    test_dir = tempfile.mkdtemp()
    test_file_path = path.join(test_dir, file_name)
    f = open(test_file_path, 'w')
    for i in range(15):
        f.write('col1%d, col2%d, col3%d, col4%d, col5%d, col6%d\n' % (i, i, i, i, i, i))
    f.close()
    return test_dir, test_file_path


class TestSchema(unittest.TestCase):
    def setUp(self):
        self.test_dir, self.test_file_path = create_csv_file('test.csv')

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_default_columns(self):
        schema = Schema(self.test_file_path)
        for index, column in enumerate(schema.columns):
            self.assertEqual(column.name, 'col_' + str(index))

    def test_set_column_name(self):
        schema = Schema(self.test_file_path)
        schema["col_0"] = "test_col"
        self.assertEqual(schema.columns[0].name, 'test_col')

    def test_set_columns_names(self):
        schema = Schema(self.test_file_path)
        with self.assertRaises(Exception) as context:
            schema.columns = ("test_col1", "test_col2", "test_col3")
        self.assertTrue("Passed columns number: 3 is not compatible with Schema current columns number: 6"
                        in context.exception)

    def test_drop_column(self):
        schema = Schema(self.test_file_path)
        schema.drop_column("col_0")
        self.assertEqual(schema.columns[0].name, 'col_1')

    def test_merge_columns(self):
        schema = Schema(self.test_file_path)
        schema.merge_columns("test_col", ["col_0", "col_1"])
        self.assertEqual(len(schema.columns), 5)
        self.assertEqual(schema.columns[0].name, 'col_2')
        merged_column = schema.columns[len(schema.columns) - 1]
        self.assertEqual(merged_column.name, 'test_col')
        self.assertTrue(merged_column.columns_indexes, [0 ,2])

    def test_merge_columns_in_range(self):
        schema = Schema(self.test_file_path)
        schema.merge_columns_in_range("test_col", (3, 5))
        self.assertEqual(len(schema.columns), 4)
        self.assertEqual(schema.columns[0].name, 'col_0')
        merged_column = schema.columns[len(schema.columns) - 1]
        self.assertEqual(merged_column.name, 'test_col')
        self.assertTrue(merged_column.columns_indexes == [3, 4 ,5])

    def test_duplicate_in_header(self):
        test_file_path = path.join(self.test_dir, 'test_duplicate_header.csv')
        f = open(test_file_path, 'w')
        f.write('head1, head1, head3, head4, head5, head6\n')
        for i in range(5):
            f.write('col1%d, col2%d, col3%d, col4%d, col5%d, col6%d\n' % (i, i, i, i, i, i))
        f.close()

        with self.assertRaises(Exception) as context:
            Schema(test_file_path, header=True)
        self.assertTrue("Should be no duplicates in CSV header: head1" in context.exception)

    def test_duplicate_columns(self):
        with self.assertRaises(Exception) as context:
            schema = Schema(self.test_file_path)
            schema['col_0'] = 'col_1'
        self.assertTrue('Should be no duplicates in columns: col_1' in context.exception)

        with self.assertRaises(Exception) as context:
            schema = Schema(self.test_file_path)
            schema.columns = ['col1', 'col1', 'col3', 'col4', 'col5', 'col6']
        self.assertTrue('Should be no duplicates in columns: col1' in context.exception)


class TestInput(unittest.TestCase):
    def setUp(self):
        self.test_dir, self.test_file_path = create_csv_file('test.csv')

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_add_basic_type_column(self):
        input = Input(Schema(self.test_file_path))
        input.add_int_column("col_3")
        is_column_exist = False
        for column in input.columns:
            if column.name == 'col_3':
                is_column_exist = True
                self.assertEqual(column.columns_indexes[0], 3)
                self.assertEqual(input.columns.get(column).data_type[0], "INT")
        self.assertTrue(is_column_exist, 'Expected column was not found')

    def test_add_categorical_type_column(self):
        input = Input(Schema(self.test_file_path))
        input.add_categorical_column("col_3")
        is_column_exist = False
        for column in input.columns:
            if column.name == 'col_3':
                is_column_exist = True
                self.assertEqual(column.columns_indexes[0], 3)
                self.assertEqual(input.columns.get(column).data_type[0], "CATEGORICAL")
        self.assertTrue(is_column_exist, 'Expected column was not found')

    def test_add_vector_type_column(self):
        schema = Schema(self.test_file_path)
        schema.merge_columns_in_range("merged_col", (3, 5))
        input = Input(schema)
        input.add_vector_column("merged_col")
        is_column_exist = False
        for column in input.columns:
            if column.name == 'merged_col':
                is_column_exist = True
                self.assertTrue(column.columns_indexes == [3, 4, 5])
                self.assertEqual(input.columns.get(column).data_type[0], "VECTOR")
        self.assertTrue(is_column_exist, 'Expected column was not found')




if __name__ == '__main__':
    unittest.main()