from pathlib import Path
import sys
import io
import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
import os
import deepstack.core as ds
import utils
import const

## Depstack setup
DEEPSTACK_IP = os.getenv("DEEPSTACK_IP", "localhost")
DEEPSTACK_PORT = os.getenv("DEEPSTACK_PORT", 5000)
DEEPSTACK_API_KEY = os.getenv("DEEPSTACK_API_KEY", "")
DEEPSTACK_TIMEOUT = os.getenv("DEEPSTACK_TIMEOUT", 10)

DEFAULT_CONFIDENCE_THRESHOLD = 0
TEST_IMAGE = "street.jpg"

predictions = None


@st.cache
def process_image(pil_image, dsobject):
    image_bytes = utils.pil_image_to_byte_array(pil_image)
    dsobject.detect(image_bytes)
    predictions = dsobject.predictions
    return predictions


st.title("Deepstack Object detection")
img_file_buffer = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

st.sidebar.title("Parameters")
confidence_threshold = st.sidebar.slider(
    "Confidence threshold", 0, 100, DEFAULT_CONFIDENCE_THRESHOLD, 1
)

if img_file_buffer is not None:
    pil_image = Image.open(img_file_buffer)

else:
    pil_image = Image.open(TEST_IMAGE)

dsobject = ds.DeepstackObject(
    DEEPSTACK_IP, DEEPSTACK_PORT, DEEPSTACK_API_KEY, DEEPSTACK_TIMEOUT
)

predictions = process_image(pil_image, dsobject)
objects = utils.get_objects(predictions, pil_image.width, pil_image.height)

# Filter objects
objects = [obj for obj in objects if obj["confidence"] > confidence_threshold]

draw = ImageDraw.Draw(pil_image)
for obj in objects:
    name = obj["name"]
    confidence = obj["confidence"]
    box = obj["bounding_box"]
    box_label = f"{name}: {confidence:.1f}%"

    utils.draw_box(
        draw,
        (box["y_min"], box["x_min"], box["y_max"], box["x_max"]),
        pil_image.width,
        pil_image.height,
        text=box_label,
        color=const.YELLOW,
    )

st.image(
    np.array(pil_image), caption=f"Processed image", use_column_width=True,
)
st.write(objects)
