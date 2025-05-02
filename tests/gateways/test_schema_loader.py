import copy

import pytest
from jsonschema.exceptions import ValidationError

from lovethedocs.gateways.schema_loader import VALIDATOR

GOOD_PAYLOAD = {
    "function_edits": [{"qualname": "foo", "signature": "foo()", "docstring": "hi"}],
    "class_edits": [
        {
            "qualname": "Bar",
            "docstring": "hi",
            "method_edits": [
                {
                    "qualname": "baz",
                    "docstring": "hi",
                    "signature": "baz()",
                }
            ],
        }
    ],
}


def test_schema_accepts_good_payload():
    # Should not raise
    VALIDATOR.validate(GOOD_PAYLOAD)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d.pop("function_edits"),  # missing functions
        lambda d: d["function_edits"].append(
            {"qualname": "bar"}  # missing several required fields
        ),
        lambda d: d.pop("class_edits"),  # missing classes
        lambda d: d["class_edits"][0].pop("method_edits"),  # missing class methods
    ],
)
def test_schema_rejects_bad_payload(mutate):
    """
    Runs a test for each lambda in the function list.

    Each lambda modifies GOOD_PAYLOAD in a way that should cause validation to fail.
    """
    bad = copy.deepcopy(GOOD_PAYLOAD)
    mutate(bad)
    with pytest.raises(ValidationError):
        VALIDATOR.validate(bad)
