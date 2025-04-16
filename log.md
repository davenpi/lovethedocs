# Log

## Improvements

- Using gpt-4.1 makes this much better. It follows instructions better on formatting.
- Can edit a directory of code.
- Now have deterministic edits (temperature = 0)
- Tweaked the system prompt to only edit the functions that "need it" and tested
  that by running the code through the system twice. I verified that the first pass
  generates edits and then a second pass does nothing.

## Challenges

- Why can't I get trailing tics? Python code is not closed with ``` as expected. USE A SMARTER MODEL (4o or 4.1) and it works.
- **Strange**: If we concatenate two very similar modules with one being the improved
  version of the other, the system tries to only respond with one version of the file.
  For example, with `OG_sample_improved.py` and `sample.py` as the modules, the system
  tries to respond with only `sample.py` in the improved folder. I added a system
  prompt to enforce the correct behavior of editing every file. Check
  `experiments/og/prompt_diffs` for a fuller explanation.
- Improve perfomrance e.g., make sure unused variables are highlighted in `sample.py`
- Will need to have a more consistent definition of "quality" for each package
  that we work with. Want to keep diffs small and match style.
- The way to properly document depends on the version of python we are using. For
  example, in older versions of python (< 3.11) type hinting for methods that return
  an instance of their class use a `TypeVar` with the base class as the bound. In
  [PEP 673](https://peps.python.org/pep-0673/) that was simplified and now methods
  which return an instance of their class are type hinted using a `Self` object from
  the typing library. We may need to allow imports of very basic built in packages
  _if_ the python version is correct.

  Concretely (taken directly from [PEP 673](https://peps.python.org/pep-0673)): In
  Python < 3.11 we do

  ```python
  from typing import TypeVar

  TShape = TypeVar("TShape", bound="Shape")

  class Shape:
      def set_scale(self: TShape, scale: float) -> TShape:
          self.scale = scale
          return self


  class Circle(Shape):
      def set_radius(self, radius: float) -> Circle:
          self.radius = radius
          return self
  Circle().set_scale(0.5).set_radius(2.7)  # => Circle
  # If we didn't use `TShape` and instead used `Shape` as the type hint on `set_scale`,
  # that code would error. Calling `set_scale` would return a `Shape` which has no
  # `set_radius` method.
  ```

  while in Python 3.11+ we do

  ```python
  from typing import Self

  class Shape:
      def set_scale(self, scale: float) -> Self:
          self.scale = scale
          return self


  class Circle(Shape):
      def set_radius(self, radius: float) -> Self:
          self.radius = radius
          return self
  ```

- Aside from proper documentation depending on version, there may be ways to improve
  documentation that require a new import. For example, a user has

  ```python

  class Shape:
    def set_scale(self, scale: float) -> 'Shape':
      self.scale = scale
      return scale
  ```

  but should be doing

  ```python

  from typing import Self

  class Shape:
    def set_scale(self, scale: float) -> Self:
      self.scale = scale
      return scale
  ```

to properly handle subclassing. Right now we will not worry about this and stick to
the rule that we don't edit code.

- Have noticed that the system will remove a line of whitespace even though we said
  don't edit code. I suppose it treats whitespace as fair game.

- Tried to get type hinting on class methods to just include the class, but the system
  keeps putting string literals i.e., `'MyClass'` instead of just `MyClass`. I tried to
  prompt sternly but this still happened. It seems to a good default behavior, but the
  fact that I can't get it to do exactly as I say is unsettling. Need better prompting.
