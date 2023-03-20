# Code repository for the paper "Archaeological Sites Detection with a Human-AI Collaboration Workflow"

This repository contains the code described in the paper "Archaeological Sites Detection with a Human-AI Collaboration Workflow" by
L.Casini, V.Orrù, A.Montanucci, N.Marchetti and M.Roccetti.  
The code contained here is the result of work by Casini and Montanucci.

The Python script `stampa_imm_qgis` is a script to be used inside QGIS. 
It contains functions to save the input images and target masks for the segmentation models starting from the shapefiles included in the zip folder and using a Bing basemaps.
Notice that when saving the input images all layers other than the basemap should be set to invisible.
On the other hand when saving masks site shapes should be the only visible layer and should be styled as all black filled polygons (a QGIS style is included)

The iPython notebook contains all the code needed to train and evaluate models.   

The remaining contents are support `.csv` and `.json` files that made deveopment easier.

Running those experiments should reflect the results we obtained and described in the paper.  

**IMPORTANT**
Pecomputed datasets and model checkpoints are available upon request given the size of the files.
contact the authors: luca.casini7@unibo.it
