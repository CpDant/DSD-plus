import os
import great_expectations
from great_expectations.core.batch import BatchRequest

from data_smell_detection.datasmelldetection.detectors.great_expectations.dataset import FileBasedDatasetManager
from data_smell_detection.datasmelldetection.detectors.great_expectations.context import GreatExpectationsContextBuilder
from data_smell_detection.datasmelldetection.core import Dataset

cwd = os.getcwd()
root_path = cwd.split("data_smell_detection")

# NOTE: From view of root directory of package
_test_data_directory = root_path[0] + "data_smell_detection/tests/test_sets"
_test_great_expectations_directory = root_path[0] + "great_expectations"
context_builder = GreatExpectationsContextBuilder(
    _test_great_expectations_directory,
    _test_data_directory
)
context = context_builder.build()

manager = FileBasedDatasetManager(context=context)


class TestFileBasedDatasetManager:
    def test_creation(self):
        FileBasedDatasetManager(context=context)

    def test_get_available_dataset_identifiers(self):
        identifiers = manager.get_available_dataset_identifiers()
        assert isinstance(identifiers, set)
        assert len(identifiers) == 1
        expected_datasets = ["data_smell_testset.csv"]
        # Ensure all expected datasets are returned by
        # get_available_dataset_identifiers.
        assert all([x in identifiers for x in expected_datasets])

    def test_get_dataset(self):
        dataset = manager.get_dataset("data_smell_testset.csv")
        assert isinstance(dataset, Dataset)


class TestDatasetWrapper:
    def test_get_column_names(self):
        dataset = manager.get_dataset("data_smell_testset.csv")

        expected_column_names = [
            "int1",
            "int2",
            "float1",
            "float2",
            "string1",
            "string2",
            "string3"
        ]
        column_names = dataset.get_column_names()
        # Ensure all expected column names are present
        assert all([name in column_names for name in expected_column_names])

    def test_get_great_expectations_dataset(self):
        dataset = manager.get_dataset("data_smell_testset.csv")

        # Extract Great Expectations dataset
        ge_dataset = dataset.get_great_expectations_dataset()
        assert isinstance(ge_dataset, great_expectations.dataset.Dataset)

    def test_get_batch_request(self):
        dataset = manager.get_dataset("data_smell_testset.csv")

        batch_request = dataset.get_batch_request()
        assert isinstance(batch_request, BatchRequest)

        # Check integrity of batch request
        assert batch_request.partition_request is not None
        assert "batch_identifiers" in batch_request.partition_request
        batch_identifiers = batch_request.partition_request["batch_identifiers"]
        assert "filename" in batch_identifiers
        assert batch_identifiers["filename"] == "data_smell_testset.csv"
