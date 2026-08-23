"""Historical LGRC-only handoff entry point, superseded as the umbrella route."""

FIRST_EXECUTABLE_GATE = "GRV8"


def main() -> None:
    raise SystemExit(
        "Use build_grv8_closeout_candidate.py for the general GRC/LGRC next-route "
        "handoff; B1-L remains a separate downstream lane pending accepted GRV-C6"
    )


if __name__ == "__main__":
    main()
