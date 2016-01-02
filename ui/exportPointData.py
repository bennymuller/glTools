import maya.mel as mel
import maya.cmds as cmds
import glTools.tools.exportPointData
import os.path


def exportPointDataUI():
    """
    Main UI for the exportPointData module
    """
    # Get current frame range
    startFrame = cmds.playbackOptions(q=True, min=True)
    endFrame = cmds.playbackOptions(q=True, max=True)

    # Window
    window = 'exportPointDataUI'
    if cmds.window(window, q=True, ex=True): cmds.deleteUI(window)
    window = cmds.window(window, t='Export Point Data', s=False)

    # Layout
    CL = cmds.columnLayout(adj=True)

    # UI Elements
    pathTBG = cmds.textFieldButtonGrp('exportPoint_pathTBG', label='Path', buttonLabel='...')
    camTBG = cmds.textFieldButtonGrp('exportPoint_camTBG', label='Camera (2D only)', buttonLabel='Select')
    rangeIFG = cmds.intFieldGrp('exportPoint_rangeIFG', nf=2, label='Frame Range', v1=startFrame, v2=endFrame)
    resIFG = cmds.intFieldGrp('exportPoint_resIFG', nf=2, label='Resolution', v1=2348, v2=1152)
    refIFG = cmds.intFieldGrp('exportPoint_refIFG', nf=1, label='Offset Base Frame', v1=startFrame)
    resOMG = cmds.optionMenuGrp('exportPoint_resOMG', label='Resolution Preset')
    export2DB = cmds.button('exportPoint_export2DB', label='Export 2D Point Data',
                          c='glTools.ui.exportPointData.export2DFromUI()')
    export2DOffsetB = cmds.button('exportPoint_export2DOffsetB', label='Export 2D Offset Data',
                                c='glTools.ui.exportPointData.export2DOffsetFromUI()')
    export3DB = cmds.button('exportPoint_export3DB', label='Export 3D Point Data',
                          c='glTools.ui.exportPointData.export3DFromUI()')
    export3DRotB = cmds.button('exportPoint_export3DRotB', label='Export 3D Rotate Data',
                             c='glTools.ui.exportPointData.export3DRotationFromUI()')
    closeB = cmds.button('exportPoint_closeB', label='Close', c='cmds.deleteUI("' + window + '")')

    # Resolution presets
    cmds.setParent(resOMG)
    cmds.menuItem(label='WIDE(full)')
    cmds.menuItem(label='WIDE(half)')
    cmds.menuItem(label='WIDE(quarter)')

    # UI Callbacks
    cmds.textFieldButtonGrp(pathTBG, e=True, bc='glTools.ui.utils.exportFolderBrowser("' + pathTBG + '")')
    cmds.textFieldButtonGrp(camTBG, e=True, bc='glTools.ui.utils.loadTypeSel("' + camTBG + '",selType="transform")')
    cmds.optionMenuGrp(resOMG, e=True, cc='glTools.tools.exportPointData.setResolution()')

    # Popup menu
    cmds.popupMenu(parent=camTBG)
    for cam in cmds.ls(type='camera'):
        if cmds.camera(cam, q=True, orthographic=True): continue
        camXform = cmds.listRelatives(cam, p=True, pa=True)[0]
        cmds.menuItem(l=camXform, c='cmds.textFieldButtonGrp("exportPoint_camTBG",e=True,text="' + camXform + '")')

    # Show Window
    cmds.window(window, e=True, w=435, h=275)
    cmds.showWindow(window)


def setResolution():
    """
    Toggle 2D output resolution from UI
    """
    preset = cmds.optionMenuGrp('exportPoint_resOMG', q=True, sl=True)
    if preset == 1: cmds.intFieldGrp('exportPoint_resIFG', e=True, v1=2348, v2=1152)
    if preset == 2: cmds.intFieldGrp('exportPoint_resIFG', e=True, v1=1174, v2=576)
    if preset == 3: cmds.intFieldGrp('exportPoint_resIFG', e=True, v1=587, v2=288)


def export2DFromUI():
    """
    export2DPointData from UI
    """
    # Get selection
    sel = cmds.ls(sl=True, fl=True)
    if not sel:
        print 'No points selected for export!!'
        return

    # Get UI data
    path = cmds.textFieldButtonGrp('exportPoint_pathTBG', q=True, text=True)
    cam = cmds.textFieldButtonGrp('exportPoint_camTBG', q=True, text=True)
    start = cmds.intFieldGrp('exportPoint_rangeIFG', q=True, v1=True)
    end = cmds.intFieldGrp('exportPoint_rangeIFG', q=True, v2=True)
    xRes = cmds.intFieldGrp('exportPoint_resIFG', q=True, v1=True)
    yRes = cmds.intFieldGrp('exportPoint_resIFG', q=True, v2=True)

    # Check UI data
    if not cam or not cmds.objExists(cam):
        print('No valid camera specified!')
        return
    if start > end:
        print('Invalid range specified!')
        return
    if not path.endswith('/'): path += '/'

    # For each point
    for pt in sel:

        # Generate export file path
        sel_name = pt.split(':')[-1].replace('.', '_').replace('[', '_').replace(']', '')
        filepath = path + sel_name + '_2D.txt'

        # Check path
        if os.path.isfile(filepath):
            chk = cmds.confirmDialog(t='Warning: File exists',
                                   message='File "' + filepath + '" already exist! Overwrite?', button=['Yes', 'No'],
                                   defaultButton='Yes', cancelButton='No', dismissString='No')
            if chk == 'No': continue

        # Isolate Select - ON
        setIsolateSelect(pt, 1)

        # Export data
        glTools.tools.exportPointData.export2DPointData(filepath, pt, cam, start, end, xRes, yRes)

        # Isolate Select - OFF
        setIsolateSelect(pt, 0)


