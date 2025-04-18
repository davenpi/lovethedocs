"""
Script to generate a .jsonl dataset for evals.
"""

from evalinfra.datasets import DatasetBuilder
from pathlib import Path


if __name__ == "__main__":
    builder = DatasetBuilder(
        input_path="evals/sample_code",
        expected_output_path="evals/sample_code/expected_output.txt",
    )
    output_path = Path("evals/data/gen_formatting_discretion.jsonl")
    builder.save_jsonl(output_path)
    print(f"✅ Dataset written to {output_path}")
