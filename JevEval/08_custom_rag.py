"""Judge medical grounding against fictional retrieval documents."""

from rubric_examples import run_example


if __name__ == "__main__":
    run_example("medical_faithfulness", __doc__)
