# -*- coding: utf-8 -*-
"""
Created on Sat Jul 28 11:45:18 2018

@author: @cccruzr
"""

#Importing necessary libraries
import sys
import sqlite3
import requests
import os
import xml.etree.ElementTree as ET

# function: Delete existing database ------------------------------------------
def deleteDB(database_fp):
    """
    Delete existing database.
    -----
    database_fp: database file path (string)
    """
    if(os.path.isfile(database_fp)):
        os.remove(database_fp)
        print("MESSAGE: Existing database deleted.")


# function: Build database ----------------------------------------------------
def buildDB():
    """
    Build database with all product categories using the ebay API
    """
    
    # Define headers, xml data and api URL
    headers = {
        'X-EBAY-API-CALL-NAME' : 'GetCategories',
        'X-EBAY-API-APP-NAME' : 'EchoBay62-5538-466c-b43b-662768d6841',
        'X-EBAY-API-CERT-NAME' : '00dd08ab-2082-4e3c-9518-5f4298f296db',
        'X-EBAY-API-DEV-NAME' : '16a26b1b-26cf-442d-906d-597b60c41c19',
        'X-EBAY-API-SITEID' : '0',
        'X-EBAY-API-COMPATIBILITY-LEVEL': '861'
    }
    
    xml_data = """
        <?xml version='1.0' encoding='utf-'?>
        <GetCategoriesRequest xmlns="urn:ebay:apis:eBLBaseComponents">
            <RequesterCredentials>
              <eBayAuthToken>AgAAAA**AQAAAA**aAAAAA**PlLuWA**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wFk4GlDpaDpAudj6x9nY+seQ**LyoEAA**AAMAAA**wSd/jBCbxJHbYuIfP4ESyC0mHG2Tn4O3v6rO2zmnoVSF614aVDFfLSCkJ5b9wg9nD7rkDzQayiqvwdWeoJkqEpNQx6wjbVQ1pjiIaWdrYRq+dXxxGHlyVd+LqL1oPp/T9PxgaVAuxFXlVMh6wSyoAMRySI6QUzalepa82jSQ/qDaurz40/EIhu6+sizj0mCgjcdamKhp1Jk3Hqmv8FXFnXouQ9Vr0Qt+D1POIFbfEg9ykH1/I2CYkZBMIG+k6Pf00/UujbQdne6HUAu6CSj9wGsqQSAEPIXXvEnVmtU+6U991ZUhPuA/DMFEfVlibvNLBA7Shslp2oTy2T0wlpJN+f/Jle3gurHLIPc6EkEmckEpmSpFEyuBKz+ix4Cf4wYbcUk/Gr3kGdSi20XQGu/ZnJ7Clz4vVak9iJjN99j8lwA2zKW+CBRuHBjZdaUiDctSaADHwfz/x+09bIU9icgpzuOuKooMM5STbt+yJlJZdE3SRZHwilC4dToTQeVhAXA4tFZcDrZFzBmJsoRsJYrCdkJBPeGBub+fqomQYyKt1J0LAQ5Y0FQxLHBIp0cRZTPAuL/MNxQ/UXcxQTXjoCSdZd7B55f0UapU3EsqetEFvIMPxCPJ63YahVprODDva9Kz/Htm3piKyWzuCXfeu3siJvHuOVyx7Q4wyHrIyiJDNz5b9ABAKKauxDP32uqD7jqDzsVLH11/imKLLdl0U5PN+FP30XAQGBAFkHf+pAvOFLrdDTSjT3oQhFRzRPzLWkFg</eBayAuthToken>
            </RequesterCredentials>
            <CategorySiteID>0</CategorySiteID>
            <DetailLevel>ReturnAll</DetailLevel>
        </GetCategoriesRequest>
    """
    
    api_url = "https://api.sandbox.ebay.com/ws/api.dll"
    
    # Create Response object 'r' using the ebay API REST request
    r = requests.post(api_url, headers=headers, data=xml_data)
    
    # Parse and create XML data
    lead = "{urn:ebay:apis:eBLBaseComponents}"
    root = ET.fromstring(r.text.encode("utf-8"))
    category_array = root.find(lead + "CategoryArray")
    
    # Create SQLite database
    database = "./categories_ebay.sqlite"
    
    ## Delete existing database first
    deleteDB(database)
    
    ## Connect database (.sqlite file created automatically)
    conn = sqlite3.connect(database)
    c = conn.cursor()
    
    ## Create new SQLite table & define the db schema
    c.execute('''CREATE TABLE categories
              (CategoryID        INT PRIMARY KEY,
               CategoryName      TEXT,
               CategoryLevel     INT,
               BestOfferEnabled  INT,
               CategoryParentID  INT
              );''')
    
    ## Populate DB
    for child in category_array:
        CatID = int(child.find(lead + "CategoryID").text)
        CatName = child.find(lead + "CategoryName").text
        CatLevel = int(child.find(lead + "CategoryLevel").text)
        ### 'BestOfferEnabled' is a Boolean (not returned when 'false')
        ### Caught and made 0 when false / 1 when true to comply the db schema
        try:
            if(child.find(lead + "BestOfferEnabled").text == 'true'):
                BOEnabled = 1
        except Exception as e:
            BOEnabled = 0
            pass
        CatParentID = int(child.find(lead + "CategoryParentID").text)
        
        ### Update categories table
        rowUpdate = (CatID, CatName, CatLevel, BOEnabled, CatParentID)
        c.execute("INSERT INTO categories VALUES (?,?,?,?,?)", rowUpdate)
    
    conn.commit()
    conn.close()
    print("MESSAGE: Database built successfully.")


