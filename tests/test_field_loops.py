import json
from pathlib import Path

import pytest

from examples.field_loops import presets, trace_loop
from ultracomplexmath import ONE, DomainError, J


def test_four_presets_and_repeated_windings():
    for case, turns, factor in zip(
        presets(), [(1, 0), (0, 1), (1, 1), (0, 0)], [-J, J, -ONE, ONE], strict=True
    ):
        vertices = [complex(*p) for p in case["vertices"]]
        assert trace_loop(vertices).windings == turns
        assert trace_loop(vertices[::-1]).windings == tuple(-t for t in turns)
        double = trace_loop(vertices * 2)
        assert double.windings == tuple(2 * t for t in turns)
        assert double.factor.isclose(ONE)
        assert trace_loop(vertices).factor.isclose(factor)


def test_invalid_closing_edge_and_singular_start():
    for points in [[0j, 1j, 2 + 0j], [1 + 0j, 1j, 2 + 0j]]:
        with pytest.raises(DomainError):
            trace_loop(points)
    with pytest.raises(ValueError):
        trace_loop([0j, 1j])


def test_offline_page_embeds_verified_reference_paths():
    path = Path(__file__).resolve().parents[1] / "docs/gallery/field-loops.html"
    data = json.loads(
        path.read_text()
        .split('<script id="field-data" type="application/json">')[1]
        .split("</script>")[0]
    )
    for case in data["presets"]:
        assert (
            list(trace_loop([complex(*p) for p in case["vertices"]]).windings) == case["windings"]
        )
