import io

import requests
import numpy as np

from PIL import Image



def pseudo_download_img(img_url):
    res = requests.get(img_url, stream=True)
    count = 1
    while res.status_code != 200 and count <= 5:
        res = requests.get(img_url, stream=True)
        print(f'Retry: {count} {img_url}')
        count += 1
    im = np.array(Image.open(io.BytesIO(res.content)))
    return im