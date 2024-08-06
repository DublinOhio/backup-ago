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

# In[1]:


import os
import uuid
import json
import shutil
import tempfile
from time import strftime
import time
# need to be able to round up
from math import ceil 

import numpy as np

from tabulate import tabulate

import pandas as pd

from arcgis.gis import GIS
from arcgis import __version__


# # Your custom variables

# In[2]:


# id for the folder where backups are stored.
backups_folder = "f74cc94ec1dc4ac8b8a16742c799b4fb"
backup_tag = "HFLBackupIncludeYes"

# group ID used to email results
GIS_staff_group_id = "81d7f67d885c4e629b4c5d49309b9e25"


# #### initialize GIS

# In[3]:


gis = GIS("home")


# # Setup email notifications (by group membership)
# 
# 

# ## Send notification
# 

# In[4]:


timestamp = strftime("%m-%d-%Y%  %H%:M")

def email_GIS_staff(GISStaffGroupID, subject_, message_):

    # define group
    GIS_staff_group = gis.groups.search(GISStaffGroupID)[0]
    
    # get members 
    users_ = GIS_staff_group.get_members()["users"]
    print("Notifying users:\n\t", users_)
    
    # send email
    did_it_work = GIS_staff_group.notify(users_, subject = subject_, message = message_)
    
    # call the function
    # email_GIS_staff(GIS_Staff_Group_ID, 
    #                subject_= email_subject, 
    #                message_ = "Time started: "+ timestamp + email_message)    
    
    print("\n\tEmail sent?:", did_it_work)


# ### References
# https://community.esri.com/t5/arcgis-notebooks-documents/send-e-mail-notifications-with-arcgis-notebooks/ta-p/1329699

# # Search for all file geodatabases
# 
# We'll refine this list to delete previous backups in the backup folder next.

# In[6]:


allmyfgdbs = gis.content.search("owner:DublinOhio", max_items = 2000, item_type = "File Geodatabase")

len(allmyfgdbs)


# In[7]:


allmyfgdbs[:10] # first 10 


# # Funcitons to Find, then Delete Previous Backups in Batches
# 
# Search all filegeodatabases, find those that are already in the backup folder

# In[ ]:


def get_items_in_bkflder():
    
    ######
    # INPUT: list of all file geodatabses
    # OUTPUT: list of file geodatabaes in the backup folders or ones with backuptag. 
    # A FGDB with the backuptag still probably failed to move from the home folder
    # 
    
    ######
    itemlist = gis.content.search("owner:DublinOhio", max_items = 2000, item_type = "File Geodatabase")
    
    items_in_backupkfolder = []

    for item in itemlist:

        # folder id for GIS Layers Backups. 
        # this is finding all the existing backups that are in that specified folder
        if item["ownerFolder"] == backups_folder:
            items_in_backupkfolder.append(item)
            
    print("Length of items in backup folder: ", len(items_in_backupkfolder))
    
    return items_in_backupkfolder


# In[9]:


items_in_bkflder = get_items_in_bkflder()


# Then, delete them, in batches of 100

# In[10]:


def backupDeleter(list_of_items_to_delete, list_all_fgdbs = allmyfgdbs):
        
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
            
        ## Check if succesfully deleted all. 
        
        new_list_of_items_to_delete = get_items_in_bkflder()
        
        if len(new_list_of_items_to_delete) > 0:
            print("\tResult:\t!!!Hey there's still backups in the backup folder that weren't deleted!!!")

        elif len(new_list_of_items_to_delete) == 0:
            print("\tResult:\tPrevious backup deletion completed, len(items_in_bkflder) == 0")

    elif n_backups == 0:

        print("No backups to delete")
    


# In[11]:


backupDeleter(items_in_bkflder)


# # Function to Create List of Content to Backup
# ## Important! Filter input
# ####  `"tags:HFLBackupIncludeYes"` A specific tag for filter 
# #### `item_type="Feature Layer"` , Only get Feature Layer types
# 
# otherwise the created GDBs may be included and backup content that does not need to be.

# In[12]:


def makeBkupList(backupTag = backup_tag):
    
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


# In[13]:


# make a list of items to backup by the tag specified.

items_to_backup = makeBkupList(backupTag = backup_tag)

items_to_backup


# In[14]:


if len(items_to_backup) == len(set(items_to_backup)):
    print("All items to backup are unique")
else:
    print("CAUTION: There are some duplicate item names in the back-up list")


# # Function to Create the Backups

# In[15]:


# Source framework, expanded upon.
# "Back up hosted content by looping through and downloading hosted feature services in FGDB format"
# https://support.esri.com/en/technical-article/000022524

