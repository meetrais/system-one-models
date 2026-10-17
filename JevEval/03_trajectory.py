"""Judge a traced agent and its tool calls without generating a response."""

from eval_helpers import configure_environment, metric_options, parse_args


def main() -> None:
    args = parse_args(__doc__, trajectory=True)
    model = configure_environment()
    from deepeval.dataset import EvaluationDataset, Golden
    from deepeval.tracing import observe
    from metrics import tool_use

    @observe(type="tool")
    def order_lookup(order_id: str) -> dict[str, str]:
        return {"order_id": order_id, "status": "in_transit"}

    @observe(type="agent")
    def support_agent(input: str) -> str:
        # This fixed example has one known order. Adapt extraction for real input.
        order = order_lookup("1234")
        return f"Your order #{order['order_id']} is {order['status']}."

    metric = tool_use(**metric_options(args, model))
    dataset = EvaluationDataset(goldens=[Golden(input="Where is my order #1234?")])
    for golden in dataset.evals_iterator(metrics=[metric]):
        support_agent(golden.input)


if __name__ == "__main__":
    main()
