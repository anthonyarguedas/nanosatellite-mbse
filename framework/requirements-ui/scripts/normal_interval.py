"""Registered numerical analysis. See normal_interval.json for its interface."""
import json
import math
import statistics
import sys

request = json.load(sys.stdin)
inputs = request["inputs"]
mean = inputs["mean"]
sigma = inputs["standard_deviation"]
confidence = inputs["confidence"]
if sigma < 0 or not 0 < confidence < 1:
    raise ValueError("standard_deviation must be nonnegative and confidence must be between 0 and 1")
quantile = statistics.NormalDist().inv_cdf(0.5 + confidence / 2)
if not math.isfinite(quantile):
    raise ValueError("confidence is too close to 1 for a finite quantile")
width = sigma * quantile
json.dump({"lower": mean - width, "upper": mean + width}, sys.stdout, allow_nan=False)
