# backup-ago
 Backup ArcGIS Online content to a specified location. 


## Purpose

Download GIS and other content from ArcGIS Online Organizations to create copies for backup and historical purposes. ArcGIS Online does not support archiving and history tracking like SDE databases so this process will provide that functionality. 

## Requirements
- ArcGIS Online Organizational Account  
- ArcGIS API for Python
- Jupyter Lab (Installed via Conda) used for development, will potentially be changed to run in base Python

## Project Setup
This project uses a hidden environment file named ".env" in the root directory. This file is ignored (by .gitignore method) so you must create this file in the root directory and add variable features.


## Setup

Install [ArcGIS API for Python](https://developers.arcgis.com/python/guide/install-and-set-up/)
- For example, [using Anaconda](https://developers.arcgis.com/python/guide/install-and-set-up/).
-- Download Anaconda, create a new environment, install ArcGIS API for Python via `conda install -c esri arcgis`

Install [Jupyter Lab](https://jupyterlab.readthedocs.io/en/stable/getting_started/installation.html)
- `conda install -c conda-forge jupyterlab`

Create `.env` file
- This file will hold credentials and other environment variables in the script.
- Create a file named `.env` in the root directory using the template
- Plug in environment varaibles for credentials

Set Environment varaibles
- credentials
- save location
- search parameters to backup

## Run

