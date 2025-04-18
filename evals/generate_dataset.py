import json

# Read input code
with open("./sample_code/hello.py", "r") as f:
    input_content = "BEGIN hello.py" + "\n"
    input_content += f.read().strip()
    input_content += "\nEND hello.py"


# Read model response (i.e., expected output)
with open("./sample_code/expected_output.txt", "r") as f:
    expected_output = f.read().strip()

# Format for OpenAI Evals
data = {"item": {"input_content": input_content, "expected_output": expected_output}}

# Write to JSONL file
with open("hello_eval.jsonl", "w") as out_file:
    out_file.write(json.dumps(data) + "\n")
