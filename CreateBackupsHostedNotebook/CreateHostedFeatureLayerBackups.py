#!/usr/bin/env python
# coding: utf-8

# ## Welcome to your notebook.
# 

# #### Run this cell to connect to your GIS and get started:

# In[3]:


from arcgis.gis import GIS
# delete all items in backup directory.
# need to be able to round up
from math import ceil 
import numpy as np

gis = GIS("home")


# # Delete current backups
# 
# ## Query all FGDBs, find which are in GIS Layers Backups folder

# In[4]:


backups_folder = "f74cc94ec1dc4ac8b8a16742c799b4fb"


# In[5]:


allmyfgdbs = gis.content.search("owner:DublinOhio", max_items = 2000, item_type = "File Geodatabase")

len(allmyfgdbs)


# In[8]:


items_in_bkflder = []

for item in allmyfgdbs:
    
    # folder id for GIS Layers Backups. 
    # this is finding all the existing backups that are in that specified folder
    if item["ownerFolder"] == backups_folder:
        items_in_bkflder.append(item)
        
len(items_in_bkflder)


# In[9]:


items_to_move = []

for item in allmyfgdbs:
    
    # folder id for GIS Layers Backups. 
    # this is finding all the existing backups that are in that specified folder
    if item["ownerFolder"] is None and " Edit" in item["title"]:
        items_to_move.append(item)
        
len(items_to_move)


# # Delete backups in batches

# In[43]:


# Backup Delete Function

def backup_deleter(list_of_items_to_delete):
    

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

    else:
        pass
    
    print("Backup Deleter complete")


# In[44]:


backup_deleter(items_in_bkflder)


# ## Query again to see if still any left in the folder

# In[10]:


allmyfgdbs = gis.content.search("owner:DublinOhio", max_items = 2000, item_type = "File Geodatabase")
len(allmyfgdbs)


# In[11]:


items_in_bkflder = []

for item in allmyfgdbs:
    
    # folder id for GIS Layers Backups. 
    # this is finding all the existing backups that are in that specified folder
    if item["ownerFolder"] == backups_folder:
        items_in_bkflder.append(item)
        
len(items_in_bkflder)


# # Try moving content again
# 
# use set() to only move unique content

# In[54]:


print("first 10...\n", allmyfgdbs[:10])


# In[55]:


# get the properties we can call from an item
vars(allmyfgdbs[0])


# In[62]:


def findBackupGDBs_withTag(backupTag = "HFLBackupIncludeYes"):
    print("Searching for content with tag: ", backupTag)
    bkupContentList = gis.content.search(query="tags:"+ backupTag, 
                                item_type="File Geodatabase",  #File Geodatabase
                                max_items=2000)
    return bkupContentList


# In[64]:


gdbs_with_tag = findBackupGDBs_withTag()


# In[66]:


gdbs_with_tag


# In[65]:


len(gdbs_with_tag)


# In[61]:


gdbs_with_tag[0] # inspect one to see it's actually a GDB


# In[67]:


backup_deleter(gdbs_with_tag) # delete GDBs with the backup tag. 


# In[68]:


gdbs_with_tag = findBackupGDBs_withTag()


# In[69]:


gdbs_with_tag

