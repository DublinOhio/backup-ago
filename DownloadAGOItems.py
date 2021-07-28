#!/usr/bin/env python
# coding: utf-8

# # Purpose

# In[ ]:





# # Import Libraries

# In[2]:


from arcgis.gis import GIS

from dotenv import load_dotenv

import os


# ## Initialize Envs & Authenticate
# 
# This gathers varaibles from a file named `.env` in the root directory. This environment file is ignored from Git using `.gitignore` file.  
# After downloading this file from GitHub you will need to create a file named `.env` in the root directory.  
# This file holds variables that are called by the script but protects them from being published to GitHub. A template is provided that needs to be renamed and your credentials entered.
# Keep the quotation marks and update for your credentials.
# ```
# GIS_USER="YourUserName"
# GIS_PASSWORD="YourPasswordHere"
# ``` 

# In[3]:


load_dotenv()


# In[4]:


# Authenticate with GIS portal. Default is ArcGIS Online but can be your own Enterprise deployment.
gis = GIS(username = os.environ.get("GIS_USER"),
          password = os.environ.get("GIS_PASSWORD")
         )


# In[5]:


print("Logged in as " + str(gis.properties.user.username))


# # Download File Geodatabase (FGDB) Backups

# FGDBs are created from another backup process using hosted notebook. These are exports of Hosted Feature Layers sent to an Archive Folder.
# 
# The current script will download these file geodatabses
# 
# Specify Folder
# 
# Reference:
# https://support.esri.com/en/technical-article/000018909
# 
# https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Item.download 
# 
# https://gis.stackexchange.com/questions/306803/how-to-search-the-folders-items-in-arcgis-on-line-using-the-arcgis-api-for-pyth
# 
# how to get list of user's folders:
# https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html?highlight=folders#arcgis.gis.User.folders
# 
# Retrieve a list of ueres's folders. Each list item is a dictionary with properties that can be called:  
# `username` (owner of the folder), `id`, `title`, `created` 
# https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.User.items
# 
# There is a param "folder=" to get items in a folder.
# 

# In[6]:


# Name of source Folder on AGO / Portal to Download
originFolder = os.environ.get("ORIGIN_FOLDER")
print("Origin folder to retrieve data:\n\t", originFolder)


# In[7]:


# Name of destination Local Folder
destFolder = os.environ.get("DEST_FOLDER")
print("Destination local folder to save data:\n\t", destFolder)


# ### Get list of items from the origin folder
# Returns list of items in specified folder. Each is an instance of the item class with full methods available. 
# https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#item

# In[56]:


# Get list of items from the origin folder
itemsInFolder =gis.users.me.items(folder=originFolder)
itemsInFolder


# In[57]:


for item in itemsInFolder:
    item.download(save_path = destFolder)


# In[64]:


print("Items now in Destination Folder: {}\n Items:\n".format(len(os.listdir(destFolder))))
for item in os.listdir(destFolder):
    print(item)

