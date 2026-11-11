"""Two-sided normal interval with supplied known standard deviation."""

import math
import statistics
import sys

from ..core.verification import (
    ScriptDefinition,
    ScriptPort,
    VerificationScript,
    cli_main,
)


def calculate(inputs):
    mean = inputs["mean"]
    sigma = inputs["standard_deviation"]
    confidence = inputs["confidence"]
    if sigma < 0 or not 0 < confidence < 1:
        raise ValueError(
            "standard_deviation must be nonnegative and confidence must be between 0 and 1"
        )
    quantile = statistics.NormalDist().inv_cdf(0.5 + confidence / 2)
    if not math.isfinite(quantile):
        raise ValueError("confidence is too close to 1 for a finite quantile")
    width = sigma * quantile
    return {"lower": mean - width, "upper": mean + width}


class NormalInterval(VerificationScript):
    definition_spec = ScriptDefinition(
        id="normal_interval",
        name="Normal distribution interval",
        description="Two-sided interval from a normal distribution. Bind mean, standard_deviation and confidence (between 0 and 1). This calculation assumes a normal distribution with known standard deviation.",
        inputs=(
            ScriptPort("mean", float, None),
            ScriptPort("standard_deviation", float, None),
            ScriptPort("confidence", float, None),
        ),
        outputs=(
            ScriptPort("lower", float, None),
            ScriptPort("upper", float, None),
        ),
        timeout_ms=3000,
    )

    def calculate(self, inputs, *, requirements=None, mode=None):
        return calculate(inputs)


if __name__ == "__main__":
    sys.exit(cli_main(NormalInterval))
