import io
import os
import re
from google.cloud import vision

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "google_creds.json"


def detect_text(img_url):
    """Detects text in the file."""
    client = vision.ImageAnnotatorClient()

    # with io.open(path, 'rb') as image_file:
    #     content = image_file.read()
    # image = vision.Image(content=content)

    image = vision.Image()
    image.source.image_uri = img_url

    response = client.text_detection(image=image)
    texts = response.text_annotations
    results = []
    for text in texts:
        vertices = [(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices]
        results.append((text.description, vertices))

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    ocr_results = results[1:]
    s = " ".join([t for t, v in ocr_results]).lower()
    return s


def parse_s(s):
    total_area_s_cands = re.findall(r"\d+\.?\d+(?=\s?sq)", s)
    total_areas = []
    for total_area_s in total_area_s_cands:
        if total_area_s.split(".")[0].isdigit():
            total_areas.append(float(total_area_s))
    total_areas = [(x if x <= 100 else x / 10.77) for x in total_areas if x != 0]
    return max(total_areas) if len(total_areas) else 0


def detect_area(path):
    """
    Perform GOOGLE OCR and return the area of the floor plan
    """
    s = detect_text(path)
    return parse_s(s)
