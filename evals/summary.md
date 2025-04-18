# Evaluating the model responses

Evals are tricky. There are many ways to get the right answer in our case.
We will mainly evaluate _formatting_ and _discretion_. Basically we want to ensure
that the model responds in the correct format and that it is not over eager to make
changes to quality work.

## Evals to write

1. Evaluate that model outputs are formatted correctly.
2. Evaluate that the model doesn't try to change it's own work. Don't fix it if it
   ain't broke!
3. Make sure that formatting is correct for multiple files.
4. Make sure formatting is correct for multiple similarly named files.
