# PolymathChallenge
Repo containing the self-contained program for the Polymath ebay categories challenge.

The script uses the ```GetCategories``` API from eBay.com to download the entire eBay category data and store it in a custom SQLite database.

- To build the database, run the python script from the command-line with the ```--rebuild``` argument:

```
python categories.py --rebuild
*> MESSAGE: Database built successfully*
```

- To render the HTML file from a category ID, use the ```--render <categoryID>``` argument:

```
python categories.py --render 3153
*> MESSAGE: The file 3153.html was successfully created.*
```

*NOTE: Please make sure ```styles.css``` is located in the same folder as the HTML file to preserve the CSS styling.*

Example ([Demo](https://cccruzr.github.io/data/polymath/3153.html)):

![Imgur](https://i.imgur.com/8yrfAZF.jpg)