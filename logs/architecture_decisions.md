States and critiques major architecture choices.

## Priority fixes

- Use `DocStyle` more. See `DocStyle` and `ModuleEditGenerator` comments below. Current
  mixed usage is error prone.
- See where we are blocked on asynchronous requests/speed.

## Domain

### Models

The domain has four models. Three models represent documentation edits
(`FunctionEdit`, `ClassEdit`, and `ModuleEdit`). One model represents the
fundamental unit we work on, a `SourceModule`.

**Edit Objects**

- Chosen to mimic the model response schema. We demand the model return JSON according
  to the schema in `gateways.lovethedocs_schema.json`.
- IMPROVEMENT: _We should move that schema_ into to the domain. Right now, it's as
  "far out" as possible in `gateways`.
- Simple dataclasses based on a the basic components of module documentation.
- IMPROVEMENT: Allow module docstrings. They give helpful summary information.

**`SourceModule` Object**

- Chosen to represent the "fundamental unit". Directories were used previously.
- Implicit assumption that a given module isn't enormous (zero token counting).
- Directories are too cumbersome (can't run on a single file) and may use too many
  tokens.
- Single class or function objects are too small. LLMs may not have enough
  context to document well. That said, LLMs will adhere to the schema more reliably on
  small inputs. We're at a happpy medium.
- FLAG: Directly relies on LibCST. We get objects from a module to enhance
  model context. The current schema demands the model respond with qualified names for
  edit targeting. We try to make the task easier by passing a modules' qualified names
  to the model (see `PromptBuilder`). LibCST helps us get qualified names.

### Services

**`PromptBuilder`**

- Creates individual prompts for each module in a sequence.
- Each prompt is the "user message" in a chat.
- Does not know about the system/developer prompt.
- Does know about prompt templates (e.g., docstyle), but does nothing with that
  knowledge.
- IMPROVEMENT: Use the template knowledge or remove it.

**`ModulePatcher`**

- Updates module source.
- FLAG: Directly relies on LibCST. Muddies the "pure" domain.
- IMPROVEMENT: Fix the bug in the patcher. It doesn't handle protocol definitions
  correctly. Need much more thorough testing. Try to break it on inputs.
- Didn't implement a port/adapter pattern because LibCST seems stable. Don't want to
  over-engineer for a future use case (e.g., patch code in new languages) before
  nailing the basic flow in python.

**`ModuleEditGenerator`**

- Wraps client request, response validation, and JSON -> `ModuleEdit` mapping.
- FLAG: Smells like asynchronous requests will be a challenge. Will need to refactor.
  This may move up the stack.
- FLAG: Accesses a `style` attribute on the client that isn't exposed in the client
  port. This `style` is not a `DocStyle` type. Instead it's a string.
- IMPROVEMENT: Make the style more clear. When a user creates a `ModuleEditGenerator`,
  it should be clear what style edits will be made. Right now that's clear b/c they need
  to pass in a client and the client (implcitly right now) requires a style. Make the
  client `style` explicit at the domain level.

### Templates

- Holds system prompt.
- Prompt specifics dictate model behavior.
- IMPROVEMENT: Ongoing tweaks to system prompt.
- IMPROVEMENT: Move response json schema here? That makes the coupling obvious.

**`PromptTemplateRepository`**

- Gets developer prompts by style. NumPy prompt is the only one defined so far.

### Use Cases

- Orchestrates across the domain.

**`DocumentationUpdateUseCase`**

- Encapsulates usage. Provides a clear public API.
- Simplifies `application.run_pipeline`.
- IMPROVEMENT: Different types of "style" are passed around. This class takes a
  `DocStyle` as it's `style` parameter, but `ModuleEditGenerator` looks for a string
  type style on its LLM client (which has no `style` exposed on it's port protocol).

### Doc Styles

- Captures basic information about different documentation styles (e.g, NumPy, Google).
- Largely unused. Either remove or refactor to use the style uniformly (e.g., demand
  client ports have a `DocStyle`).
- Only have NumPy doc style so far.

## Questions to ponder:

1. How does the current architecture support or hinder the product's primary value
   proposition?
2. Which architectural improvements would deliver the most user value?
3. Are there architectural choices that limit potential use cases?