def backupItems(bkupList = items_to_backup, bkupFolder = backups_folder): # backups_folder defined at top of script
    
    ######
    # INPUT: List of items to backup, and output destination
    # PROCESS: 
    # - Creats backup file geodatabses (in the home folder)
    # - moves them to backup folder
    # OUTPUT: 
    # - returns list of output item IDs and messaging for processes
    # - returns list of items that failed export or move
    
    ######
    outputItemIDs = []
    outputItemTitles = []
    
    item_export_result = [] # hold result of trying to export
    items_move_result = [] # hold result of trying to move

    
    timestamp = strftime("%Y%m%dT%H%M%S")
    t = time.process_time()
    
    # for naming timestamp in ISO 8601 compliant 
    print("Timestamp is {}\nExporting {} items to destination {}\n\n".format(timestamp, len(bkupList), bkupFolder))
    
    
    # for index, item, in the backup list.
    for idx, item in enumerate(bkupList):
        
        # purge result variable name, otherwise if one fails it will report back the previous iteration's ID #
        if 'result' in locals():
            
            del result 
        
        try:
    
            dataitem = gis.content.get(item.id)
            print("Processing item: ", item, "ID: ", dataitem)
            
            outputItemTitles.append(item.title)
            outputItemIDs.append(item.id)

            try:
                print("\tExporting item")
                result = dataitem.export(item.title, "File Geodatabase", parameters = None)
                print("\tExporting item complete")
                
                item_export_result.append("Success")
                
            except Exception as error:
                print("Failed Exporting Item", error)
                item_export_result.append(error) # add item to failed list
                
# may need to move this to a separate function. 
            try:
                print("\tMoving item to", bkupFolder)
                result.move(bkupFolder)
                print("\tMoving item complete")
                items_move_result.append("Success")
                
            except Exception as error:
                print("Failed to move item ", error)
                items_move_result.append(error) # add item to failed list


            print("\tItem {} of total {} complete".format((idx + 1), len(bkupList)))

            print("\tID of backup", result.id)
            print("\n******\n")
            
 
        except Exception as error:
            print("Failed somewhere. ", error)
    
    print("Export to GDBs complete. List of output item IDs available\nID List: ", outputItemIDs)
    
    timestamp = strftime("%Y%m%dT%H%M%S")
    
    print("Elapsed Minutes: ", ((time.process_time() - t)/60.0))

    for item in outputItemIDs:
        i = gis.content.get(item)
        print("\t", i.title, " ID --->\t", i.id)
        
    return outputItemTitles, outputItemIDs, item_export_result, items_move_result
    


# # Run the Backups

# In[ ]:


# testing with first 10 items, :10
backups = backupItems(items_to_backup, backups_folder)


# In[ ]:


backups


# In[ ]:


np.transpose(backups)


# In[ ]:


results_df = pd.DataFrame(np.transpose(backups), columns = ["title", "id", "export", "moved"])
results_df


# add links
results_df = results_df.assign(Link = lambda x: ("https://dublinohio.maps.arcgis.com/home/item.html?id="+x['id'] ))


results_df



# In[ ]:


n_rows = results_df.shape[0]

n_success = sum(results_df["export"]== "Success")

n_failed = n_rows - n_success

per_succes = (n_success *1.0 / n_rows)*100


# In[ ]:


per_succes


# ### Format as HTML table for email 
# 
# get some stats first

# In[ ]:


[n_rows,n_success, n_failed, per_succes]


# In[ ]:


summ_df = pd.DataFrame([[n_rows,n_success, n_failed, per_succes]], columns = ["Items", "Success", "Failed", "Percent Success"])
summ_df


# In[108]:


message_ = ("Total Items: {}|\n  \tSuccesses:\t {}| \n\tFailed:\t\t {}| \n\tPercent Success:\t {}|\n").format(n_rows, n_success, n_failed, per_succes)

print(message_)


# In[ ]:


message_ = summ_df.to_html()


# In[ ]:


message_ += results_df.to_html(
    render_links=True,
    escape=True,
)
#message_


# In[ ]:


message_


# In[ ]:


strftime("%m-%d-%Y  %H:%M")


# In[ ]:


# Send email

email_subject = "Backup Results"

email_message = message_

timestamp = strftime("%m-%d-%Y  %H:%M")

# call the function
email_GIS_staff(GIS_staff_group_id, 
                subject_= email_subject + " " + strftime("%m-%d-%Y  %H:%M"), 
                message_ = email_message)


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





# In[ ]:


def removeBkupTag(TagList, removeTags = [backup_tag]):
    # Defined a default tag i.e. HFLBackupIncludeYes but this can be any list of tags.
    
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
    
    # Add a new tag, "BackedupFGDB"
    newTags.append("ExistingBackupFGDB")
    
    # Update the tags with the clean list. 
    item.update(item_properties={'tags':newTags})
    
    print("\tConfirmed: tags after update:\n\t", item.tags)


# In[ ]:


def removeBackupTagsFromBackups(backupResults):
    for item in backupResults:
        updateTags(item)


# In[ ]:


# maybe do this inside the backup process rather than after?  remove the tag right then and there?

def removeBkupTagList(backupTag = backup_tag):
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


removelist = removeBkupTagList(backupTag = backup_tag)


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
