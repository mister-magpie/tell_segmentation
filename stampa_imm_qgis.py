import pickle
from qgis.PyQt import QtGui
import os 
import random
import numpy as np
import json




def centroid2vec(cx,cy):
    name = "test_tile"
    tile_meters = 1000

    left = cx - (tile_meters/2)
    top = cy + (tile_meters/2)
    right = cx + (tile_meters/2)
    bottom = cy - (tile_meters/2)


    layer =  QgsVectorLayer('Polygon?crs=EPSG:3857', name , "memory")
    pr = layer.dataProvider() 
    poly = QgsFeature()

    points = [
        QgsPointXY(left,top),
        QgsPointXY(right,top),
        QgsPointXY(right,bottom),
        QgsPointXY(left,bottom),
        ]
    poly.setGeometry(QgsGeometry.fromPolygonXY([points]))
    pr.addFeatures([poly])
    layer.updateExtents()
    QgsProject.instance().addMapLayers([layer])


#Serve per salvare un'immagine per ogni sito, dove il sito sta al centro dell'immagine. 
def save_tile(cx,cy,
            tile_meters=500,shiftx=0,shifty=0,
            outputSize=512,
            fn = "", uzbekistan=False,fn1=""):

    rasters = ["bing"]

    project = QgsProject.instance()
    manager = project.layoutManager()
    layoutName = "ctx_saver"
    layouts_list = manager.printLayouts()

    for layout in layouts_list:
        if layout.name() == layoutName:
            manager.removeLayout(layout)

    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    layout.setName(layoutName)
    manager.addLayout(layout)

    layers = []
    for r in rasters:
        layers = layers + project.mapLayersByName(r)

    assert(os.path.exists(fn)==False)

    left = cx - (tile_meters/2)
    top = cy + (tile_meters/2)
    right = cx + (tile_meters/2)
    bottom = cy - (tile_meters/2)
    extent = QgsRectangle(left,top,right,bottom)
    if(uzbekistan==True):
        df_sites = pd.read_csv("testsetUzbeko_v2.csv")
        df_sites.loc[df_sites['ShortCode'] == fn1, ['extent']] = extent
        df_sites.to_csv("testsetUzbeko_v2.csv", index=False)

    map = QgsLayoutItemMap(layout)
    map.setRect(0,0,outputSize,outputSize)
    ms = QgsMapSettings()
    ms.setLayers(layers)
    ms.setExtent(extent)
    map.setExtent(extent)
    ms.setOutputSize(QSize(outputSize,outputSize))
    layout.addLayoutItem(map)
    map.attemptMove(QgsLayoutPoint(0,0,QgsUnitTypes.LayoutPixels))
    map.attemptResize(QgsLayoutSize(outputSize,outputSize,QgsUnitTypes.LayoutPixels))
    layout.pageCollection().page(0).setPageSize(map.sizeWithUnits())

    exporter = QgsLayoutExporter(layout)
    
    exporter.exportToImage(fn, QgsLayoutExporter.ImageExportSettings())
    layout.removeLayoutItem(map)
    return True
    
    


import pandas as pd


    
    

