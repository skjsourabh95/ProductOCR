import pytesseract
import json
from pytesseract import Output
import warnings
warnings.filterwarnings("ignore")

with open('config.json') as f:
  CONFIG = json.load(f)
  
def do_ocr(img):

	d = pytesseract.image_to_data(img, output_type=Output.DICT,config = CONFIG["custom_config"])
	n_boxes = len(d['level'])
	results = []
	for i in range(n_boxes):
		(x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
		word = d['text'][i]
		
		if word !=" " and word:
			results.append([word,x, y, w, h])
	return results