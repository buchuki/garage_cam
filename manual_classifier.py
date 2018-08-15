import shutil
import cv2
import pandas


import config
from util import get_ftp_files
from util import iter_source_image_paths


def classify():
    data_dir = config.options.data_dir
    source_dir = data_dir / "source"
    classification_file = data_dir / "classifications.csv"
    classifications_back = data_dir / "classifications.back"

    print("Loading image files...")
    get_ftp_files(**config.ftp, source_dir=source_dir)

    if classification_file.exists():
        shutil.copy(classification_file, classifications_back)
        classifications = pandas.read_csv(
            classification_file, header=None, names=["name", "class"]
        )
    else:
        classifications = pandas.DataFrame(columns=["name", "class"])

    previous_files = set(classifications.iloc[0:, 0])

    # For ease of entry on a Kinesis keyboard
    print("SPACE means CLOSED")
    print("0 means 10 CLOSED")
    print("BACKSPACE means OPEN")
    print("Q means QUIT")

    closed_count = 0
    for image in iter_source_image_paths():
        if image.name in previous_files:
            continue

        frame = cv2.imread(str(image))

        cv2.imshow("image", frame)
        if closed_count:
            key = cv2.waitKey(1) & 0xFF
            classifications.loc[len(classifications)] = [image.name, "CLOSED"]
            closed_count -= 1
            print(image.name, f"CLOSED ({closed_count})")
            continue

        key = cv2.waitKey(0) & 0xFF

        if key == ord("q"):  # Q means quit
            break
        elif key == 32:  # SPACE means CLOSED
            classifications.loc[len(classifications)] = [image.name, "CLOSED"]
            print(image.name, "CLOSED")
        elif key == 8:  # BACKSPACE means OPEN
            classifications.loc[len(classifications)] = [image.name, "OPEN"]
            print(image.name, "OPEN")
        elif key == ord("0"):  # 0 means "CLOSED 10" (useful for night images)
            closed_count = 10
            classifications.loc[len(classifications)] = [image.name, "CLOSED"]
            print(image.name, "CLOSED (10)")
        else:
            print(key)

    classifications.to_csv(classification_file, index=False, header=False)
    cv2.destroyAllWindows()