# function: Get Parent Category Array------------------------------------------
def getParentCat(catID):
    """
    Returns the parent category array based on a SQL query to the SQLite 
    database
    
    catID: category ID (int)
    
    parentCatArray: array with the parent category (list)
    """
    conn = sqlite3.connect('categories_ebay.sqlite')
    c = conn.cursor()
    
    # Execute parent query
    c.execute("SELECT * FROM categories WHERE CategoryID=" + str(catID))
    parentCatArray = c.fetchone() #Returns a tuple
    conn.commit()
    conn.close()
    
    return parentCatArray


# function: Get Child Category Array-------------------------------------------
def getChildCat(catID):
    """
    Returns the child category array based on a SQL query to the SQLite 
    database
    
    catID: parent category ID (int)
    
    childCatArray: array with the child category (list)
    """
    conn = sqlite3.connect('categories_ebay.sqlite')
    c = conn.cursor()
    
    # Execute child query - CategoryLevel > 1 to avoid infinite recursion
    # when CategoryID == CategoryParentID as in CatID = '888'
    c.execute("SELECT * FROM categories WHERE CategoryLevel>1 AND \
               CategoryParentID=" + str(catID))
    childCatArray = c.fetchall() #Returns a tuple
    conn.commit()
    conn.close()
    
    return childCatArray


# function: render HTML list body content--------------------------------------
def renderList(file, catArray):
    """
    Writes the HTML body content with the <ul> for the requested category ID.
    
    file: pointer to the HTML file (I/O file object)
    catArray: list of either parent or children category (list)
    """
    file.write("<ul>")
    
    if(catArray[3] == 1):
        catBOE = '[Best Offer Enabled]'
    else:
        catBOE = ''
    
    list_content = "<li>" + catArray[1] + " (" + str(catArray[0]) + ") <span class='catLevel'>[Category Level: "+ str(catArray[2]) +"]</span> <sup>" + catBOE + "</sup></li>"
    file.write(list_content)
    
    # Recursive call to render childArray
    childArray = getChildCat(catArray[0])
    if(len(childArray) > 0):
        for son in childArray:
            renderList(file, son)
            
    file.write("</ul>")


# function: render HTML content and save to file-------------------------------
def renderCategory(catID):
    """
    Renders the complete HTML file with the category tree for the requested ID
    
    catID: category ID (int)
    """
    # Check for existing category
    if getParentCat(catID) is None:
        print(("ERROR: Category {} not found.").format(catID))
        return
    else:
        html_filepath = str(catID) + ".html"
        html_file = open(html_filepath, 'w') #File object
    
    # Populate html file
    ## Header
    html_header = '''<!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <title>Polymath Challenge</title>
    <link rel="stylesheet" type="text/css" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css">
    <link rel="stylesheet" type="text/css" href="styles.css">
    </head>
    <body>
    <div class="wrapper"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/EBay_logo.png/320px-EBay_logo.png"><h3>Category Tree for: <span class="catTitle">{} ({})</span></h3></div>
    '''.format(getParentCat(catID)[1], str(catID))
    html_file.write(html_header)
    
    ## Body (list)
    renderList(html_file, getParentCat(catID))
    
    ## Closure 'footer'
    html_footer = '''
    </body>
    </html>
    '''
    html_file.write(html_footer)
    
    html_file.close()
    print("MESSAGE: The file {}.html was successfully created.".format(str(catID)))


# Execution -------------------------------------------------------------------
if(sys.argv[1]):
    # Build the database
    if(sys.argv[1] == "--rebuild"):
        try:
            buildDB()
        except Exception as e:
            print(e)
            print('ERROR: Could not build the database.')
    
    # Render the HTML file        
    elif(sys.argv[1] == "--render"):
        database = "./categories_ebay.sqlite"
        if(os.path.isfile(database)):
            if(len(sys.argv) == 3):
                try:
                    renderCategory(sys.argv[2])
                except Exception as e:
                    print(e)
                    print("ERROR: Could not render nor create {}.html HTML file.".format(str(sys.argv[2])))
            
            else:
                print("ERROR: A categoryID argument is necessary, for example: --render 888")
        else:
            print("ERROR: categories_ebay.sqlite database does not exist. Run '--rebuild' first.")
    else:
        print("ERROR: Entered argument is invalid. Please run '--rebuild' or '--render'")
else:
    print("ERROR: Argument is necessary. Try running '--rebuild' or '--render'.")