def export2DOffsetFromUI():
    """
    export2DOffsetData from UI
    """
    # Get selection
    sel = cmds.ls(sl=True, fl=True)
    if not sel:
        print 'No points selected for export!!'
        return

    # Get UI data
    path = cmds.textFieldButtonGrp('exportPoint_pathTBG', q=True, text=True)
    cam = cmds.textFieldButtonGrp('exportPoint_camTBG', q=True, text=True)
    start = cmds.intFieldGrp('exportPoint_rangeIFG', q=True, v1=True)
    end = cmds.intFieldGrp('exportPoint_rangeIFG', q=True, v2=True)
    ref = cmds.intFieldGrp('exportPoint_refIFG', q=True, v1=True)
    xRes = cmds.intFieldGrp('exportPoint_resIFG', q=True, v1=True)
    yRes = cmds.intFieldGrp('exportPoint_resIFG', q=True, v2=True)

    # Check UI data
    if not cam or not cmds.objExists(cam):
        print('No valid camera specified!')
        return
    if start > end:
        print('Invalid range specified!')
        return
    if not path.endswith('/'): path += '/'

    # For each point
    for pt in sel:

        # Generate export file path
        sel_name = pt.split(':')[-1].replace('.', '_').replace('[', '_').replace(']', '')
        filepath = path + sel_name + '_2DOffset.txt'

        # Check path
        if os.path.isfile(filepath):
            chk = cmds.confirmDialog(t='Warning: File exists',
                                   message='File "' + filepath + '" already exist! Overwrite?', button=['Yes', 'No'],
                                   defaultButton='Yes', cancelButton='No', dismissString='No')
            if chk == 'No': continue

        # Isolate Select - ON
        setIsolateSelect(pt, 1)

        # Export data
        glTools.tools.exportPointData.export2DOffsetData(filepath, pt, cam, start, end, xRes, yRes, ref)

        # Isolate Select - OFF
        setIsolateSelect(pt, 0)


def export3DFromUI():
    """
    export3DPointData from UI
    """
    # Get selection
    sel = cmds.ls(sl=True, fl=True)
    if not sel:
        print 'No points selected for export!!'
        return

    # Get UI data
    path = cmds.textFieldButtonGrp('exportPoint_pathTBG', q=True, text=True)
    start = cmds.intFieldGrp('exportPoint_rangeIFG', q=True, v1=True)
    end = cmds.intFieldGrp('exportPoint_rangeIFG', q=True, v2=True)

    # Check UI data
    if start > end:
        print('Invalid range specified!')
        return
    if not path.endswith('/'): path += '/'

    # For each point
    for pt in sel:

        # Generate export file path
        sel_name = pt.split(':')[-1].replace('.', '_').replace('[', '_').replace(']', '')
        filepath = path + sel_name + '_3D.txt'

        # Check path
        if os.path.isfile(filepath):
            chk = cmds.confirmDialog(t='Warning: File exists',
                                   message='File "' + filepath + '" already exist! Overwrite?', button=['Yes', 'No'],
                                   defaultButton='Yes', cancelButton='No', dismissString='No')
            if chk == 'No': continue

        # Isolate Select - ON
        setIsolateSelect(pt, 1)

        # Export data
        glTools.tools.exportPointData.export3DPointData(filepath, pt, start, end)

        # Isolate Select - OFF
        setIsolateSelect(pt, 0)


def export3DRotationFromUI():
    """
    export3DRotationData from UI
    """
    # Get selection
    sel = cmds.ls(sl=True, fl=True, type=['transform', 'joint'])
    if not sel:
        print 'No valid transform selected for export!!'
        return

    # Get UI data
    path = cmds.textFieldButtonGrp('exportPoint_pathTBG', q=True, text=True)
    start = cmds.intFieldGrp('exportPoint_rangeIFG', q=True, v1=True)
    end = cmds.intFieldGrp('exportPoint_rangeIFG', q=True, v2=True)

    # Check UI data
    if start > end:
        print('Invalid range specified!')
        return
    if not path.endswith('/'): path += '/'

    # For each point
    for pt in sel:

        # Generate export file path
        sel_name = pt.split(':')[-1].replace('.', '_').replace('[', '_').replace(']', '')
        filepath = path + sel_name + '_3Drot.txt'

        # Check path
        if os.path.isfile(filepath):
            chk = cmds.confirmDialog(t='Warning: File exists',
                                   message='File "' + filepath + '" already exist! Overwrite?', button=['Yes', 'No'],
                                   defaultButton='Yes', cancelButton='No', dismissString='No')
            if chk == 'No': continue

        # Isolate Select - ON
        setIsolateSelect(pt, 1)

        # Export data
        glTools.tools.exportPointData.export3DRotationData(filepath, pt, start, end, rotateOrder='zxy')

        # Isolate Select - OFF
        setIsolateSelect(pt, 0)


def setIsolateSelect(pt, state):
    """
    """
    # Check point
    if not cmds.objExists(pt):
        raise Exception('Object "' + pt + '" does not exist!')

    # Select point
    cmds.select(pt)

    # Get panel list
    panelList = cmds.getPanel(type='modelPanel')

    # For each panel
    for panel in panelList: cmds.isolateSelect(panel, state=state)
