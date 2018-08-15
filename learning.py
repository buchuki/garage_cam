import time
import cv2
from sklearn import svm
from sklearn.externals import joblib

import numpy
import pandas

import config
from util import iter_source_images, latest_image


def normalize_to_vector(image_frame):
    small = cv2.resize(image_frame, (640, 480))
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    normalized = gray / 255  # Convert to 0-1.0 range

    sample_vector = numpy.reshape(normalized, (normalized.size, 1))

    return sample_vector[:, 0]


def train():
    data_dir = config.options.data_dir
    classification_file = data_dir / "classifications.csv"
    training_parameters_file = data_dir / "svm_trained.joblib"

    classification_rows = pandas.read_csv(
        classification_file, header=None, names=["name", "class"]
    )

    classifications = {}

    for c in classification_rows.itertuples():
        classifications[c[1].strip()] = 1 if c[2] == "OPEN" else 0

    features = []
    expected = []

    for image, frame in iter_source_images():
        classification = classifications.get(image.name)
        if classification is None:
            print(f"No classification for {image.name}")
            continue

        features.append(normalize_to_vector(frame))
        expected.append(classification)

    features = numpy.array(features)
    expected = numpy.array(expected)

    classifier = svm.SVC(C=5)

    now = time.time()
    classifier.fit(features, expected)
    end = time.time()
    print(f"{end-now} seconds")

    joblib.dump(classifier, str(training_parameters_file))


def predict_command():
    image_path = config.options.image
    if not image_path:
        image_path = latest_image()

    print(f"{image_path.name}: {predict(image_path)}")


def predict(image_path):
    data_dir = config.options.data_dir
    training_parameters_file = data_dir / "svm_trained.joblib"

    cv2_image = cv2.imread(str(image_path))

    features = [normalize_to_vector(cv2_image)]
    features = numpy.array(features)

    new_classifier = joblib.load(str(training_parameters_file))

    predictions_val = new_classifier.predict(features)[0]

    return "OPEN" if predictions_val else "CLOSED"
