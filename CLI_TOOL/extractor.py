from spellchecker import SpellChecker
import enchant
import re
import distance
import warnings
warnings.filterwarnings("ignore")
import nltk
from nltk.corpus import stopwords
try:
     nltk.data.find('tokenizers/stopwords')
except LookupError:
    nltk.download('stopwords')

def correct_spelling(cand):
    spell = SpellChecker()
    spell.word_frequency.load_text_file('corpora.txt')
    return spell.correction(cand)
	
def get_unigrams_ingredients(final_items):
    pwl = enchant.request_pwl_dict("corpora.txt")
    dic = enchant.DictWithPWL("en","corpora.txt")
    ingredients_found = []
    for i in range(len(final_items)-1):
        cand = final_items[i][0]
        if dic.check(cand):
    #         print(cand)
            ingredients_found.append(cand)
    return ingredients_found
	
def get_bigrams_ingredients(final_items):
    pwl = enchant.request_pwl_dict("corpora.txt")
    dic = enchant.DictWithPWL("en","corpora.txt")
    ingredients_found = []
    indexes_2_remove =[]
    for i in range(len(final_items)-1):
        cand = ' '.join([final_items[i][0],final_items[i+1][0]])
        if dic.check(cand):
    #         print(cand)
            indexes_2_remove.append(i)
            indexes_2_remove.append(i+1)
            ingredients_found.append(cand)
    return indexes_2_remove,ingredients_found
	
def merge_boxes(rects):
    """Takes the corpus from word boxes and returns a dictionary with merger boxes coordinates and word contained"""
    acceptedRects = []
    rectsUsed=[False]*len(rects)
    
    # Iterate all initial bounding rects
    for supIdx, supVal in enumerate(rects):
#         print(supVal,supIdx)
        if (rectsUsed[supIdx] == False):
            # Initialize current rect
            currxMin = supVal[1]
            currxMax = supVal[3]
            curryMin = supVal[2]
            curryMax = supVal[4]
#             print("current:",currxMin, curryMin, currxMax,  curryMax)
            # This bounding rect is used
            rectsUsed[supIdx] = True
            mergeword=supVal[0]
            # Iterate all initial bounding rects
            # starting from the next
            thr=1.50
            xThr=thr*(currxMax-currxMin)/len(mergeword)
            yThr=curryMax-curryMin
            for subIdx, subVal in enumerate(rects[(supIdx+1):], start = (supIdx+1)):

                # Initialize merge candidate
                candxMin = subVal[1]
                candxMax = subVal[3]
                candyMin = subVal[2]
                candyMax = subVal[4]

                # Check if x distance between current rect
                # and merge candidate is small enough
                if currxMax+xThr>=candxMin and currxMax-xThr<=candxMax and curryMax+yThr>=candyMax and curryMax-yThr<=candyMax:

                    # Reset coordinates of current rect
                    mergeword+=" "+subVal[0]
                    currxMax = candxMax
                    curryMax = candyMax
#                     print("Temp:",currxMin, curryMin, currxMax,  curryMax)
                    # Merge candidate (bounding rect) is used
                    rectsUsed[subIdx] = True
                else:
                    break
#             print("final:",currxMin, curryMin, currxMax,  curryMax)
            # No more merge candidates possible, accept current rect
            acceptedRects.append([mergeword,currxMin, curryMin, currxMax,  curryMax])
    final_merges=[]
    for merge in acceptedRects:
            final_merges.append([merge[0],merge[1],merge[2],merge[3],merge[4]])
    return  final_merges

def get_correct_nutrients(array_list):
    buffer_y = 10
    array_list.sort(key = lambda x: (x[1],x[2]))
    sorted_array_list = sorted(array_list,key = lambda x: (x[2],x[1]))
    current_element = sorted_array_list[0]
    for i in range(1,len(sorted_array_list)):
        if(abs(sorted_array_list[i][2] - current_element[2]) <= buffer_y):
            sorted_array_list[i][2] = current_element[2]
        current_element = sorted_array_list[i]
    sorted_array_list.sort(key = lambda x: (x[2],x[1]))
