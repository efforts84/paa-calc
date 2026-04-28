#!/usr/bin/env python3
import csv
from pathlib import Path


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent
    output_path = base_dir / "promotion_fixation.csv"

    rows = [
        [
            "current_grade",
            "current_basic_pay",
            "promoted_grade",
            "lowest_higher_stage",
            "next_step_after_promotion",
        ],
        ["EG-04", "179770", "EG-05", "184840", "194080"],
    ]

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)

    print(output_path)


if __name__ == "__main__":
    main()