def save_dataset_1000(masks,TEST=None,NEGS=None,TRAIN=None):
    df_sites = pd.read_csv(r"./trainset1000.csv")
    df_negs = pd.read_csv(r"./negs1000.csv")
    df_maysan = pd.read_csv(r"./maysan1000.csv")
    print(df_maysan.shape)
    # masks
    if masks:
        if TEST:
            for i,s in df_maysan.iterrows():
                save_tile(s.cx,s.cy,tile_meters=1000,outputSize=1024,
                    fn="/datasets/bing_1k/maysan/masks/"+str(s.entry_id)+".png"
                )
                if i%100==0: print("img:",i)
            print("Mask test done")
        if TRAIN:    
            for i,s in df_sites.iterrows():
                save_tile(s.cx,s.cy,tile_meters=1000,outputSize=1024,
                    fn="/datasets/bing_1k/train/masks/"+str(s.entry_id)+".png"
                )
                if i%100==0: print("img:",i)
            print("Mask train done")
        if NEGS:
            for i,s in df_negs.iterrows():
                save_tile(s.cx,s.cy,tile_meters=1000,outputSize=1024,
                    fn="/datasets/bing_1k/train/masks/"+str(s.id)+".png"
                )
                if i%100==0: print("img:",i)
            print("Mask negs done")
    # sites
    else:
        if TRAIN:
            for i,s in df_sites.iterrows():
                save_tile(s.cx,s.cy,tile_meters=1000,outputSize=1024,
                    fn="/datasets/bing_1k/train/sites/"+str(s.entry_id)+".jpg"
                )
                if i%100==0: print("img:",i)
            print("sites train done")
        if NEGS:
            for i,s in df_negs.iterrows():
                save_tile(s.cx,s.cy,tile_meters=1000,outputSize=1024,
                    fn="/datasets/bing_1k/train/sites/"+str(s.id)+".jpg"
                )
                if i%100==0: print("img:",i)
            print("sites negs done")
        if TEST:
            for i,s in df_maysan.iterrows():
                save_tile(s.cx,s.cy,tile_meters=1000,outputSize=1024,
                    fn="/datasets/bing_1k/maysan/sites/"+str(s.entry_id)+".jpg"
                )
                if i%100==0: print("img:",i)
            print("sites test done") 

#serve per salvarmi le coordinate di ogni centroide di ogni tile dell'area di selezione
def save_coor(cx,cy,idx):
    dictionary = {
    "name": "tile"+str(idx) ,
    "cx": cx,
    "cy": cy}
    with open("coor_maysan.json") as fp:
        listObj = json.load(fp)
    
    listObj.append(dictionary)
    with open("coor_maysan.json", "w") as json_file:
        json.dump(listObj, json_file,
                indent=4,
                separators=(',', ': '))


#dato un polygon, ritorna la lista dei vertici
def extract_vertex_from_polygon(fn='sel_area.shp'):
    layer=QgsVectorLayer(fn)
    iter = layer.getFeatures()
    for feature in iter:
        geom = feature.geometry()
        vertices = feature.geometry().asMultiPolygon()
        points = []
        for v in vertices:
            points.append(v)
        points=points[0][0]
        return(points)

def tile_maysan(masks,fn='sel_area_512.shp'):
    points=extract_vertex_from_polygon(fn)[:-1]
    #print(points[1][0])
    points_order=np.sort(np.array(points).ravel())
    #print(points_order)
    coordinateX=points_order[4:]
    coordinateY=points_order[:-4]
    #print(coordinateY)
    est=max(coordinateX)
    nord=max(coordinateY)
    ovest=min(coordinateX)
    sud=min(coordinateY)
    
    tile_spost=500
    cx=ovest+tile_spost
    cy=sud+tile_spost
    print((est-cx)/(tile_spost*2))
    iterorr=round((est-cx)/(tile_spost*2)+0.01)
    itervert=round((nord-cy)/(tile_spost*2)+0.01)
    print(iterorr)
    itertot=iterorr*itervert
    print("Si creeranno: ",itertot," immagini")
    scorr_vert=False
  
    for i in range(1,itertot+1):
        
        if(scorr_vert==False):
            cx=cx+tile_spost*2
            if(i==1): cx=ovest+tile_spost
            if(masks==True):
                save_tile(cx,cy,tile_meters=1000,outputSize=1024,
                fn="/datasets/maysan_sel_tile/masks/"+str(i)+".png")
            else:
                save_tile(cx,cy,tile_meters=1000,outputSize=1024,
                fn="/datasets/maysan_sel_tile/sites/"+str(i)+".jpg")
                #save_coor(cx,cy,i)
            if(i%iterorr)==0: scorr_vert=True
        else:
            cy=cy+tile_spost*2
            cx=ovest+tile_spost
            if(masks==True):
                save_tile(cx,cy,tile_meters=1000,outputSize=1024,
                fn="/datasets/maysan_sel_tile/masks/"+str(i)+".png")
            else:
                save_tile(cx,cy,tile_meters=1000,outputSize=1024,
                fn="/datasets/maysan_sel_tile/sites/"+str(i)+".jpg")
                #save_coor(cx,cy,i)
            scorr_vert=False
    print("Fatto!")