#     print(sorted_array_list)


    refrence_list = []
    for i in range(len(sorted_array_list)):
        if(re.match(r"diluted",sorted_array_list[i][0].lower())):
            refrence_list.append(sorted_array_list[i])
        elif(re.match(r"per",sorted_array_list[i][0].lower())):
            refrence_list.append(sorted_array_list[i-1])
            refrence_list.append(sorted_array_list[i])
    # print(refrence_list)

    sorted_array_list_new = [x for x in sorted_array_list if x not in refrence_list]
    sorted_array_list = sorted_array_list_new
    correct_pairs =[]
    remove_indexes =[]
    for i in range(len(sorted_array_list)-1):
        if sorted_array_list[i+1][0].isdigit() and len(sorted_array_list[i][0])>=3:
            correct_pairs.append(sorted_array_list[i][0]+" "+sorted_array_list[i+1][0])
            remove_indexes.append(i)
            remove_indexes.append(i+1)
    for i in range(len(sorted_array_list)-1):
        if sorted_array_list[i+1][0].lower() in ["mcg","mg","g","iu"] and len(sorted_array_list[i][0])>=3 and sorted_array_list[i+2][0].lower().isdigit():
            correct_pairs.append(sorted_array_list[i][0]+" "+sorted_array_list[i+1][0]+" "+sorted_array_list[i+2][0])
            remove_indexes.append(i)
            remove_indexes.append(i+1)
            remove_indexes.append(i+2)
    sorted_array_list =[item for i,item in enumerate(sorted_array_list) if i not in remove_indexes]
    return correct_pairs,sorted_array_list,refrence_list
	

def get_pairs_nutrients(correct_pairs):
    final_nutrients=[]
    for pair in correct_pairs:
        items = pair.split()
        if len(items)>=3:
            amount = items[-1]
            unit = items[-2]
            if unit[0]=="m" and len(unit)==2:
                unit ="mg"
            elif unit[0]=="m" and len(unit)==3:
                unit="mcg"
            else:
                unit="IU"
            name = "-".join(items[:-2])

            if "mg" in name[-2:]:
                name = name[:-2]
                unit = name[-2:]
            elif "mcg" in name[-3:]:
                name = name[:-3]
                unit = name[-3:]
            name = correct_spelling(name)
            final_nutrients.append((name,unit,amount))

        else:
            amount = items[-1]
            name = "-".join(items[:-1])
            name = correct_spelling(name)
            final_nutrients.append((name,amount))
    return final_nutrients

def get_singe_nutrients(sorted_array_list):
    final_nutrients =[]
    single_nutrients =[]
    for i in sorted_array_list:
        name = correct_spelling(i[0])
        single_nutrients.append(name)
    single_nutrients = list(set(single_nutrients))
    pwl = enchant.request_pwl_dict("corpora.txt")
    dic = enchant.DictWithPWL("en","corpora.txt")
    for i in single_nutrients:
        cand = i.split()[0]
        if dic.check(cand) and not cand.isdigit() and len(cand)>=3 and cand not in ["vitamin","vitamins","mineral","minerals","nutrients","nutrient"] :
            final_nutrients.append((cand,))
    return final_nutrients

def get_reference(refrence_list):
    for ref in refrence_list:
        if "per" in ref[0]:
            return "per 100 calories"
    return 0

def check_ingredients(results):
    with open('ingredients.txt', 'r') as f:
        ingredients = f.read().splitlines()
    count=0
    read = []
    for result in results:
        if result[0].lower() in ingredients and result[0].lower() not in read:
            count+=1
            read.append(result[0].lower())
        if count>=5:
            return True
    return False

def check_nutrients(results):
    with open('nutrients.txt', 'r') as f:
        nutrients = f.read().splitlines()
    count=0
    read = []
    for result in results:
        
        if result[0].lower() in nutrients and result[0].lower() not in read:
            count+=1
            read.append(result[0].lower())
        if count>=5:
            return True
    return False


	
def get_response(results):
    """retuns a dict of items"""
    ingredients =False
    nutrients = False
    for token in results:
        score=1-(distance.levenshtein(token[0].lower(),"ingredients")/max(len(token[0].lower()),len("ingredients")))
        if score >0.70 and not ingredients:
            ingredients = token
        elif score >0.70 and ingredients:
            if token[1]<ingredients[1]:
                ingredients = token
        
        score=1-(distance.levenshtein(token[0].lower(),"nutrients")/max(len(token[0].lower()),len("nutrients")))
        if score >0.70:
            nutrients = token
            
#         score=1-(distance.levenshtein(token[0].lower(),"nutrition")/max(len(token[0].lower()),len("nutrition")))
#         if score >0.70:
#             nutrients = token
            
#    print(ingredients)
#    print(nutrients)
    
    
    ingredients_candidates =[]
    nutrients_candidates = []
    final_ingredients =[]  
    final_nutrients = []
    nutrients_found = []
    ingredients_found =[]
    refrence_list =[]
    
    if ingredients and nutrients:
        print("both nutrients and ingredients present")
        
        if (ingredients[1] > nutrients[1]) and (abs(ingredients[2]-nutrients[2])<=10):
#            print("side-by-side-nutrients-first")
            x_min = nutrients[1]
            x_max = ingredients[1]
            nutrients_candidates = [item for item in results if item[1]>x_min and item[1]<x_max-5]
            ingredients_candidates = [item for item in results if item[1]>x_max-5]
    
        elif (ingredients[1] < nutrients[1]) and (abs(nutrients[2]-ingredients[2])<=10):
