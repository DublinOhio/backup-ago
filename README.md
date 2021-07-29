# backup-ago
 Backup ArcGIS Online content to a specified location. 


## Purpose

Download GIS and other content from ArcGIS Online Organizations to create copies for backup and historical purposes. ArcGIS Online does not support archiving and history tracking like SDE databases so this process will provide that functionality. 

## Requirements
- ArcGIS Online Organizational Account  
- ArcGIS API for Python
- JupyterLab (Installed via Conda) 
-- Used for development, will potentially be changed to run in base Python
-- JupyterLab has a lot of requirements and makes this script heavier than it needs to be

## Project Setup
This project uses a hidden environment file named ".env" in the root directory. This file is ignored (by .gitignore method) so you must create this file in the root directory and add variable features.

## Setup
Clone (download) this project.  

Create a Python environment for the project (**strongly recommended**).
- You can install the libraries into your base Python environment; however, it is probably better to create a separate environment for projects
- Example using [Conda](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) shown below.
- You will use this specified environment in your task scheduler.
- Launch conda command prompt then `conda create --name envname` which creatse a new env by default in `C:\Users\username\Anaconda3\envs`

Activate the new environment
- `conda activate envname` [docs](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#activating-an-environment)  

Install [ArcGIS API for Python](https://developers.arcgis.com/python/guide/install-and-set-up/)
- For example, [using Anaconda](https://developers.arcgis.com/python/guide/install-and-set-up/).  
-- `conda install -c esri arcgis`  
-- Can alternatively use Miniconda.

Install [dotenv](https://anaconda.org/conda-forge/python-dotenv) library in conda
- `conda install -c conda-forge python-dotenv`

Install [JupyterLab](https://jupyterlab.readthedocs.io/en/stable/getting_started/installation.html)  
- `conda install -c conda-forge jupyterlab`  
- (Optional, included with Anaconda full install)

Create `.env` file
- This file will hold credentials and other environment variables in the script.
- Create a file named `.env` in the root directory using the template. You can rename the template to `.env`.  
- Plug in environment varaibles for credentials

Set Environment varaibles
- credentials
- save location
- search parameters to backup


## Run
Can be run as a Python file i.e. scheduled with Windows Task Scheduler or interactively in a Jupyter Lab notebooks.

Development was done in Jupyter Lab then exported to Python.
- Run Jupyter Lab, open notebook, run all cells.  
-- `conda activate env-name` then `cd path-to-project` then `jupyter lab`  
-- run the notebook. 
**OR **
- Run Python .py version of the file on demand or via Task Scheduler
- **Be sure to use the Python environment with the installed ArcGIS and dotenv libraries** (i.e. using the Ana/Miniconda distribution here).