#salva il dataset dimensione 2048x2048 pixel, se filter=True il dataset è filtrato
def save_dataset_2000(filter,masks,TEST=None,NEGS=None,TRAIN=None):
    df_sites = pd.read_csv(r"./dataset1000withFilter.csv")
    df_negs = pd.read_csv(r"./negs1000.csv")
    df_maysan = pd.read_csv(r"./maysan1000.csv")
    if (filter==True): df_sites=df_sites[df_sites["filter"]==True]
    print(df_sites.shape)
    # masks
    if masks:
        if TEST:
            for i,s in df_maysan.iterrows():
                save_tile(s.cx,s.cy,tile_meters=2000,outputSize=2048,
                    fn="/datasets/bing_2k/maysan/masks/"+str(s.entry_id)+".png"
                )
                if i%100==0: print("img:",i)
            print("Mask test done")
        if TRAIN:    
            for i,s in df_sites.iterrows():
                save_tile(s.cx,s.cy,tile_meters=2000,outputSize=2048,
                    fn="/datasets/bing_2k/train/masks/"+str(s.entry_id)+".png"
                )
                if i%100==0: print("img:",i)
            print("Mask train done")
        if NEGS:
            for i,s in df_negs.iterrows():
                save_tile(s.cx,s.cy,tile_meters=2000,outputSize=2048,
                    fn="/datasets/bing_2k/train/masks/"+str(s.id)+".png"
                )
                if i%100==0: print("img:",i)
            print("Mask negs done")
    # sites
    else:
        if TRAIN:
            for i,s in df_sites.iterrows():
                save_tile(s.cx,s.cy,tile_meters=2000,outputSize=2048,
                    fn="/datasets/bing_2k/train/sites/"+str(s.entry_id)+".jpg"
                )
                if i%100==0: print("img:",i)
            print("sites train done")
        if NEGS:
            for i,s in df_negs.iterrows():
                save_tile(s.cx,s.cy,tile_meters=2000,outputSize=2048,
                    fn="/datasets/bing_2k/train/sites/"+str(s.id)+".jpg"
                )
                if i%100==0: print("img:",i)
            print("sites negs done")
        if TEST:
            for i,s in df_maysan.iterrows():
                save_tile(s.cx,s.cy,tile_meters=2000,outputSize=2048,
                    fn="/datasets/bing_2k/maysan/sites/"+str(s.entry_id)+".jpg"
                )
                if i%100==0: print("img:",i)
            print("sites test done") 

def save_dataset_2000_uzbeko(masks):
    df_sites = pd.read_csv("testsetUzbeko_v2.csv")
    print(df_sites.shape)
    # masks
    if masks:
        for i,s in df_sites.iterrows():
            save_tile(s.cx,s.cy,tile_meters=2000,outputSize=2048,
                    fn="/datasetUzbeko/masks/"+str(s.ShortCode)+".png",
                    uzbekistan=True,fn1=str(s.ShortCode)
                )
            if i%100==0: print("img:",i)
        print("Mask train done")
        
    # sites
    else:
       
        for i,s in df_sites.iterrows():
            save_tile(s.cx,s.cy,tile_meters=2000,outputSize=2048,
                fn="/datasetUzbeko/sites/"+str(s.ShortCode)+".jpg"
            )
            if i%100==0: print("img:",i)
        print("sites train done")
       