#            print("side-by-side-ingredients-first")
            x_min = ingredients[1]
            x_max = nutrients[1]
            ingredients_candidates = [item for item in results if item[1]>x_min and item[1]<x_max-5]
            nutrients_candidates = [item for item in results if item[1]>x_max-5]
            
        elif (ingredients[2] < nutrients[2]) and (abs(nutrients[1]-ingredients[1])<=30):
#            print("up-down-ingredients-first")
            y_min = ingredients[2]
            y_max = nutrients[2]
            ingredients_candidates = [item for item in results if item[2]>y_min and item[2]<y_max]
            nutrients_candidates = [item for item in results if item[2]>y_max and item[3]>=20 and item[4]>=20]
            
            
        elif ingredients[2] > nutrients[2] and (abs(nutrients[1]-ingredients[1])<=30):
#            print("up-down-nutrients-first")
            y_max = ingredients[2]
            y_min = nutrients[2]
            ingredients_candidates = [item for item in results if item[2]>y_max]
            nutrients_candidates = [item for item in results if item[2]>y_min and item[2]<y_max and item[3]>=20 and item[4]>=20]
            
                    
    elif not ingredients and nutrients:
        print("only nutrients present")
        nutrients_candidates = [item for item in results if item[3]>=20 and item[4]>=20]
        
        
    elif ingredients and not nutrients:
        print("only ingredients present")
        ingredients_candidates = results
        
    else:
        print("checking for other rules to confirm")
        ing_present = check_ingredients(results)
        nut_present = check_nutrients(results)
        if ing_present:
            print("ingredients found!")
            ingredients_candidates = results
        
        if nut_present:
            print("nutrients found!")
            nutrients_candidates = [item for item in results if item[3]>=20 and item[4]>=20]
        if not ing_present and not nut_present:
            print("No data present skipping Image!")
                            
    
        
    if nutrients_candidates:
        print("Extarcting Nutrients!")
        for item in nutrients_candidates:
            nutrient = item[0].lower()
            nutrient = nutrient.strip("[] -" )
            nutrient = re.sub('[",.\':()*]', '', nutrient)
            item[0] = nutrient
            if nutrient and nutrient!=" ":
                final_nutrients.append([nutrient,item[1],item[2],item[1]+item[3],item[2]+item[4]])
        nutrients_found = merge_boxes(final_nutrients)
        correct_pairs,incorrect_pairs,refrence_list = get_correct_nutrients(nutrients_found)
        final_nutrients = get_pairs_nutrients(correct_pairs)
        final_nutrients = final_nutrients + get_singe_nutrients(incorrect_pairs)
        
                
    if ingredients_candidates:
        print("Extarcting Ingredients!")
        for item in ingredients_candidates:
            ingredient = item[0].lower()
            if not re.match("[0-9]", ingredient) and len(ingredient)>2:
                ingredient = ingredient.strip("[] -" )
                ingredient = re.sub('[".,\':()*]', '', ingredient)
                score=1-(distance.levenshtein(ingredient.lower(),"contains")/max(len(token[0].lower()),len("contains")))
                if score >0.70:
                    break
                item[0] = ingredient
                ingredient = correct_spelling(ingredient)
                final_ingredients.append([ingredient,item[1],item[2],item[1]+item[3],item[2]+item[4]])  
                
        indexes_2_remove,ingredients_found= get_bigrams_ingredients(final_ingredients)
        final_ingredients = [v for i,v in enumerate(final_ingredients) if i not in indexes_2_remove]
        ingredients_found = ingredients_found+get_unigrams_ingredients(final_ingredients)

            
                
    return ingredients_found,final_nutrients,refrence_list

def process_ingredients_nutrients(results):
    ingredients_found,nutrients_found,refrence_list = get_response(results)
    ingredients =[]
    nutrients =[]
    if not ingredients_found and not nutrients_found:
        return False,False
    ref = get_reference(refrence_list)
    for ingredient in ingredients_found:
        ingredients.append({"name":ingredient,
                           "amount":0,
                            "unit":0,
                            "referenceValue":ref
                           })
    for nutrient in nutrients_found:
        if len(nutrient) == 2:
            nutrients.append({"name":nutrient[0],
                            "amount":nutrient[1],
                            "unit":0,
                            "referenceValue":ref
                           })
        if len(nutrient) ==1:
            nutrients.append({"name":nutrient[0],
                            "amount":0,
                            "unit":0,
                            "referenceValue":ref
                           })
        if len(nutrient) ==3:
            nutrients.append({"name":nutrient[0],
                            "amount":nutrient[2],
                            "unit":nutrient[1],
                            "referenceValue":ref
                           })
    print("Extraction Complete!")
    return ingredients,nutrients

def remove_stop_words(results):
    sw = stopwords.words("english")
    final_results =[]
    for res in results:
        if res[0].lower() not in sw:
            final_results.append(res)
    return final_results
