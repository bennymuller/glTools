import maya.cmds as cmds
import maya.mel as mel


def ui():
    """
    """
    # Window
    win = 'graphFilterUI'
    if cmds.window(win, q=True, ex=True): cmds.deleteUI(win)
    win = cmds.window(win, t='Graph Editor Filter', mxb=True, mnb=True, s=True, wh=[248, 210])

    # Layout
    fl = cmds.formLayout(numberOfDivisions=100)

    # UI Elements
    graphFilterAttrListTSL = cmds.textScrollList('graphFilter_attrListTSL', w=120, nr=8, ams=True)

    graphFilterModeRBG = cmds.radioButtonGrp('graphFilter_modeRBG', label='Mode', labelArray2=['Replace', 'Append'],
                                           nrb=2, sl=1)

    graphEditorB = cmds.button(l='Graph Editor', c='mel.eval("GraphEditor")')
    allCurveB = cmds.button(l='All Curves', c='displayAllCurves()')
    clearViewB = cmds.button(l='Clear View', c='cmds.selectionConnection("graphEditor1FromOutliner",e=True,clear=True)')

    graphFilterFilterB = cmds.button('graphFilter_filterB', l='Filter Selected',
                                   c='glTools.tools.graphFilter.filterCurves()')
    graphFilterSelectB = cmds.button('graphFilter_selectB', l='Select All', c='glTools.tools.graphFilter.selectAll()')
    graphFilterClearB = cmds.button('graphFilter_clearB', l='Clear list',
                                  c='cmds.textScrollList("graphFilter_attrListTSL",e=True,ra=True)')
    graphFilterUpdateB = cmds.button('graphFilter_updateB', l='Update List',
                                   c='glTools.tools.graphFilter.updateAttrList()')

    # Form Layout
    cmds.formLayout(fl, e=True, af=[(graphFilterAttrListTSL, 'left', 5), (graphFilterAttrListTSL, 'bottom', 5)],
                  ap=[(graphFilterAttrListTSL, 'right', 5, 50)],
                  ac=[(graphFilterAttrListTSL, 'top', 5, graphFilterModeRBG)])
    cmds.formLayout(fl, e=True, af=[(graphFilterModeRBG, 'left', 5), (graphFilterModeRBG, 'right', 5)],
                  ac=[(graphFilterModeRBG, 'top', 5, graphEditorB)])
    cmds.formLayout(fl, e=True, af=[(graphEditorB, 'left', 5), (graphEditorB, 'top', 5)],
                  ap=[(graphEditorB, 'right', 5, 33)])
    cmds.formLayout(fl, e=True, af=[(allCurveB, 'top', 5)], ap=[(allCurveB, 'left', 5, 33), (allCurveB, 'right', 5, 66)])
    cmds.formLayout(fl, e=True, af=[(clearViewB, 'right', 5), (clearViewB, 'top', 5)], ap=[(clearViewB, 'left', 5, 66)])
    cmds.formLayout(fl, e=True, af=[(graphFilterFilterB, 'right', 5)], ap=[(graphFilterFilterB, 'left', 5, 50)],
                  ac=[(graphFilterFilterB, 'top', 5, graphFilterModeRBG)])
    cmds.formLayout(fl, e=True, af=[(graphFilterSelectB, 'right', 5)], ap=[(graphFilterSelectB, 'left', 5, 50)],
                  ac=[(graphFilterSelectB, 'top', 5, graphFilterFilterB)])
    cmds.formLayout(fl, e=True, af=[(graphFilterClearB, 'right', 5)], ap=[(graphFilterClearB, 'left', 5, 50)],
                  ac=[(graphFilterClearB, 'top', 5, graphFilterSelectB)])
    cmds.formLayout(fl, e=True, af=[(graphFilterUpdateB, 'right', 5)], ap=[(graphFilterUpdateB, 'left', 5, 50)],
                  ac=[(graphFilterUpdateB, 'top', 5, graphFilterClearB)])

    # Update keyable attribute list
    updateAttrList()

    # Show window
    cmds.showWindow(win)


def updateAttrList():
    """
    """
    # Clear attribute list
    cmds.textScrollList('graphFilter_attrListTSL', e=True, ra=True)

    # Get current selection
    sel = cmds.ls(sl=True)
    if not sel: return

    # List all keyable attributes
    attrList = list(set(cmds.listAttr(sel, k=True)))
    attrList.sort()

    # Update textScrollList
    for attr in attrList: cmds.textScrollList('graphFilter_attrListTSL', e=True, a=attr)

    # Return result
    return attrList


def selectAll():
    """
    """
    # Select all attributes in the list
    for i in range(cmds.textScrollList('graphFilter_attrListTSL', q=True, ni=True)):
        cmds.textScrollList('graphFilter_attrListTSL', e=True, sii=(i + 1))


def displayAllCurves():
    """
    """
    # Display all attribute curves
    sel = cmds.selectionConnection('graphEditorList', q=True, object=True)
    for obj in sel: cmds.selectionConnection('graphEditor1FromOutliner', e=True, select=obj)


def addCurveToEditor(attr):
    """
    """
    # Get current selection
    sel = cmds.ls(sl=True)
    for obj in sel:
        objAttr = obj + '.' + attr
        # Check attr
        if cmds.objExists(objAttr):
            # Add to graphEditor
            cmds.selectionConnection('graphEditor1FromOutliner', e=True, select=objAttr)


def filterCurves():
    """
    """
    # Check attribute list selection
    if cmds.textScrollList('graphFilter_attrListTSL', q=True, nsi=True):

        # Check mode
        if cmds.radioButtonGrp('graphFilter_modeRBG', q=True, sl=True) == 1:
            cmds.selectionConnection('graphEditor1FromOutliner', e=True, clear=True)
        attrs = cmds.textScrollList('graphFilter_attrListTSL', q=True, si=True)
        for attr in attrs: addCurveToEditor(attr)

    # Update UI
    mel.eval('GraphEditor')
    mel.eval('SelectAllMarkingMenu')
    mel.eval('buildSelectAllMM')
    mel.eval('SelectAllMarkingMenuPopDown')
