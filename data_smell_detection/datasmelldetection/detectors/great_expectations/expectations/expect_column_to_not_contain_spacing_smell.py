from typing import Optional

from great_expectations.core import ExpectationConfiguration
from great_expectations.expectations.expectation import ColumnMapExpectation

from great_expectations.profile.base import ProfilerDataType

from data_smell_detection.datasmelldetection.core.datasmells import DataSmellType
from data_smell_detection.datasmelldetection.detectors.great_expectations.datasmell import (
    DataSmell,
    DataSmellMetadata
)

class ExpectColumnValuesToNotContainSpacingSmell(ColumnMapExpectation, DataSmell):

    data_smell_metadata = DataSmellMetadata(
        data_smell_type=DataSmellType.SPACING_SMELL,
        profiler_data_types={ProfilerDataType.STRING}
    )

    examples = [
        {
            "data": {

                "spacing": ["Test", "Test", "Test"]

            },
            "tests": [
                {
                    "title": "test_spacing",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "spacing"},
                    "out": {
                        "success": True,
                        "partial_unexpected_list": []
                    }
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
            "@Tensa53",
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
        "regex": r'^\s|\s\s+|\s$',
        "mostly": 1
    }

    def validate_configuration(self, configuration: Optional[ExpectationConfiguration]):
        super().validate_configuration(configuration)
        assert configuration is not None
        assert "regex" not in configuration.kwargs, "regex cannot be altered"

expectation = ExpectColumnValuesToNotContainSpacingSmell()
expectation.register_data_smell()
del expectation