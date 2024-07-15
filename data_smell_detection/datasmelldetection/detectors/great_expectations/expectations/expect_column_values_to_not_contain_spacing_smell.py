from typing import Optional

from great_expectations.core import ExpectationConfiguration
from great_expectations.expectations.expectation import ColumnMapExpectation

from great_expectations.profile.base import ProfilerDataType

from datasmelldetection.core.datasmells import DataSmellType
from datasmelldetection.detectors.great_expectations.datasmell import (
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
                "begin_space": [" test", "test", "test"],
                "multiple_begin_space": ["      test", "test", "test"],
                "inner_space": ["test    test", "test", "test"],
                "end_space": ["test ", "test", "test"],
                "multiple_end_space": ["test      ", "test", "test"],
                "no_spacing_smell": ["test", "test test", "test"],
            },
            "tests": [
                {
                    "title": "begin_space_test",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "begin_space", "mostly": 1},
                    "out": {"success": False}
                },

                {
                    "title": "multiple_begin_space_test",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "multiple_begin_space", "mostly": 1},
                    "out": {"success": False}
                },

                {
                    "title": "inner_space_test",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "inner_space", "mostly": 1},
                    "out": {"success": False}
                },

                {
                    "title": "end_space_test",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "end_space", "mostly": 1},
                    "out": {"success": False}
                },

                {
                    "title": "multiple_end_space_test",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "multiple_end_space", "mostly": 1},
                    "out": {"success": False}
                },

                {
                    "title": "no_spacing_smell_test",
                    "exact_match_out": False,
                    "include_in_gallery": True,
                    "in": {"column": "no_spacing_smell", "mostly": 1},
                    "out": {"success": True}
                },
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