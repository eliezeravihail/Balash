import pytest

from balash.core.pipeline import Pipeline, PipelineError


def test_unknown_block_is_rejected():
    with pytest.raises(KeyError):
        Pipeline.from_dict({"pipeline": "p", "steps": [{"id": "a", "block": "nope"}]})


def test_input_must_be_an_earlier_step():
    with pytest.raises(PipelineError):
        Pipeline.from_dict(
            {"pipeline": "p", "steps": [{"id": "a", "block": "notify", "input": "b"}, {"id": "b", "block": "notify"}]}
        )


def test_duplicate_step_ids_are_rejected():
    with pytest.raises(PipelineError):
        Pipeline.from_dict({"pipeline": "p", "steps": [{"id": "a", "block": "notify"}, {"id": "a", "block": "notify"}]})


def test_params_reach_the_block(h):
    p = Pipeline.from_dict({"pipeline": "p", "steps": [{"id": "t", "block": "balances_text", "tolerance": 2}]})
    assert p.steps[0].params == {"tolerance": 2}


def test_failed_step_marks_the_run_failed(h):
    p = Pipeline.from_dict({"pipeline": "p", "steps": [{"id": "s", "block": "monthly_stats"}]})
    from balash.core.record import Record

    with pytest.raises(PipelineError):
        p.run([Record("month", {"month": "bad"})], h.service.context(h.out, "x"))
    run = h.service.store.one("SELECT status FROM runs WHERE pipeline = 'p'")
    assert run["status"] == "failed"
