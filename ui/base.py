import maya.cmds as cmds
import glTools.utils.base


def parentListUI():
    """
    UI for parentList()
    """
    # Window
    window = 'parentListUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Parent List')

    # Layout
    fl = cmds.formLayout(numberOfDivisions=100)

    # UI Elements
    childTXT = cmds.text(l='Child List:', al='left')
    childTSL = cmds.textScrollList('parentList_childListTSL', allowMultiSelection=True)

    parentTXT = cmds.text(l='Parent List:', al='left')
    parentTSL = cmds.textScrollList('parentList_parentListTSL', allowMultiSelection=True)

    parentB = cmds.button(label='Parent', c='glTools.ui.base.parentListFromUI()')
    cancelB = cmds.button(label='Cancel', c='cmds.deleteUI("' + window + '")')

    # Layout
    cmds.formLayout(fl, e=True, af=[(childTXT, 'left', 5), (childTXT, 'top', 5)], ap=[(childTXT, 'right', 5, 50)])
    cmds.formLayout(fl, e=True, af=[(childTSL, 'left', 5)], ap=[(childTSL, 'right', 5, 50)],
                  ac=[(childTSL, 'top', 5, childTXT), (childTSL, 'bottom', 5, parentB)])

    cmds.formLayout(fl, e=True, af=[(parentTXT, 'right', 5), (parentTXT, 'top', 5)], ap=[(parentTXT, 'left', 5, 50)])
    cmds.formLayout(fl, e=True, af=[(parentTSL, 'right', 5)], ap=[(parentTSL, 'left', 5, 50)],
                  ac=[(parentTSL, 'top', 5, parentTXT), (parentTSL, 'bottom', 5, cancelB)])

    cmds.formLayout(fl, e=True, af=[(parentB, 'left', 5), (parentB, 'bottom', 5)], ap=[(parentB, 'right', 5, 50)])
    cmds.formLayout(fl, e=True, af=[(cancelB, 'right', 5), (cancelB, 'bottom', 5)], ap=[(cancelB, 'left', 5, 50)])

    # UI Callbacks

    cmds.textScrollList(childTSL, e=True, dcc='glTools.ui.utils.selectFromTSL("' + childTSL + '")')
    cmds.textScrollList(childTSL, e=True, dkc='glTools.ui.utils.removeFromTSL("' + childTSL + '")')

    cmds.textScrollList(parentTSL, e=True, dcc='glTools.ui.utils.selectFromTSL("' + parentTSL + '")')
    cmds.textScrollList(parentTSL, e=True, dkc='glTools.ui.utils.removeFromTSL("' + parentTSL + '")')

    # Popup menu

    childPUM = cmds.popupMenu(parent=childTSL)
    cmds.menuItem(l='Add Selected', c='glTools.ui.utils.addToTSL("' + childTSL + '")')
    cmds.menuItem(l='Remove Selected', c='glTools.ui.utils.removeFromTSL("' + childTSL + '")')
    cmds.menuItem(l='Clear List', c='cmds.textScrollList("' + childTSL + '",e=True,ra=True)')
    cmds.menuItem(l='Select Hilited', c='glTools.ui.utils.selectFromTSL("' + childTSL + '")')

    parentPUM = cmds.popupMenu(parent=parentTSL)
    cmds.menuItem(l='Add Selected', c='glTools.ui.utils.addToTSL("' + parentTSL + '")')
    cmds.menuItem(l='Remove Selected', c='glTools.ui.utils.removeFromTSL("' + parentTSL + '")')
    cmds.menuItem(l='Clear List', c='cmds.textScrollList("' + parentTSL + '",e=True,ra=True)')
    cmds.menuItem(l='Select Hilited', c='glTools.ui.utils.selectFromTSL("' + parentTSL + '")')

    # Display UI
    cmds.showWindow(window)


def parentListFromUI():
    """
    """
    # Get child list
    childList = cmds.textScrollList('parentList_childListTSL', q=True, ai=True)
    # Get parent list
    parentList = cmds.textScrollList('parentList_parentListTSL', q=True, ai=True)
    # Parent child list to parent list
    glTools.utils.base.parentList(childList, parentList)


def renameHistoryNodesUI():
    """
    UI for parentList()
    """
    # Window
    window = 'renameHistoryNodesUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Rename History Nodes')

    # Layout
    cl = cmds.columnLayout()

    # UI Elements
    nodeTypeTFG = cmds.textFieldGrp('renameHist_nodeTypeTFG', label='Node Type')
    nodeSuffixTFG = cmds.textFieldGrp('renameHist_nodeSuffixTFG', label='Node Suffix')
    stripSuffixCBG = cmds.checkBoxGrp('renameHist_stripSuffixCBG', l='Strip Old Suffix', ncb=1, v1=True)

    renameB = cmds.button(label='Rename', c='glTools.ui.base.renameHistoryNodesFromUI()')
    cancelB = cmds.button(label='Cancel', c='cmds.deleteUI("' + window + '")')

    # Display UI
    cmds.showWindow(window)


def renameHistoryNodesFromUI():
    """
    """
    # Get node type and suffix lists
    nodeType = cmds.textFieldGrp('renameHist_nodeTypeTFG', q=True, text=True)
    nodeSuffix = cmds.textFieldGrp('renameHist_nodeSuffixTFG', q=True, text=True)
    stripSuffix = cmds.checkBoxGrp('renameHist_stripSuffixCBG', q=True, v1=True)

    nodeTypeList = nodeType.split(' ')
    nodeSuffixList = nodeSuffix.split(' ')

    if len(nodeTypeList) != len(nodeSuffixList):
        if nodeSuffixList:
            raise Exception('Node type and suffix list length mis-match!')

    # Get scene selection
    sel = cmds.ls(sl=1)

    # For each object in selection
    for obj in sel:

        # For each node type
        for i in range(len(nodeTypeList)):

            # Determine suffix
            nodeSuffix = ''
            if nodeSuffixList: nodeSuffix = nodeSuffixList[i]

            # Rename nodes
            glTools.utils.base.renameHistoryNodes(obj, nodeTypeList[i], suffix=nodeSuffix, stripOldSuffix=stripSuffix)
