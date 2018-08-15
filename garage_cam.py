#!/usr/bin/env python

import argparse
import config
from pathlib import Path
from util import make_video_of_files
from manual_classifier import classify
from learning import train, predict_command as predict
from send_message_service import message_loop


def abs_path(path):
    return Path(path).absolute()


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser.add_argument(
        "--data_dir",
        type=abs_path,
        default=abs_path("__file__").parent / "data",
        help="Path to the garage cam data directory",
    )

    make_video_parser = subparsers.add_parser(
        "make_video", help="Make a video of all available source images"
    )
    make_video_parser.add_argument(
        "output", type=abs_path, help="Path to the output video file"
    )
    make_video_parser.set_defaults(func=make_video_of_files)

    manual_classify_parser = subparsers.add_parser(
        "manual_classify",
        help="Manually classify source images that have not"
        " previously been classified",
    )
    manual_classify_parser.set_defaults(func=classify)

    train_parser = subparsers.add_parser("train", help="Train SVM on classified images")
    train_parser.set_defaults(func=train)

    predict_parser = subparsers.add_parser(
        "predict", help="Predict whether image is " "OPEN or CLOSED"
    )
    predict_parser.add_argument(
        "image",
        default=None,
        type=abs_path,
        nargs="?",
        help="Name of image to predict. "
        "If not supplied, use most recent source image",
    )
    predict_parser.set_defaults(func=predict)

    message_service_parser = subparsers.add_parser(
        "message_service",
        help="Start service that sends an IFTTT message when door status changes",
    )
    message_service_parser.set_defaults(func=message_loop)

    args = parser.parse_args()
    config.options = args
    args.func()


if __name__ == "__main__":
    main()
