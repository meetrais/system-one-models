"""Ask a yes/no question about a local image, audio, video, or PDF, or an HTTPS URI."""

import argparse

from decision_client import create_client, decisions_model, media_block, print_result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="Local file path, Files API URI, or public/signed HTTPS media URL")
    parser.add_argument("--type", required=True, choices=["image", "audio", "video", "document"])
    parser.add_argument("--mime-type", required=True, help="Real file MIME type, e.g. image/jpeg")
    parser.add_argument("--question", required=True, help="Full yes/no question about the media")
    parser.add_argument("--context", default="Evaluate the attached media.", help="Optional shared text context")
    parser.add_argument("--resolution", choices=["low", "medium", "high", "ultra_high"])
    args = parser.parse_args()
    if not args.question.strip():
        parser.error("--question must not be empty")
    try:
        block = media_block(args.source, args.type, args.mime_type, args.resolution)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    with create_client() as client:
        result = client.decisions.create(
            model=decisions_model(),
            input=[{"type": "text", "text": args.context + "\n"}, block],
            questions={"media_check": {"type": "noul", "instructions": args.question}},
        )
    print_result(result)


if __name__ == "__main__":
    main()
