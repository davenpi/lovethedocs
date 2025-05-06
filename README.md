# lovethedocs

Make every docstring sparkle.

## Why?

- **One‑command upgrades** – run `lovethedocs update path/`, review, merge.
- **Consistent NumPy‑style** docstrings everywhere – Google and reST next.
- **Scales with `-c/--concurrency`** – fire off many model requests in parallel.
- **Non‑destructive** – edits live in `path/.lovethedocs/` until you accept them.

## Quick start

```bash
pip install lovethedocs        # install
export OPENAI_API_KEY=sk-...   # authenticate
lovethedocs update path/       # stage edits
lovethedocs review path/       # open diffs in your viewer
lovethedocs clean path/        # wipe staged edits

# Stage + review in one go (8 parallel requests)
lovethedocs update -r -c 8 path/
```

Or put the key in a `.env` file at your project root:

```bash
echo "OPENAI_API_KEY=sk-..." > .env
```

## 🎯 Example

Before:

```python
def process_data(data, threshold):
    # Process data according to threshold
    result = []
    for item in data:
        if item > threshold:
            result.append(item * 2)
    return result
```

After:

```python
def process_data(data: list, threshold: float) -> list:
    """
    Filter and transform data based on a threshold value.

    Parameters
    ----------
    data : list
        The input data list to process.
    threshold : float
        Values above this threshold will be processed.

    Returns
    -------
    list
        A new list containing doubled values of items that exceeded the threshold.
    """
    result = []
    for item in data:
        if item > threshold:
            result.append(item * 2)
    return result
```

## 🔧 Usage

Generate, review, and clean up staged files. Use `-c/--concurrency N` to set parallel
request count (default 0).

### Generate Documentation
```bash
# Update docs for a single file
lovethedocs update path/to/your/file.py

# Update docs and review for an entire directory
lovethedocs update -r path/to/your/project/

# Speed up large projects with more workers
lovethedocs update -c 16 path/to/your/project/ 
```

### Review staged edits

`lovethedocs` tries diff viewers in this order:
1.	IDEs launched with the `code` command (VS Code)
2.	git (git diff --no-index)
3.	Colourised terminal diff

```bash
lovethedocs review path/
```

Override with -v/--viewer:

```bash
# Use Git’s difftool
lovethedocs review -v git path/

# Stage and review. Force output to terminal
lovethedocs update -r -v terminal path/ 
```

All new files are staged in a `.lovethedocs/staged/` directory within your
project. For example, if you run `lovethedocs update path/`, the updated
versions will be stored in `path/.lovethedocs/staged/.` When you accept
changes during review, original files are backed up to
`path/.lovethedocs/backups/`.

### Clean up

```bash
lovethedocs clean path/
```

## 🔍 How It Works

LoveTheDocs:

1. Analyzes your Python codebase with LibCST.
2. Extracts function and class information.
3. Uses LLMs to generate docstrings in NumPy style (Google and reST next).
4. Updates your code with LLM generated documentation.
5. Presents changes for your review and approval.

The process is non-destructive - you maintain complete control over which changes to
accept.



## 🛣️ Development Roadmap

### Currently Working On

- **Latency**: Asynchronous model requests
- **UX**: Smaller diffs and more diff reviewers
- **Style**: More doc styles (Google, reStructuredText)
- **Providers**: More model providers (Google, Anthropic, etc.)
- **Error handling**: Improved CLI interface with better error handling

### Future Plans

- **LLM optimized docs**: Give context with the fewest tokens.
- **Automation**: Integration with common CI/CD pipelines
- **Metrics**: Quality metrics and evals.

## 🧰 Technical Details

Under the hood, LoveTheDocs uses:

- A clean domain-driven architecture
- LibCST for reliable code analysis (no regex parsing!)
- LLM-generated docs with a system prompt for each doc style.

## 👥 Contributing

Contributions are welcome! The project is in its early stages, and we're still figuring
out the contribution process. If you're interested:

- Open an issue to discuss ideas or report bugs.
- Submit pull requests for small fixes.
- Open up an issue for larger features.

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file
for details.
