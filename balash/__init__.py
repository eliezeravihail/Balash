"""Balash: an AI supervision toolkit.

Two kinds of blocks share one external shape:

* software blocks are plain deterministic code;
* harness blocks package the model for one purpose, with an exact input and
  output specification, validation in code, caching and an explicit
  "uncertain" exit.

Pipelines are YAML files that chain blocks. See docs/balash-design.md.
"""

__version__ = "0.1.0"
