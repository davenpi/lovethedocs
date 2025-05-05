# LoveTheDocs

Automatically enhance your Python documentation to make your code more understandable,
maintainable, and useful.

## 🚀 Why LoveTheDocs?

### Save Developer Time and Money

- **Reduce Documentation Overhead**: Generate high-quality docstrings in seconds
  instead of spending hours manually writing/re-writing them.
- **Cost-Effective**: Improve your entire codebase's documentation for pennies (just
  the cost of model inference) rather than days of developer time.
- **Consistent Style**: Enforce NumPy-style documentation conventions across your
  entire codebase automatically.

### Improve Code Quality

- **Better Readability**: Well-documented code is easier to understand, modify, and
  debug
- **Faster Onboarding**: New team members can quickly grasp your codebase with clear
  documentation
- **Clearer Intentions**: Explicit parameter types and descriptions reveal the purpose
  of your code

### The future!

- **Better AI Integration**: High-quality documentation improves how LLMs understand
  your code
- **Enhanced Tooling**: Better docstrings improve IDE completion, type checking, and
  further documentation generation
- **Maintainability**: Clear documentation reduces technical debt and makes future
  changes easier

## Quick start

```bash
pip install lovethedocs             # 1 Install
export OPENAI_API_KEY=sk-...        # 2 Auth
lovethedocs update -r path/         # 3 Generate + review
```

Or add the API Key to a `.env` file in your project root

```bash
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

## 🔧 Usage

LoveTheDocs offers a simple command-line interface with two main commands:

### Generate Documentation

```bash
# Update documentation for a single file
lovethedocs update path/to/your/file.py

# Update documentation for an entire directory
lovethedocs update path/to/your/project/

# Update multiple paths at once
lovethedocs update path/one/ path/two/ path/three/file.py
```

### Review and Apply Changes

```bash
# Review generated documentation changes (opens in VS Code diff view)
lovethedocs review path/to/your/project/

# Generate and immediately review changes
lovethedocs update path/to/your/project/ -r
```

All new files are staged in a `.lovethedocs/staged/` directory within your
project. For example, if you run `lovethedocs update path/`, the updated
versions will be stored in `path/.lovethedocs/staged/.` When you accept
changes during review, original files are backed up to
`path/.lovethedocs/backups/`.

## 🔍 How It Works

LoveTheDocs:

1. Analyzes your Python codebase with LibCST
2. Extracts function and class information
3. Uses LLMs to generate docstrings in NumPy style (more styles coming).
4. Updates your code with LLM generated documentation
5. Presents changes for your review and approval

The process is non-destructive - you maintain complete control over which changes to
accept.

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
- AI-generated content with specialized prompting strategies
- Comprehensive validation to ensure correct output

## 👥 Contributing

Contributions are welcome! The project is in its early stages, and we're still figuring
out the contribution process. If you're interested:

- Open an issue to discuss ideas or report bugs
- Submit pull requests for small fixes
- Open up an issue for larger features.

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file
for details.
