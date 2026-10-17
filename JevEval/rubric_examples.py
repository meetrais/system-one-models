"""Shared entry point for the five custom rubric examples."""

from eval_helpers import configure_environment, metric_options, parse_args, run_case


def run_example(rubric: str, description: str) -> None:
    args = parse_args(description, conversation=True)
    model = configure_environment()
    # Load DeepEval only after loading the environment, as in the original samples.
    import metrics
    from sample_cases import rubric_case

    metric = getattr(metrics, rubric)(
        conversational=args.multi_turn, **metric_options(args, model)
    )
    case = rubric_case(rubric, conversational=args.multi_turn)
    run_case(metric, case, use_evaluate=args.evaluate)
