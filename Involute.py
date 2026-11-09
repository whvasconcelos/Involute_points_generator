#CRIAÇÃO DOS PONTOS DE UM DENTE DE ENGRENAGEM

import numpy as np
import pandas as pd
from pathlib import Path

base_radius=float(input("Base radius: ")) #20 as an example
delta_radius=float(input("Delta to external radius: ")) #5 as an example
num_pts=int(input("Number of points to create: ")) #20 as an example
external_radius=base_radius+delta_radius
angle=np.acos(base_radius/external_radius)

def cord_x(alpha):
    return -base_radius*np.sqrt(1+alpha**2)*np.sin(alpha-np.atan(alpha))

def cord_y(alpha):
    return base_radius*(1+(np.sqrt(1+alpha**2)*np.cos(alpha-np.atan(alpha))-1))


alpha_values=(angle/num_pts)*(np.arange(0,num_pts)+1)
alpha_values=np.insert(alpha_values,0,0)
#print(alpha_values)

#--------------------------------------------------------------------------------------------------------------------------------------------------------
# Generating the command lines to use in FreeCAD Macros.
Path("commands.txt").write_text(f'''#FreeCAD commands:
import FreeCAD
import PartDesign
import PartDesignGui
import Sketcher
App.getDocument('Unnamed').getObject('Body').newObject('Sketcher::SketchObject','Sketch')
App.getDocument('Unnamed').getObject('Sketch').AttachmentSupport = (App.getDocument('Unnamed').getObject('Origin'),['XY_Plane'])
App.getDocument('Unnamed').getObject('Sketch').MapMode = 'FlatFace'
''')

# Generating the points
points=[]
counter=0
for a in alpha_values:
    file=open('commands.txt','a')
    cord=([cord_x(a),cord_y(a)])
    file.write(f'''App.getDocument('Unnamed').getObject('Sketch').addGeometry(Part.Point(App.Vector({cord_x(a):.6f},{cord_y(a):.6f},0)), False)\n''')
App.getDocument('Unnamed').getObject('Sketch').addConstraint(Sketcher.Constraint('DistanceX',{counter},1,{cord_x(a):.6f}))
App.getDocument('Unnamed').getObject('Sketch').addConstraint(Sketcher.Constraint('DistanceY',{counter},1,{cord_y(a):.6f}))\n''')
    file.close
    points.append(cord)
    counter=counter+1

# Generating the lines
for value in np.arange(0,num_pts):
    file=open('commands.txt','a')
    file.write(f'''App.getDocument('Unnamed').getObject('Sketch').addGeometry(Part.LineSegment(App.Vector({points[value][0]:.6f},{points[value][1]:.6f},0),App.Vector({points[value+1][0]:.6f},{points[value+1][1]:.6f},0)),False)
App.getDocument('Unnamed').getObject('Sketch').addConstraint(Sketcher.Constraint('Coincident',{value+num_pts+1},1,{value},1)) 
App.getDocument('Unnamed').getObject('Sketch').addConstraint(Sketcher.Constraint('Coincident',{value+num_pts+1},2,{value+1},1))\n''')
    file.close

#--------------------------------------------------------------------------------------------------------------------------------------------------------
#Generating a csv table with cordinates
export=pd.DataFrame(points,columns=['cord_x','cord_y'])

print(export)
export.to_csv('cordinates_test.csv', index=False)
