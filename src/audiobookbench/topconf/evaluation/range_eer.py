"""RangeEER gate.

The project has no verified RangeEER implementation. This explicit refusal
prevents an impressionistic implementation from entering confirmatory code.
"""


class RangeEERNotReady(RuntimeError):
    pass


def range_eer(*_args, **_kwargs):
    raise RangeEERNotReady("RangeEER requires a verified paper/official reference implementation before use")
