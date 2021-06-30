# backup-ago
 Backup ArcGIS Online content to a specified location. 


## Purpose

Download GIS and other content from ArcGIS Online Organizations to create copies for backup and historical purposes. ArcGIS Online does not support archiving and history tracking like SDE databases so this process will provide that functionality. 

## Requirements
- ArcGIS Online Organizational Account  
- ArcGIS API for Python

## Project Setup
This project uses a hidden environment file named ".env" in the root directory. This file is ignored (by .gitignore method) so you must create this file in the root directory and add variable features.


## Setup

Install [ArcGIS API for Python](https://developers.arcgis.com/python/guide/install-and-set-up/)
- For example, [using Anaconda](https://developers.arcgis.com/python/guide/install-and-set-up/).
-- Download Anaconda, create a new environment, install ArcGIS API for Python `conda install -c esri arcgis`
