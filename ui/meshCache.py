import maya.cmds as cmds
import glTools.tools.meshCache
import glTools.utils.mesh


def meshCacheUI():
    """
    Main UI for the meshCache module
    """
    # Get current frame range
    startFrame = cmds.playbackOptions(q=True, min=True)
    endFrame = cmds.playbackOptions(q=True, max=True)

    # Window
    window = 'meshCacheUI'
    if cmds.window(window, q=True, ex=True): cmds.deleteUI(window)
    window = cmds.window(window, t='Export Mesh Cache', s=True)

    # Layout
    CL = cmds.columnLayout(adj=True)

    # UI Elements
    pathTBG = cmds.textFieldButtonGrp('meshCache_pathTBG', label='Path', buttonLabel='...')
    nameTFG = cmds.textFieldGrp('meshCache_nameTFG', label='Combine Cache Name', text='')
    rangeIFG = cmds.intFieldGrp('meshCache_rangeIFG', nf=2, label='Frame Range', v1=startFrame, v2=endFrame)
    paddingIFG = cmds.intFieldGrp('meshCache_paddingIFG', nf=1, label='Frame Padding', v1=4)
    uvSetTFG = cmds.textFieldGrp('meshCache_uvSetTFG', label='UV Set', text='default')
    spaceRBG = cmds.radioButtonGrp('meshCache_spaceRBG', label='Output Mode', labelArray2=['Local', 'World'],
                                 numberOfRadioButtons=2, sl=2)
    gzipCBG = cmds.checkBoxGrp('meshCache_gzipCBG', numberOfCheckBoxes=1, label='gzip', v1=False)
    exportGeoB = cmds.button('meshCache_exportGeoB', label='Export GEO', c='glTools.ui.meshCache.exportGeoFromUI()')
    exportGeoCombineB = cmds.button('meshCache_exportGeoCombineB', label='Export GEO Combined',
                                  c='glTools.ui.meshCache.exportGeoCombinedFromUI()')
    exportObjB = cmds.button('meshCache_exportObjB', label='Export OBJ', c='glTools.ui.meshCache.exportObjFromUI()')
    exportObjCombineB = cmds.button('meshCache_exportObjCombineB', label='Export OBJ Combined',
                                  c='glTools.ui.meshCache.exportObjCombinedFromUI()')
    closeB = cmds.button('meshCache_closeB', label='Close', c='cmds.deleteUI("' + window + '")')

    # UI Callbacks
    cmds.textFieldButtonGrp(pathTBG, e=True, bc='glTools.ui.utils.exportFolderBrowser("' + pathTBG + '")')

    # Show Window
    cmds.window(window, e=True, w=450, h=262)
    cmds.showWindow(window)


def exportGeoFromUI():
    """
    writeGeoCache from UI
    """
    # Get UI info
    path = cmds.textFieldButtonGrp('meshCache_pathTBG', q=True, text=True)
    start = cmds.intFieldGrp('meshCache_rangeIFG', q=True, v1=True)
    end = cmds.intFieldGrp('meshCache_rangeIFG', q=True, v2=True)
    pad = cmds.intFieldGrp('meshCache_paddingIFG', q=True, v1=True)
    uvSet = cmds.textFieldGrp('meshCache_uvSetTFG', q=True, text=True)
    worldSpace = bool(cmds.radioButtonGrp('meshCache_spaceRBG', q=True, sl=True) - 1)
    gz = cmds.checkBoxGrp('meshCache_gzipCBG', q=True, v1=True)

    # Check UV Set
    if uvSet == 'default': uvSet = ''

    # Get selection
    sel = [i for i in cmds.ls(sl=True, fl=True, o=True) if glTools.utils.mesh.isMesh(i)]
    if not sel:
        print 'No valid mesh objects selected for export!!'
        return

    # Export each mesh
    for mesh in sel:
        # Generate file name
        mesh_name = mesh.replace(':', '_')

        # Export
        glTools.tools.meshCache.writeGeoCache(path, mesh_name, mesh, start, end, pad, uvSet, worldSpace, gz)


