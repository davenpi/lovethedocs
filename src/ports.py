"""
ports.py
========

High-level goal
---------------

Declare **ports**—small ``typing.Protocol`` definitions that capture what the
application *needs* from the outside world (e.g., “give me a JSON response for
this prompt”, “load/write a source file”).  They are *contracts*, not
implementations.

Relationship between layers
---------------------------

* **Domain** doesn't import anything.
* **Application** *primarily* codes against these ports, but its orchestration
  modules (e.g., ``run_pipeline.py``) may import the *default* gateway
  implementations so they can be passed in as arguments.  Those defaults can be
  swapped for stubs in tests or for alternative gateways (e.g., a local LLM)
  at run-time.

Why bother?
-----------

* **Testability** - pass an in-memory stub that implements the protocol and
  unit tests stay fast and offline.
* **Flexibility** - infrastructure can change (different file system, new
  OpenAI wrapper, etc.) without touching business logic.
* **Clarity** - newcomers open this file and immediately see the external
  surface area of the core.

Guidelines
----------

1. Keep each protocol minimal—only the methods required by current use-cases.
2. No imports from ``gateways``; this module must remain dependency-free.
3. Document side-effects or guarantees in each method's docstring.
"""

from typing import Protocol


class AIClientPort(Protocol):
    """Turn a prompt into the model's JSON response."""

    def request(self, source_prompt: str, *, model: str) -> dict: ...


class FileWriterPort(Protocol):
    """Abstracts disk I/O so tests can inject an in-memory implementation."""

    def load_modules(self, base_path): ...
    def write_file(self, path, code: str, *, root): ...
