"""Judge refund handling across a complete conversation."""

from eval_helpers import configure_environment, metric_options, parse_args, run_case


def main() -> None:
    args = parse_args(__doc__)
    model = configure_environment()
    from metrics import refund_handling
    from sample_cases import refund_case

    run_case(refund_handling(**metric_options(args, model)), refund_case(), use_evaluate=args.evaluate)


if __name__ == "__main__":
    main()
