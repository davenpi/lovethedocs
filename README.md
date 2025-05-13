# lovethedocs

Polish your Python docs in 30 seconds.

## Why lovethedocs?

Make your docs excellent. It takes ~30 seconds (API calls) and costs 10¢ on small
repos.

* **One‑command upgrades** – `lovethedocs update path/`
* **Choose your style** – `NumPy` (default) or `Google` with `-s/--style`
* **Non‑destructive** – edits live in `.lovethedocs/` until you accept them
* **Parallel & fast** – set `-c/--concurrency` for multiple requests at once

---

## Quick start

```bash
pip install lovethedocs

# 1. Get an OpenAI API key (https://platform.openai.com) and set it:
export OPENAI_API_KEY=sk-...

# 2. Stage docstrings for your project (NumPy style):
lovethedocs update path/to/project/

# ...or choose Google style and review in one shot with 8 workers:
lovethedocs update -s google -r -c 8 path/to/project/
```

### Review & clean

```bash
lovethedocs review path/to/project/   # open diffs in your viewer
lovethedocs clean  path/to/project/   # wipe staged edits
```

Tested on macOS; supported diff viewers: `cursor`, `code`, `git`, `terminal`.
Help adding others is welcome!

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

### CLI cheatsheet

| Goal                    | Command                                          |
|-------------------------|--------------------------------------------------|
| Update one file         | `lovethedocs update my_module.py`                |
| Use Google style        | `lovethedocs update -s google path/`             |
| Speed up (16 workers)   | `lovethedocs update -c 16 path/`                 |
| Force terminal diff     | `lovethedocs review -v terminal path/`           |

---

## Contributors welcome

Issues, discussions, and PRs are encouraged—especially new doc styles, diff viewers, or
provider integrations. Open an issue to get started.

---

*lovethedocs is free to install; LLM calls are billed by OpenAI at your usage rates.*

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file
for details.