def exportGeoCombinedFromUI():
    """
    writeGeoCombineCache from UI
    """
    # Get UI info
    path = cmds.textFieldButtonGrp('meshCache_pathTBG', q=True, text=True)
    name = cmds.textFieldGrp('meshCache_nameTFG', q=True, text=True)
    start = cmds.intFieldGrp('meshCache_rangeIFG', q=True, v1=True)
    end = cmds.intFieldGrp('meshCache_rangeIFG', q=True, v2=True)
    pad = cmds.intFieldGrp('meshCache_paddingIFG', q=True, v1=True)
    uvSet = cmds.textFieldGrp('meshCache_uvSetTFG', q=True, text=True)
    worldSpace = bool(cmds.radioButtonGrp('meshCache_spaceRBG', q=True, sl=True) - 1)
    gz = cmds.checkBoxGrp('meshCache_gzipCBG', q=True, v1=True)

    # Check Name
    if not name:
        print 'Provide valid cache name and try again!'
        return

    # Check UV Set
    if uvSet == 'default': uvSet = ''

    # Get selection
    sel = [i for i in cmds.ls(sl=True, fl=True, o=True) if glTools.utils.mesh.isMesh(i)]
    if not sel:
        print 'No valid mesh objects selected for export!!'
        return

    # Write Combine Cache
    glTools.tools.meshCache.writeGeoCombineCache(path, name, sel, start, end, pad, uvSet, worldSpace, gz)


def exportObjFromUI():
    """
    writeObjCache from UI
    """
    # Get UI info
    path = cmds.textFieldButtonGrp('meshCache_pathTBG', q=True, text=True)
    start = cmds.intFieldGrp('meshCache_rangeIFG', q=True, v1=True)
    end = cmds.intFieldGrp('meshCache_rangeIFG', q=True, v2=True)
    pad = cmds.intFieldGrp('meshCache_paddingIFG', q=True, v1=True)
    uvSet = cmds.textFieldGrp('meshCache_uvSetTFG', q=True, text=True)
    worldSpace = bool(cmds.radioButtonGrp('meshCache_spaceRBG', q=True, sl=True) - 1)
    gz = cmds.checkBoxGrp('meshCache_gzipCBG', q=True, v1=True)

    # Check UV Set
    if uvSet == 'default': uvSet = ''

    # Get selection
    sel = [i for i in cmds.ls(sl=True, fl=True, o=True) if glTools.utils.mesh.isMesh(i)]
    if not sel:
        print 'No valid mesh objects selected for export!!'
        return

    # Export each mesh
    for mesh in sel:
        # Generate file name
        mesh_name = mesh.replace(':', '_')

        # Export
        glTools.tools.meshCache.writeObjCache(path, mesh_name, mesh, start, end, pad, uvSet, worldSpace, gz)


def exportObjCombinedFromUI():
    """
    writeObjCombineCache from UI
    """
    # Get UI info
    path = cmds.textFieldButtonGrp('meshCache_pathTBG', q=True, text=True)
    name = cmds.textFieldGrp('meshCache_nameTFG', q=True, text=True)
    start = cmds.intFieldGrp('meshCache_rangeIFG', q=True, v1=True)
    end = cmds.intFieldGrp('meshCache_rangeIFG', q=True, v2=True)
    pad = cmds.intFieldGrp('meshCache_paddingIFG', q=True, v1=True)
    uvSet = cmds.textFieldGrp('meshCache_uvSetTFG', q=True, text=True)
    worldSpace = bool(cmds.radioButtonGrp('meshCache_spaceRBG', q=True, sl=True) - 1)
    gz = cmds.checkBoxGrp('meshCache_gzipCBG', q=True, v1=True)

    # Check Name
    if not name:
        print 'Provide valid cache name and try again!'
        return

    # Check UV Set
    if uvSet == 'default': uvSet = None

    # Get selection
    sel = [i for i in cmds.ls(sl=True, fl=True, o=True) if glTools.utils.mesh.isMesh(i)]
    if not sel:
        print 'No valid mesh objects selected for export!!'
        return

    # Write Combine Cache
    glTools.tools.meshCache.writeObjCombineCache(path, name, sel, start, end, pad, uvSet, worldSpace, gz)
