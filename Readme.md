#  Solution Deployment
```
This solution expects a working tesseract version >4 install in the system ans is present in the path of teh system running this solution
1. The solution is  a CLI tool processed through a valid conda prompt or a python path present cmd.
2. The root directory of the solution is - CLI_TOOL folder.
3. The main file to run the solution is-extractionCLI.py
```

# MONGO CONNECTION
```
1. Make Sure you have a valid mongodb connection in your local system with the data imported in the db-product_scraper_db and collection-products.
2. If the name of the host and port are different please change the configuration in config.json present in CLI_TOOL folder. (Better to run in localhost)
3. If the name of the db and collection are different please change them in appropriate python file. Open extractionCLI.py and you will find comments to change the name present there.
```
# VIRTUAL ENVIRONMENT (ANCONDA ENVIROMENT).
```
1. conda create �n infant python==3.7 �y
2. conda activate infant
3. move into the CLI_TOOL directory where the requirements.txt is present.
4. type command �pip install �r requirements.txt
5. It will take some time to install the required packages.
6. once completed please follow the "solution guide" attached with this submission to run the solution and see its different modes.
```