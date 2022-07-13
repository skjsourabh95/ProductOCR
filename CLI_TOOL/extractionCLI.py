import argparse
from pymongo import MongoClient
import cv2
from PIL import Image
import io
import json
import os

from bson.objectid import ObjectId
from preprocessing import remove_noise_and_smooth
from tesseract_ocr import do_ocr
from extractor import process_ingredients_nutrients,remove_stop_words
from prediction import predit_type
import tensorflow as tf
import logging
tf.get_logger().setLevel(logging.ERROR)

import warnings

#ignore by message
warnings.filterwarnings("ignore")
                        
                        
with open('config.json') as f:
	CONFIG = json.load(f)


client = MongoClient(host=CONFIG["db_host"], port=CONFIG["db_port"]) ## change the port nad host of teh mongodb in the config file

db = client.product_scraper_db  ## change the db name(current product_scraper_db) here if you have something else


# Create the parser
my_parser = argparse.ArgumentParser(description='Extract the ingredients and nutrients for product')

# Add the arguments
my_parser.add_argument('-id',
                       '--mongo_id',
                       action='store',
                       help='Product Mongo Id')

my_parser.add_argument('-d',
                      '--debug',
                       action='store_true',
                       help='show results in console rather than updating DB')


my_parser.add_argument('-m',
                      '--model',
                       action='store_true',
                       help='uses ML model for predicition rather than rule-based logic')


# Execute the parse_args() method
args = my_parser.parse_args()

id = str(args.mongo_id)




if id!="None":
	print("Processing 1 record with Id-%s"%id)
	data = db.products.find({"_id" : ObjectId(id)}) ## change the collection name here(current products) if you have something else -1
	data = list(data)
	
else:
	print("Processing all records")
	data = db.products.find({}) ## change the collection name here(current products) if you have something else -2
	data = list(data)
	
print("No of Products:",len(data))
print()

if args.model:
    print("using model for prediction")
            
else:
    print("using rule-based logic for prediction")
    
    
for i,d in enumerate(data):
    print("processing product-%s with id-%s"%(i,d["_id"]))
    print("_____________________________________________")
    print()
    ingredients_final=[]
    nutrients_final = []
    
    for j,photo in enumerate(d['photos']):
        image_data = photo['data']
        print("processing Image-",photo['url'])
        
        image = Image.open(io.BytesIO(image_data))
        image.save('test.jpg')
        
        img = cv2.imread('test.jpg') 
        
        if args.model:
            
            pred = predit_type('test.jpg')
            
            if pred == 0:
                
                print("model prediciton-", "No data")
                print("Skipping Image!")
                
            else:
                print("model prediciton-","Data Present")
                
                img = remove_noise_and_smooth('test.jpg')
            
                results = do_ocr(img)
                
                results =  remove_stop_words(results)
                
                ingredients,nutrients = process_ingredients_nutrients(results)
                
                if ingredients:
                    for ing in ingredients:
                        if ing not in ingredients_final:
                            ingredients_final.append(ing)
                if nutrients:
                    for nut in nutrients:
                        if nut not in nutrients_final:
                            nutrients_final.append(nut)
            print()
        
            
        else:
        
            img = remove_noise_and_smooth('test.jpg')
            
            results = do_ocr(img)
            
            results =  remove_stop_words(results)
            
            ingredients,nutrients = process_ingredients_nutrients(results)
            
            if ingredients:
                for ing in ingredients:
                    if ing not in ingredients_final:
                        ingredients_final.append(ing)
            if nutrients:
                for nut in nutrients:
                    if nut not in nutrients_final:
                        nutrients_final.append(nut)
            print()
    
    if (ingredients_final or nutrients_final) and not args.debug:
        print("updating DB")
        result = db.products.update_one(  ## change the collection name here(current products) if you have something else -3
                        {"_id" : ObjectId(d["_id"])},
                        {
                            "$set": {
                                "ingredients": ingredients_final,
                                "nutrients":nutrients_final
                            }

                        }
                    )
    elif (ingredients_final or nutrients_final) and args.debug:
        print("Extracted Items-")
        
        if ingredients_final:
            print("Ingredients")
            for item in ingredients_final:
                print(item)
            print()
        if nutrients_final:
            print("Nutrients")
            for item in nutrients_final:
                print(item)
            print()
            
    print("_____________________________________________")
    print()
if os.path.exists("test.jpg"):
    os.remove("test.jpg")
    