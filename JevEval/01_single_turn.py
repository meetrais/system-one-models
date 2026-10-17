"""Judge whether a weather response is faithful to its tool output."""

from eval_helpers import configure_environment, metric_options, parse_args, run_case


def main() -> None:
    args = parse_args(__doc__)
    model = configure_environment()
    from metrics import tool_faithfulness
    from sample_cases import weather_case

    run_case(tool_faithfulness(**metric_options(args, model)), weather_case(), use_evaluate=args.evaluate)


if __name__ == "__main__":
    main()
