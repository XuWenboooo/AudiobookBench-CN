# W7 mechanism execution-config equivalence audit v1

    MECHANISM_EXECUTION_CONFIG = FAIL_NOT_UNIQUELY_DERIVABLE
    MECHANISM_CONFIG_SHA256 = NOT_AVAILABLE
    PROTOCOL_SEMANTICS_CHANGED = NO

The frozen protocol and preparation contract specify a permitted family grid,
the fields that a configuration must contain, and a fail-closed rule for
missing fields. They do not specify a per-case family assignment or the
concrete implementation/version/reference/span/seed/quality values. The final
case manifest therefore cannot establish an executable transform from its
schema-derived identity alone.

Any attempt to choose a family, generator, parameters, reference, span, or
seed now would introduce an unapproved scientific choice. No configuration was
invented, no formal W7 asset was transformed, and protocol semantics were not
changed.
