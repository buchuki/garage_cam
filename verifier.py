import pandas

import config
from learning import train, predict


def verify():
    data_dir = config.options.data_dir
    classification_file = data_dir / "classifications.csv"

    classification_rows = pandas.read_csv(
        classification_file, header=None, names=["name", "class"]
    )

    num_rows = classification_rows.shape[0]
    to_train = classification_rows.iloc[: (num_rows // 2), :]
    to_validate = classification_rows.iloc[(num_rows // 2) :, :]

    train(to_train, "svm_validate.joblib")

    for row in to_validate.itertuples():
        image_name = row[1]
        expected = row[2]

        if not image_name:
            continue

        predicted = predict(data_dir / "source" / image_name, "svm_validate.joblib")
        if expected != predicted:
            print(f"expected {image_name} to be {expected} but got {predicted}")
