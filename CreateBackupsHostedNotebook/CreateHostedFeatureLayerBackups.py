#!/usr/bin/env python
# coding: utf-8

# # Backup HFLs to AGO
# 
# Create static snapshots of HFLs for archiving and backup purposes in AGO
# 
# ### References:
# 
# https://developers.arcgis.com/rest/users-groups-and-items/export-item.htm
# 
# [How To: Back up hosted content by looping through and downloading hosted feature services in FGDB format](https://support.esri.com/en/technical-article/000022524)
# 
# [How To: Back up content in ArcGIS Online](https://support.esri.com/en/technical-article/000011795)
# 
# [How To: Download feature service items from ArcGIS Online using ArcGIS API for Python](https://support.esri.com/en/technical-article/000018909)
# 
# Searching content https://developers.arcgis.com/python/guide/accessing-and-creating-content/

# ### Imports

# In[ ]:


import os
import uuid
import json
import shutil
import tempfile
from time import strftime


##import pandas as pd

from arcgis.gis import GIS
from arcgis import __version__


# #### initialize GIS

# In[ ]:


gis = GIS("home")


# # Delete current contents of backup folder.
# 
# ## First, search for all file geodatabases
# 
# ## Then, find those that are in the ownerFolder for my GIS backups, delete those.
# 

# In[ ]:


allmyfgdbs = gis.content.search("owner:DublinOhio", max_items = 2000, item_type = "File Geodatabase")

backupfgdbs = []

for item in allmyfgdbs:
    
    # folder id for GIS Layers Backups 
    if item.ownerFolder == "f74cc94ec1dc4ac8b8a16742c799b4fb":
        backupfgdbs.append(item)


# In[ ]:


#API doc ref: https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html?highlight=delete#arcgis.gis.ContentManager.delete_items 
gis.content.delete_items(items = backupfgdbs)


# Properties of an item, found ownerFolder from here
# 
# ```#from pprint import pprint
# #pprint(vars(mycontent[2]))```
# 
# ```{'_depend': <Dependencies for ff35d0b42fd841188c5b564909686eb0>,
#  '_gis': GIS @ https://www.arcgis.com version:9.3,
#  '_hydrated': False,
#  '_portal': <arcgis.gis._impl._portalpy.Portal object at 0x7fbe182e8cd0>,
#  '_workdir': '/tmp',
#  'access': 'private',
#  'accessInformation': 'City of Dublin, Ohio, USA',
#  'advancedSettings': None,
#  'appCategories': [],
#  'avgRating': 0,
#  'banner': None,
#  'categories': [],
#  'created': 1633824388000,
#  'culture': 'en-us',
#  'description': 'Trees planted and maintained by the City in the right-of-way '
#                 'of Dublin OH, USA. These trees are typically found between '
#                 'the sidewalk and the street in the &quot;tree lawn&quot;.',
#  'documentation': None,
#  'extent': [[-83.20229096510711, 40.065185068482265],
#             [-83.08937282431096, 40.16284924299875]],
#  'groupDesignations': None,
#  'guid': None,
#  'id': 'ff35d0b42fd841188c5b564909686eb0',
#  'industries': [],
#  'isOrgItem': True,
#  'itemid': 'ff35d0b42fd841188c5b564909686eb0',
#  'languages': [],
#  'largeThumbnail': None,
#  'licenseInfo': None,
#  'listed': False,
#  'modified': 1633824455000,
#  'name': 'Street_Trees_Edit_AsOf_20211010T000014.zip',
#  'numComments': 0,
#  'numRatings': 0,
#  'numViews': 0,
#  'owner': 'DublinOhio',
#  'ownerFolder': 'f74cc94ec1dc4ac8b8a16742c799b4fb',
#  'properties': None,
#  'protected': False,
#  'proxyFilter': None,
#  'scoreCompleteness': 61,
#  'screenshots': [],
#  'snippet': 'Trees planted and maintained in the right-of-way of Dublin OH, '
#             'USA',
#  'spatialReference': '102723',
#  'subInfo': 0,
#  'tags': ['Arboriculture', 'Trees', 'Urban Forestry'],
#  'thumbnail': None,
#  'title': 'Street_Trees_Edit_AsOf_20211010T000014',
#  'type': 'File Geodatabase',
#  'typeKeywords': ['File Geodatabase'],
#  'url': None}```

# # Create list of content to backup
# ## Important! Filter input
# ####  `"tags:HFLBackupIncludeYes"` A specific tag for filter 
# #### `item_type="Feature Layer"` , Only get Feature Layer types
# 
# otherwise the created GDBs may be included and backup content that does not need to be.

# In[ ]:


