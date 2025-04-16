# Log

## Improvements

- Now have deterministic edits (temperature = 0)
- Tweaked the system prompt to only edit the functions that "need it" and tested
  that by running the code through the system twice. I verified that the first pass
  generates edits and then a second pass does nothing.

## Challenges

- Will need to have a better more consistent definition of "quality" for each package
  that we work with. Want to keep diffs small.
