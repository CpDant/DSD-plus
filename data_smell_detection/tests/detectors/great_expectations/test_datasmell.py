from great_expectations.profile.base import ProfilerDataType

from data_smell_detection.datasmelldetection.detectors.great_expectations.datasmell import DataSmellRegistry, DataSmell

from .helper_functions import (
    check_data_smell_stored_in_registry,
    check_remaining_data_types_have_no_registered_smells,
    check_get_expectation_type_to_data_smell_type_dict,
    check_get_registered_data_smells
)
from .fixtures import (
    data_smell_registry_empty,
    data_smell_registry_with_data_smell1,
    data_smell_registry_with_data_smell2,
    data_smell_information1,
    data_smell_information2
)


class TestDataSmellMetadata:
    def test_validate_configuration(self):
        # TODO: Implement
        pass


class TestDataSmellRegistry:
    def test_creation(self, data_smell_registry_empty):
        # Iterate over possible values of ProfilerDataType and ensure that
        # after the creation no data smells are stored.
        for profiler_data_type in ProfilerDataType:
            result = data_smell_registry_empty.get_smell_dict_for_profiler_data_type(profiler_data_type)
            assert len(result) == 0

    def test_empty_registry(self, data_smell_registry_empty):
        registry: DataSmellRegistry = data_smell_registry_empty

        # Ensure an empty dictionary is returned for the mapping from
        # expectation types to data smell types.
        check_get_expectation_type_to_data_smell_type_dict(
            returned_dict=registry.get_expectation_type_to_data_smell_type_dict(),
            data_smell_information=[]
        )

        # Ensure that an empty set is returned by get_registered_data_smells()
        check_get_registered_data_smells(
            returned_set=registry.get_registered_data_smells(),
            data_smell_information=[]
        )


    def test_one_data_smell(self, data_smell_registry_with_data_smell1, data_smell_information1):
        # Perform registration of one data smell and ensure that
        # get_smell_dict_for_profiler_data_type() calls return expected
        # results. The registration of the corresponding smell is performed
        # by the fixture.

        registry: DataSmellRegistry = data_smell_registry_with_data_smell1

        # Ensure the registration of the first data smell (extreme value smell)
        # was successful
        check_data_smell_stored_in_registry(
            registry=registry,
            metadata=data_smell_information1.metadata,
            expectation_type=data_smell_information1.expectation_type
        )
        # Ensure that only one data smell has been registered for int and float.
        for data_type in [ProfilerDataType.INT, ProfilerDataType.FLOAT]:
            result = registry.get_smell_dict_for_profiler_data_type(data_type)
            assert len(result) == 1

        # Ensure that the data smell has not been registered for other
        # ProfilerDataTypes (not int and not float).
        check_remaining_data_types_have_no_registered_smells(
            registry,
            data_smell_information1.metadata.profiler_data_types
        )

        # Ensure get_expectation_type_to_data_smell_type_dict method
        # returns expected dictionary.
        expectation_type_to_data_smell_dict = \
            registry.get_expectation_type_to_data_smell_type_dict()
        check_get_expectation_type_to_data_smell_type_dict(
            returned_dict=expectation_type_to_data_smell_dict,
            data_smell_information=[data_smell_information1]
        )

        # A set of one element should be returned by
        # get_registered_data_smells()
        check_get_registered_data_smells(
            returned_set=registry.get_registered_data_smells(),
            data_smell_information=[data_smell_information1]
        )

    def test_two_data_smells(
            self,
            data_smell_registry_with_data_smell2,
            data_smell_information1,
            data_smell_information2):
        # Perform registration of two data smells and ensure that
        # get_smell_dict_for_profiler_data_type() calls return expected
        # results. The registration of the corresponding smells is performed
        # by the fixtures.

        # NOTE: data_smell_registry_with_data_smell2 already has two
        # smells registered.
        registry: DataSmellRegistry = data_smell_registry_with_data_smell2

        # Check if registration of second data smell was successful
        check_data_smell_stored_in_registry(
            registry,
            data_smell_information2.metadata,
            data_smell_information2.expectation_type
        )

        # Ensure that the extreme value smell registered before (data smell 1)
        # is still present.
        check_data_smell_stored_in_registry(
            registry,
            data_smell_information1.metadata,
            data_smell_information1.expectation_type
        )

        # Ensure that only int and float smells have been registered.
        check_remaining_data_types_have_no_registered_smells(
            registry,
            {ProfilerDataType.INT, ProfilerDataType.FLOAT}
        )

        # Information about data smells which were registered at a data smell
        # registry (required for testing)
        data_smell_informatoion_list = [
            data_smell_information1,
            data_smell_information2
        ]

        # Ensure get_expectation_type_to_data_smell_type_dict method
        # returns expected dictionary if two data smells are registered.
        expectation_type_to_data_smell_dict = \
            registry.get_expectation_type_to_data_smell_type_dict()
        check_get_expectation_type_to_data_smell_type_dict(
            returned_dict=expectation_type_to_data_smell_dict,
            data_smell_information=data_smell_informatoion_list
        )

        # A set of two elements should be returned by
        # get_registered_data_smells()
        check_get_registered_data_smells(
            returned_set=registry.get_registered_data_smells(),
            data_smell_information=data_smell_informatoion_list
        )


class TestDataSmell:
    def test_is_abstract(self):
        assert DataSmell.is_abstract() == True

