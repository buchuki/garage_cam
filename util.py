from collections import namedtuple
import datetime
from ftplib import FTP

import cv2

import config

ImageData = namedtuple("ImageData", ["path", "image"])


def latest_image():
    return max((p for p in iter_source_image_paths()))


def image_date(image_path):
    return datetime.datetime.strptime(image_path.name, "P%y%m%d%H%M%S%f.jpg")


def iter_source_image_paths(filter=None):
    for path in sorted((config.options.data_dir / "source").iterdir()):
        if path.suffix != ".jpg":
            continue
        if not path.name.startswith("P"):
            continue
        if filter and not filter(path):
            continue
        yield (path)


def iter_source_images(filter=None):
    """
    Loop over all images in the source directory and yield the image
    path and a numpy array containing the image data.
    """
    for path in iter_source_image_paths(filter):
        yield ImageData(path, cv2.imread(str(path)))


def remove_old_images(ftp, rm_dir):
    print(f"removing {rm_dir}")
    files = ftp.nlst(f"pub/{rm_dir}/images")

    for file in files:
        ftp.delete(file)

    ftp.rmd(f"pub/{rm_dir}/images")
    ftp.rmd(f"pub/{rm_dir}")


def get_ftp_files(host, username, password, source_dir, remove_older_than=2):
    ftp = FTP(host, username, password)
    dates = [d.partition("/")[2] for d in ftp.nlst("pub")]
    older_than = (
        datetime.date.today() - datetime.timedelta(days=remove_older_than)
    ).strftime("%Y%m%d")

    for d in dates:
        if d < older_than:
            remove_old_images(ftp, d)

        files = ftp.nlst(f"pub/{d}/images")

        for file in files:
            dest_file = file.rpartition("/")[2]
            ftp.retrbinary(f"RETR {file}", (source_dir / dest_file).open("wb").write)

    ftp.close()


def make_video_of_files(fps=5):
    output_path = config.options.output
    out = None
    first_image = True
    for _, image in iter_source_images():
        if first_image:
            height, width, channels = image.shape
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
            first_image = False

        out.write(image)

        cv2.imshow("video", image)

        if (cv2.waitKey(1) & 0xFF) == ord("q"):
            break

    out.release()
    cv2.destroyAllWindows()
