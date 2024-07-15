from typing import Optional

from great_expectations.core import ExpectationConfiguration
from great_expectations.expectations.expectation import ColumnMapExpectation

from great_expectations.profile.base import ProfilerDataType

from datasmelldetection.core.datasmells import DataSmellType
from datasmelldetection.detectors.great_expectations.datasmell import (
    DataSmell,
    DataSmellMetadata
)

class ExpectColumnValuesToNotContainSpecialCharacterSmell(ColumnMapExpectation, DataSmell):

    data_smell_metadata = DataSmellMetadata(
        data_smell_type=DataSmellType.SPECIAL_CHARACTER_SMELL,
        profiler_data_types={ProfilerDataType.STRING}
    )

    examples = [
        {
            "data": {
                "no_special_character_smell": ["22", "hello", "hello22", "HELLO", "HELLO 22"],
                "two_or_more_faulty_elements_with_punctuation": ["te§t", "t&st", "¿test?", "test ¶", "~test"],
            },
            "tests": [
                {
                    "title": "TC_06_CR_01",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "two_or_more_faulty_elements_with_punctuation", "mostly": 1},
                    "out": {"success": False}
                },

                {
                    "title": "TC_02_CR_01",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "no_special_character_smell", "mostly": 1},
                    "out": {"success": True}
                }
            ]
        }
    ]

    library_metadata = {
        "maturity": "experimental",
        "tags": [
            "experimental"
        ],
        "contributors": [
            "@CpDant",
        ],
        "package": "experimental_expectations",
    }

    map_metric = "column_values.not_match_regex"

    success_keys = (
        "mostly",
        "regex"
    )

    default_kwarg_values = {
        "catch_exceptions": True,
        "regex": r'[^a-zA-Z0-9\s]',
        "mostly": 1
    }

    def validate_configuration(self, configuration: Optional[ExpectationConfiguration]):
        super().validate_configuration(configuration)
        assert configuration is not None
        assert "regex" not in configuration.kwargs, "regex cannot be altered"

expectation = ExpectColumnValuesToNotContainSpecialCharacterSmell()
expectation.register_data_smell()
del expectation