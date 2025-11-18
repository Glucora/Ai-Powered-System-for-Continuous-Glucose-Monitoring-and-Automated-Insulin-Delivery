import dearpygui.dearpygui as dpg
from enum import Enum





class Shape:
    def __init__(self, startPos :tuple[int, int],fillColor : tuple[int, int, int,int] =(255,255,255,255), textLabel : str = "" , textLabelSize: int =14):
        self.xpos = startPos[0]
        self.ypos = startPos[1]
        self.textLabel = textLabel
        self.textLabelSize = textLabelSize
        self.fill = fillColor
        

    def updateShapeColor(self,updatedColor: tuple [int, int ,int ,int]):
        dpg.configure_item(self.tag, fill=updatedColor)

class Circle(Shape):
    def __init__(self,center :tuple[int, int], radius :int, fillColor : tuple[int, int, int,int],textLabel : str = "" , textLabelSize: int =14):
        super().__init__(startPos=center, textLabel=textLabel, textLabelSize=textLabelSize, fillColor=fillColor)
        self.radius = radius
        self.tag = dpg.draw_circle(center=center,radius=radius, fill=fillColor)
        dpg.draw_text(pos=center, text=self.textLabel, size=self.textLabelSize, color=(0,0,0,255))



class Rectangle(Shape):
    def __init__(self,v1 :tuple[int, int], height: int, width: int, fillColor : tuple[int, int, int,int] ,textLabel : str = "" , textLabelSize: int =14 ):
        super().__init__(startPos=v1, textLabel=textLabel, textLabelSize=textLabelSize, fillColor=fillColor)
        self.height = height
        self.width =width
        v2 = (v1[0] + width, v1[1] + height)

        self.tag = dpg.draw_rectangle(pmin=v1, pmax=v2,fill=fillColor)
        
        txtPos = ((v1[0]+self.width/2.5)-len(textLabel) , (v1[1]+ 0.5 *self.height))
        dpg.draw_text(pos=txtPos, text=self.textLabel, size=self.textLabelSize, color=(0,0,0,255))  


class PhoneShape(Shape):
    def __init__(self, startPos : tuple[int, int], height: int, width: int ,fillColor = (255, 255, 255, 255), textLabel = "", textLabelSize = 14):
        super().__init__(startPos, fillColor, textLabel, textLabelSize)

        self.height = height
        self.width =width

        dpg.draw_rectangle(pmin=startPos, pmax=((startPos[0] + width),( startPos[1] + height)), fill=fillColor)
        self.tag = dpg.draw_rectangle(pmin=((startPos[0]*1.01),(startPos[1]*1.05)), pmax=(((startPos[0] + 0.95 * width)),( startPos[1] + 0.80 * height)),fill=(190,190,190,255))
        dpg.draw_circle(center=[(startPos[0] + 0.5 * width),(startPos[1] +  height- 20)], radius=15, fill=(0,0,0,255))
        txtPos = ((startPos[0]+width/2.5)-len(textLabel) , (startPos[1]+ 0.5 *height))
        dpg.draw_text(pos=txtPos, text=self.textLabel, size=self.textLabelSize, color=(0,0,0,255))

class ShapeConnection():
    def __init__(self, shape1 : Shape | Circle | Rectangle | PhoneShape, shape2: Shape | Circle | Rectangle | PhoneShape):
        if isinstance(shape1,Rectangle | PhoneShape):
            startPos =  (shape1.xpos   , (shape1.ypos + shape1.height) -0.5 * shape1.height)
        else:
            startPos = (shape1.xpos, shape1.ypos)     
        if isinstance(shape2,Rectangle | PhoneShape):
            endPos =  (shape2.xpos + shape2.width , (shape2.ypos + 0.5 * shape2.height))
        else:
            endPos = (shape2.xpos, shape2.ypos)
        dpg.draw_arrow(startPos, endPos, color=(255,255,255,255))