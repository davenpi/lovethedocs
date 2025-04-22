import copy
import pytest
from jsonschema.exceptions import ValidationError

from src.infra.schema_loader import VALIDATOR

GOOD_PAYLOAD = {
    "modules": [
        {
            "path": "pkg/foo.py",
            "functions": [
                {
                    "name": "foo",
                    "qualname": "foo",
                    "docstring": "hi",
                    "edit_type": "docstring",
                    "signature": "foo()",
                    "examples": [],
                }
            ],
            "classes": [],
        }
    ],
}


def test_schema_accepts_good_payload():
    # Should not raise
    VALIDATOR.validate(GOOD_PAYLOAD)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d["modules"][0].pop("functions"),  # missing functions
        lambda d: d["modules"][0].pop("path"),  # missing path
        lambda d: d["modules"][0]["functions"].append(
            {"qualname": "bar"}  # missing several required fields
        ),
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
