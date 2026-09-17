from typing import Any

from src.main.api.models.comparison.model_comparator import ModelComparator
from src.main.api.models.comparison.model_comparison_configuration import (
    ModelComparisonConfigLoader
)


class ModelAssertions:
    def __init__(self, request: Any, response: Any):
        self.request = request
        self.response = response

    def match(self) -> 'ModelAssertions':
        config_loader = ModelComparisonConfigLoader(
            'model-comparison.properties'
        )

        rule = config_loader.get_rule_for(self.request)

        if rule is None:
            raise AssertionError(
                f'No comparison rule found for class '
                f'{self.request.__class__.__name__}'
            )

        actual_response_class = self.response.__class__.__name__

        if actual_response_class != rule.response_class_name:
            raise AssertionError(
                f'Expected response class {rule.response_class_name}, '
                f'but got {actual_response_class}'
            )

        result = ModelComparator.compare_fields(
            self.request,
            self.response,
            rule.field_mapping
        )

        if not result.is_success():
            raise AssertionError(
                'Model comparison failed with mismatched fields:\n'
                f'{result.mismatches}'
            )

        return self