def makeBkupList(backupTag = "HFLBackupIncludeYes"):
    print("Searching for content with tag: ", backupTag)
    bkupContentList = gis.content.search(query="tags:"+ backupTag, 
                                item_type="Feature *",  #Feature Service, Feature Layer, Feature Collection
                                max_items=2000)
    print("Query Results to Backup:\n", bkupContentList)
    return bkupContentList


# # Function to Create the Backups

# In[ ]:


#https://support.esri.com/en/technical-article/000022524

def backupItems(bkupList, bkupFolder = "GIS Layers Backups"):
    ######
    # INPUT: List of items to backup, and output destination
    # OUTPUT: returns list of output item IDs and messaging for processes
    
    ######
    timestamp = strftime("%Y%m%dT%H%M%S")
    # for naming timestamp in ISO 8601 compliant 

    print("Timestamp is {}\nExporting {} items to destination {}\n\n".format(timestamp, len(bkupList), bkupFolder))
    
    outputItemIDs = []
    outputItmeNames = []
    
    for idx, item in enumerate(bkupList):
        
        try:
    
            dataitem = gis.content.get(item.id)
            print("Processing item: ", item, "ID: ", dataitem)

            
            try:
                print("\tExporting item")
                result = dataitem.export(item.title, "File Geodatabase", parameters = None)
                print("\tExporting item complete")
            except:
                print("Failed Exporting Item")

            try:
                
                print("\tMoving item to", bkupFolder)
                result.move(bkupFolder, owner = "DublinOhio")
                print("\tMoving item complete")
            except:
                print("Failed to move item")
                

            print("\tItem {} of total {} complete".format((idx + 1), len(bkupList)))

            print("\tID of backup", result.id)
            print("\n******\n")
            outputItemIDs.append(result.id)
        
        except:
            print("Failed somewhere")
    
    print("Export to GDBs complete. List of output item IDs available\nID List: ", outputItemIDs)
    
    for item in outputItemIDs:
        i = gis.content.get(item)
        print("\t", i.title, " ID --->\t", i.id)
    return outputItemIDs
    


# # Function to Clean up content 
# 
# ## Find the new content we just created
# 
# The backup function returns a list of backup item IDs if defined 
# i.e. `backups = backupItems(bkupList,  bkupFolder = "GIS Layers Backups")`

# ### Remove tag used to flag for backups
# 
# Function to remove clutter tags such as the Backup Notice tag so it will not appear in future searches for this.
# 
# i.e. `removeBkupTag(['Test', 'IncludeInBackups', 'HFLBackupIncludeYes'])` returns 
# ```
# Original Tags
# 	 ['Test', 'IncludeInBackups', 'HFLBackupIncludeYes'] 
# 	New Tags
# 	 ['Test', 'IncludeInBackups']
# ```

# In[ ]:


def removeBkupTag(TagList, removeTags = ["HFLBackupIncludeYes"]):
    # Defined a default tag HFLBackupIncludeYes but this can be any list of tags.

    
    tagsClean = [n for n in TagList if n not in removeTags]
    
    print("Original Tags\n\t", TagList, "\n\tNew Tags\n\t", tagsClean)
    
    return tagsClean


# In[ ]:


def updateTags(itemID):
    # Takes in item ID then updates and removes backup tags
    
    item = gis.content.get(itemID)
    print("Updating tags on item:", item)
    
    # Call the remove backup tag function 
    newTags = removeBkupTag(item.tags)
    
    # Update the tags with the clean list. 
    item.update(item_properties={'tags':newTags})
    
    print("\tConfirmed: tags after update:\n\t", item.tags)


# In[ ]:


def removeBackupTagsFromBackups(backupResults):
    for item in backupResults:
        updateTags(item)


# # Run the Backups

# In[ ]:


bkupList = makeBkupList(backupTag = "HFLBackupIncludeYes")


bkupList


# In[ ]:


backups = backupItems(bkupList,  bkupFolder = "GIS Layers Backups")


# In[ ]:


def removeBkupTagList(backupTag = "HFLBackupIncludeYes"):
    print("Searching for content with tag: ", backupTag)
    bkupContentList = gis.content.search(query="tags:"+ backupTag, 
                                item_type="File Geodatabase",  
                                max_items=2000)
    print("Query Results to Backup:\n", bkupContentList)
    
    backupitemIDs = []
    
    for i in bkupContentList:
        backupitemIDs.append(i.id)
        
    # get item ids
    return backupitemIDs


# In[ ]:


removelist = removeBkupTagList(backupTag = "HFLBackupIncludeYes")


# In[ ]:


removeBackupTagsFromBackups(removelist)

