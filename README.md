# Love the docs

## Why?

Love the docs is a project to make it easier to understand software packages and APIs.

It's hard to understand how to use a new piece of software. It's often made
unecessarily complex by out of date or incomplete documentation. Eventually, with
persistence, we figure out how a project works by reading the source, looking through
GitHub issues, or developing enough understanding to realize that the authors just
haven't reviewed the documentation in a while.

There are 27 million software developers in the world. Let's say that in a year
each of them spends a single hour in an unnecessary state of confusion because of
unclear documentation. That's 27 million hours. That's three thousand calendar years of
collective confusion. In monetary terms, assuming a global hourly rate of $30/hr,
that's $810 million dollars every year.

Let's show the docs some love!

## What should it look like?

It seems obvioius that LLMs can help us solve this problem. I will take that as an
assumption.

In the long run I think this project should basically be an autonomous system that
visits software packages, gets the code, ensures the code works by running it in it's
own environment, and makes clarity updates to the documentation. The system will
periodically do this or be integrated directly into the workflow when new commits
are made to the repo (continuous integration).

## What is a first step in that direction?

The full system will take time, but I think the first few steps are clear.

- Edit a single file
- Edit the files that file imports
- Continue until we have covered the entire codebase

## What challenges do I foresee?

I think the LLMs are quite capable. The general challenge will be managing the context
window and ensuring that, on large codebases, the system doesn't need to keep the
entire codebase in context.

Ultimately it would be nice to suggest improvements based on a "global view" of the
project, but I don't know how to start there.

## Imagined Usage

### Install

`pip install lovethedocs`

### Optionally configure behavior

Setting tone or comment style though I think the LLM will pick up on most of this
itself.

### Run

`lovethedocs .`

### Result

Beautiful docs.
