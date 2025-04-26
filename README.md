# LoveTheDocs

Enhance Python docs with AI to make your code more understandable, maintainable,
and useful.

## 🌟 Why LoveTheDocs?

Good documentation is essential for two key reasons:

1. **Developer Experience**: Quality documentation leads to higher quality code written in less time. Developers spend less time figuring out how libraries work and more time building.

2. **AI Integration**: LLMs are increasingly important consumers of documentation. The quality of AI assistance depends directly on the quality of the documentation it reads.

## 🚀 Quick Start

LoveTheDocs is not yet available on PyPI. To use it:

1. Clone the repository:

   ```bash
   git clone https://github.com/davenpi/lovethedocs.git
   cd lovethedocs
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key:

   ```bash
   # Create a .env file in the project root
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```

4. Run LoveTheDocs on your Python project:

   ```bash
   # Using the provided alias (recommended)
   source .aliases
   lovethedocs path/to/your/python/code

   # Or run directly
   python -m src.cli.lovethedocs path/to/your/python/code
   ```

5. Find improved documentation in the `_improved` directory.

## 🔍 How It Works

LoveTheDocs:

1. Analyzes your Python codebase
2. Extracts class and function information
3. Uses AI (for now Open AI models) to generate improved docstrings in NumPy style
4. Updates your code with the enhanced documentation
5. Formats the result with black

The result is consistent, comprehensive documentation with a lot less effort.

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

### Foundation (Current Focus)

#### User Experience Improvements

- [ ] Add asynchronous model requests for faster processing
- [ ] Create scripts to automatically view and incorporate diffs
- [ ] Improve CLI interface with progress indication and better error handling
- [ ] Add support for configuration files to customize behavior

#### Architecture Enhancements

- [ ] Improve core/domain logic. Extend domain services for clarity.
- [ ] Add support for multiple model providers (Anthropic + Open AI)
- [ ] Implement adaptable documentation style templates (NumPy vs. Google)
- [ ] Improve module and package level documentation generation

#### Evaluation and Telemetry

- [ ] Create model evaluation pipeline to measure documentation quality
- [ ] Iteratively refine prompting strategies based on quality metrics
- [ ] Build telemetry system to track usage patterns and failure modes
- [ ] Implement logging infrastructure for systematic performance analysis
- [ ] Develop feedback mechanisms to improve future documentation

#### Automation and Integration

- [ ] Build GitHub action for automated documentation improvements
- [ ] Create PR system for seamless code improvement integration
- [ ] Add continuous integration hooks

### Future Directions

#### AI-Optimized Documentation

- [ ] Research and develop documentation formats specifically designed for LLM consumption
- [ ] Create exporters for compact schema representations of docstrings
- [ ] Implement dual-format documentation that serves both human and AI readers
- [ ] Build tools to analyze documentation information density and LLM comprehension

#### Documentation Quality Assurance

- [ ] Integrate doctest validation for all code examples
- [ ] Implement automated repair of failing examples in documentation
- [ ] Create validation pipelines for documentation correctness and completeness
- [ ] Develop metrics for documentation quality beyond traditional coverage

## 🧰 Technical Details

LoveTheDocs uses a clean architecture with:

- Domain models for documentation edits
- LibCST for code manipulation (no regex parsing!)
- OpenAI GPT-4 with a specialized prompting strategy
- Dependency injection for testability

## 👥 Contributing

Contributions to LoveTheDocs are welcome! The project is in its early stages, and I'm
still figuring out the contribution process. If you're interested in contributing:

- Open an issue to discuss ideas or report bugs
- Submit pull requests for small fixes
- For larger features, please reach out to me first at davenport.ianc@gmail.com

Thanks!

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file
for details.
