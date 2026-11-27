"""Check that the final workbook joins to 3,500 raw comments.

The project does not keep a second annotation CSV. Labels are read from
Annotation Dataset/NIRA_Project_Final_Annotation.xlsx.
"""
from load_final_annotation import TASKS, load_final_annotation


def main():
    frame = load_final_annotation()
    if len(frame) != 3500:
        raise SystemExit(f"expected 3,500 rows, found {len(frame)}")
    for task in TASKS:
        if frame[task].str.strip().eq("").any():
            raise SystemExit(f"{task} has an empty label")
    print("NIRA_Project_Final_Annotation.xlsx")
    print("rows", len(frame))
    for task in TASKS:
        print(task, frame[task].value_counts().to_dict())


if __name__ == "__main__":
    main()
