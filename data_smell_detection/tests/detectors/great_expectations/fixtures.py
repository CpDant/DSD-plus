from typing import Tuple, List
import pytest
from copy import deepcopy

# A data smell registry with no smells registered.
from data_smell_detection.datasmelldetection.core import DataSmellType
from data_smell_detection.datasmelldetection.detectors.great_expectations.datasmell import DataSmellRegistry, \
    DataSmellMetadata
from great_expectations.profile.base import ProfilerDataType

from .helper_dataclasses import DataSmellInformation


# A data smell registry with no smells registered.
@pytest.fixture
def data_smell_registry_empty() -> DataSmellRegistry:
    return DataSmellRegistry()


# Return data smell information for a simulated data smell for int and float
# columns.
@pytest.fixture
def data_smell_information1() -> DataSmellInformation:
    metadata = DataSmellMetadata(
        data_smell_type=DataSmellType.EXTREME_VALUE_SMELL,
        profiler_data_types={ProfilerDataType.INT, ProfilerDataType.FLOAT}
    )
    expectation_type = "expect_column_values_to_not_contain_extreme_value_smell"
    return DataSmellInformation(
        metadata=metadata,
        expectation_type=expectation_type,
        kwargs={}
    )


# Return the data smell informatoin for a second simulated data smell for float
# columns.
@pytest.fixture
def data_smell_information2() -> DataSmellInformation:
    metadata = DataSmellMetadata(
        data_smell_type=DataSmellType.INTEGER_AS_FLOATING_POINT_NUMBER_SMELL,
        profiler_data_types={ProfilerDataType.FLOAT}
    )
    expectation_type = \
        "expect_column_values_to_not_contain_integer_as_floating_point_number_smell"
    return DataSmellInformation(
        metadata=metadata,
        expectation_type=expectation_type,
        kwargs={}
    )


# Create a data smell registry with exactly one registered data smell
# (data_smell_information1 is registered).
@pytest.fixture
def data_smell_registry_with_data_smell1(data_smell_registry_empty, data_smell_information1) \
        -> DataSmellRegistry:
    registry = deepcopy(data_smell_registry_empty)

    registry.register(
        metadata=data_smell_information1.metadata,
        expectation_type=data_smell_information1.expectation_type
    )
    return registry


# Create a data smell registry with exactly two registered data smells
# (data_smell_information1 and data_smell_information2 are registered).
@pytest.fixture
def data_smell_registry_with_data_smell2(
        data_smell_registry_with_data_smell1,
        data_smell_information2) -> DataSmellRegistry:
    registry = deepcopy(data_smell_registry_with_data_smell1)

    registry.register(
        metadata=data_smell_information2.metadata,
        expectation_type=data_smell_information2.expectation_type
    )
    return registry


# The data smells present in the data smell registry
# `data_smell_registry_with_data_smell1`.
@pytest.fixture
def data_smell_registry_with_data_smell1_information(
        data_smell_information1) -> List[DataSmellInformation]:
    return [
        data_smell_information1
    ]


# The data smells present in the data smell registry
# `data_smell_registry_with_data_smell2`.
@pytest.fixture
def data_smell_registry_with_data_smell2_information(
        data_smell_registry_with_data_smell1_information,
        data_smell_information2) -> List[DataSmellInformation]:
    return data_smell_registry_with_data_smell1_information + \
           [data_smell_information2]


# Information about data smells with custom kwargs. This information list is
# needed to ensure that profiling with a data smell configuration with custom
# kwargs produces the corresponding expectation configurations.
@pytest.fixture
def data_smell_registry_with_data_smell1_custom_kwargs_information() \
        -> List[DataSmellInformation]:
    return [
        DataSmellInformation(
            metadata=DataSmellMetadata(
                data_smell_type=DataSmellType.EXTREME_VALUE_SMELL,
                profiler_data_types={ProfilerDataType.INT, ProfilerDataType.FLOAT}
            ),
            expectation_type="expect_column_values_to_not_contain_extreme_value_smell",
            kwargs={
                "threshold": 3
            }
        )
    ]


# Information about data smells with custom kwargs. This information list is
# needed to ensure that profiling with a data smell configuration with custom
# kwargs produces the corresponding expectation configurations.
@pytest.fixture
def data_smell_registry_with_data_smell2_custom_kwargs_information(
        data_smell_registry_with_data_smell1_custom_kwargs_information) \
        -> List[DataSmellInformation]:
    return data_smell_registry_with_data_smell1_custom_kwargs_information + [
        DataSmellInformation(
            metadata=DataSmellMetadata(
                data_smell_type=DataSmellType.INTEGER_AS_FLOATING_POINT_NUMBER_SMELL,
                profiler_data_types={ProfilerDataType.FLOAT}
            ),
            expectation_type= \
                "expect_column_values_to_not_contain_integer_as_floating_point_number_smell",
            kwargs={
                "mostly": 0.8
            }
        )
    ]


# A data smell registry which contains the data smells in
# `data_smell_registry_with_data_smell1_custom_kwargs_information`.
@pytest.fixture
def data_smell_registry_with_data_smell2_custom_kwargs(
        data_smell_registry_empty,
        data_smell_registry_with_data_smell2_custom_kwargs_information) \
        -> DataSmellRegistry:
    registry = deepcopy(data_smell_registry_empty)

    for data_smell_information in data_smell_registry_with_data_smell2_custom_kwargs_information:
        registry.register(
            metadata=data_smell_information.metadata,
            expectation_type=data_smell_information.expectation_type
        )

    return registry
