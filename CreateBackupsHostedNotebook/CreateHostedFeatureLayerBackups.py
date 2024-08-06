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

# In[89]:


import os
import uuid
import json
import shutil
import tempfile
from time import strftime
import time
# need to be able to round up
from math import ceil 

##import pandas as pd

from arcgis.gis import GIS
from arcgis import __version__


# # Your custom variables

# In[65]:


# id for the folder where backups are stored.
backups_folder = "f74cc94ec1dc4ac8b8a16742c799b4fb"


# #### initialize GIS

# In[2]:


gis = GIS("home")


# # Search for all file geodatabases
# 
# We'll refine this list to delete previous backups in the backup folder next.

# In[66]:


allmyfgdbs = gis.content.search("owner:DublinOhio", max_items = 2000, item_type = "File Geodatabase")

len(allmyfgdbs)


# In[67]:


allmyfgdbs[:10] # first 10 


# # Funcitons to Find, then Delete Previous Backups in Batches
# 
# Search all filegeodatabases, find those that are already in the backup folder

# In[85]:


def get_items_in_bkflder(itemlist = allmyfgdbs):
    
    ######
    # INPUT: list of all file geodatabses
    # OUTPUT: list of file geodatabaes in the backup folders
    
    ######
    
    items_in_bkflder = []

    for item in itemlist:

        # folder id for GIS Layers Backups. 
        # this is finding all the existing backups that are in that specified folder
        if item["ownerFolder"] == backups_folder:
            items_in_bkflder.append(item)
            
    print("Length of items in backup folder: ", len(items_in_bkflder))
    
    return items_in_bkflder


# In[86]:


get_items_in_bkflder()


# Then, delete them, in batches of 100

# In[87]:


def backupDeleter(list_of_items_to_delete):
        
    ######
    # INPUT: list of items to delete
    # OUTPUT: None; deletes items. Prints results.
    
    ######
    
    print("Starting backupDeleter...")
    n_backups = len(list_of_items_to_delete)
    
    # when backups are already gone we don't need to delete them.
    if n_backups > 0:

        #get number of batches needed, each batch can be max 100 
        n_batches = ceil(n_backups/100.00)
        print("Chop the list of backups to delete into {} batches".format(n_batches))

        # https://numpy.org/doc/stable/reference/generated/numpy.array_split.html#numpy.array_split
        # split batch list into about equal numbers per batch
        batch_list = np.array_split(list_of_items_to_delete, n_batches)

        for i in batch_list:
            print("Batch length: ",len(i))

        for i, batch in enumerate(batch_list):
            print("starting batch ", i+1)
            
            try:
                gis.content.delete_items(items = batch)
            except Exception as error:
                # handle the exception
                print("An exception occurred:", error) 
                
            print("\tBatch complete")
        
        if len(list_of_items_to_delete) > 0:
            print("\tResult:\t!!!Hey there's still backups in the backup folder that weren't deleted!!!")

        elif len(list_of_items_to_delete) == 0:
            print("\tResult:\tPrevious backup deletion completed, len(items_in_bkflder) == 0")

    elif n_backups == 0:

        print("No backups to delete")
    


# In[88]:


backupDeleter(items_in_bkflder)


# # Function to Create List of Content to Backup
# ## Important! Filter input
# ####  `"tags:HFLBackupIncludeYes"` A specific tag for filter 
# #### `item_type="Feature Layer"` , Only get Feature Layer types
# 
# otherwise the created GDBs may be included and backup content that does not need to be.

# In[81]:


def makeBkupList(backupTag = "HFLBackupIncludeYes"):
    
    ######
    # INPUT: tag that identifies feature layers for backups
    # OUTPUT: list of Feature layers that have the corresponding tag
    
    ######
    
    
    print("Searching for content with tag: ", backupTag)
    bkupContentList = gis.content.search(query="tags:"+ backupTag, 
                                item_type="Feature *",  #Feature Service, Feature Layer, Feature Collection
                                max_items=2000)
    print("Query Results to Backup:\n", bkupContentList)
    return bkupContentList


# In[99]:


# make a list of items to backup by the tag specified.

items_to_backup = makeBkupList(backupTag = "HFLBackupIncludeYes")

items_to_backup


# In[100]:


len(items_to_backup)


# In[101]:


len(set(items_to_backup))


# # Function to Create the Backups

# In[109]:


# Source framework, expanded upon.
# "Back up hosted content by looping through and downloading hosted feature services in FGDB format"
# https://support.esri.com/en/technical-article/000022524

def backupItems(bkupList = items_to_backup, bkupFolder = backups_folder): # backups_folder defined at top of script
    
    ######
    # INPUT: List of items to backup, and output destination
    # PROCESS: 
    # - Creats backup file geodatabses (in the home folder)
    # - moves them to backup folder
    # OUTPUT: returns list of output item IDs and messaging for processes
    
    ######
    
    timestamp = strftime("%Y%m%dT%H%M%S")
    t = time.process_time()
    
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
            except Exception as error:
                print("Failed Exporting Item", error)
                
# may need to move this to a separate function. 
            try:
                print("\tMoving item to", bkupFolder)
                result.move(bkupFolder)
                print("\tMoving item complete")
            except Exception as error:
                print("Failed to move item ", error)

            print("\tItem {} of total {} complete".format((idx + 1), len(bkupList)))

            print("\tID of backup", result.id)
            print("\n******\n")
            outputItemIDs.append(result.id)
        
        except Exception as error:
            print("Failed somewhere. ", error)
    
    print("Export to GDBs complete. List of output item IDs available\nID List: ", outputItemIDs)
    
    timestamp = strftime("%Y%m%dT%H%M%S")
    
    print("Elapsed Minutes: ", ((time.process_time() - t)/60.0))

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

# In[103]:


def removeBkupTag(TagList, removeTags = ["HFLBackupIncludeYes"]):
    # Defined a default tag HFLBackupIncludeYes but this can be any list of tags.

    
    tagsClean = [n for n in TagList if n not in removeTags]
    
    print("Original Tags\n\t", TagList, "\n\tNew Tags\n\t", tagsClean)
    
    return tagsClean


# In[104]:


def updateTags(itemID):
    # Takes in item ID then updates and removes backup tags
    
    item = gis.content.get(itemID)
    print("Updating tags on item:", item)
    
    # Call the remove backup tag function 
    newTags = removeBkupTag(item.tags)
    
    # Add a new tag, "BackedupFGDB"
    newTags.append("ExistingBackupFGDB")
    
    # Update the tags with the clean list. 
    item.update(item_properties={'tags':newTags})
    
    print("\tConfirmed: tags after update:\n\t", item.tags)


# In[105]:


def removeBackupTagsFromBackups(backupResults):
    for item in backupResults:
        updateTags(item)


# # Run the Backups

# In[107]:


# make a list of items to backup by the tag specified.

items_to_backup = makeBkupList(backupTag = "HFLBackupIncludeYes")

items_to_backup


# In[ ]:


backups = backupItems(items_to_backup, backups_folder)


# In[ ]:


# maybe do this inside the backup process rather than after?  remove the tag right then and there?

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


# # General Reference
# 
# ###  Properties of an item, found ownerFolder from here
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

# In[ ]:




