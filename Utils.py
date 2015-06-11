def AttachDrawnObjsToCanvas(objs, canvas):
    "Add drawn objs to canvas to prevent them being deleted before drawn"        
    
    if not objs: return

    try:
        canvas.DrawnObjs = [ o for o in objs.values()[:] if (hasattr(o, 'Draw') or hasattr(o, 'DrawLatex'))]
    except AttributeError:
        canvas.DrawnObjs = []
        canvas.DrawnObjs = [ o for o in objs.values()[:] if (hasattr(o, 'Draw') or hasattr(o, 'DrawLatex'))]
    return 
