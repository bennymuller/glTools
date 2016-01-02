import maya.mel as mel
import maya.cmds as cmds
import glTools.utils.reference


def removeReferenceEditsUI():
    """
    """
    # Define Local Command Prefix
    cmdPrefix = 'import glTools.tools.removeReferenceEdits;reload(glTools.tools.removeReferenceEdits);glTools.tools.removeReferenceEdits.'

    # ================
    # - Build Window -
    # ================

    window = 'removeReferenceEditsUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Remove Reference Edits')

    # ===============
    # - UI Elements -
    # ===============

    # Layout
    FL = cmds.formLayout()

    refListTXT = cmds.text(label='Reference List')
    refListTSL = cmds.textScrollList('refEdits_refListTSL', allowMultiSelection=False)
    nodeListTXT = cmds.text(label='Node List')
    nodeListTSL = cmds.textScrollList('refEdits_nodeListTSL', allowMultiSelection=True)
    nodeSearchTFG = cmds.textFieldButtonGrp('refEdits_nodeSearchTFG', label='Node Search', buttonLabel='Clear', text='',
                                          cw=(1, 80))

    nodeSearchSEP = cmds.separator(style='single')

    showNamespaceCBG = cmds.checkBoxGrp('refEdits_showNamespaceCBG', numberOfCheckBoxes=1, label='Show Namespace',
                                      v1=False)
    showLongNamesCBG = cmds.checkBoxGrp('refEdits_showLongNamesCBG', numberOfCheckBoxes=1, label='Show Long Names',
                                      v1=False)
    showSuccessEditsCBG = cmds.checkBoxGrp('refEdits_showSuccessEditsCBG', numberOfCheckBoxes=1,
                                         label='Show Successful Edits', v1=True)
    showFailedEditsCBG = cmds.checkBoxGrp('refEdits_showFailedEditsCBG', numberOfCheckBoxes=1, label='Show Failed Edits',
                                        v1=True)

    showDetailsSEP = cmds.separator(style='single')

    # Edit Command Check Boxes
    parentCBG = cmds.checkBoxGrp('refEdits_parentCBG', numberOfCheckBoxes=1, label='parent', v1=True)
    setAttrCBG = cmds.checkBoxGrp('refEdits_setAttrCBG', numberOfCheckBoxes=1, label='setAttr', v1=True)
    addAttrCBG = cmds.checkBoxGrp('refEdits_addAttrCBG', numberOfCheckBoxes=1, label='addAttr', v1=True)
    delAttrCBG = cmds.checkBoxGrp('refEdits_delAttrCBG', numberOfCheckBoxes=1, label='deleteAttr', v1=True)
    conAttrCBG = cmds.checkBoxGrp('refEdits_conAttrCBG', numberOfCheckBoxes=1, label='connectAttr', v1=True)
    disconAttrCBG = cmds.checkBoxGrp('refEdits_disconAttrCBG', numberOfCheckBoxes=1, label='disconnectAttr', v1=True)

    # Buttons
    printEditsAttrB = cmds.button(label='Print Edit Attributes', c=cmdPrefix + 'printNodeEditAttributes()')
    printEditsCmdsB = cmds.button(label='Print Edit Commands', c=cmdPrefix + 'printNodeEditCommands()')
    removeEditsB = cmds.button(label='Remove Edits', c=cmdPrefix + 'removeReferenceEditsFromUI()')
    closeB = cmds.button(label='Close', c='cmds.deleteUI("' + window + '")')

    # ===============
    # - Pop-up Menu -
    # ===============

    # Reference List
    cmds.popupMenu(parent=refListTSL)
    cmds.menuItem('Reload Reference', c=cmdPrefix + 'reloadReferenceFromUI()')
    cmds.menuItem('Unload Reference', c=cmdPrefix + 'unloadReferenceFromUI()')
    cmds.menuItem('Remove Reference', c=cmdPrefix + 'removeReferenceFromUI()')
    cmds.menuItem('Import Reference', c=cmdPrefix + 'importReferenceFromUI()')

    # Node List
    cmds.popupMenu(parent=nodeListTSL)
    cmds.menuItem('Select', c=cmdPrefix + 'selectNode()')
    cmds.menuItem('Print Edit Attributes', c=cmdPrefix + 'printNodeEditAttributes()')
    cmds.menuItem('Print Edit Commands', c=cmdPrefix + 'printNodeEditCommands()')

    # ================
    # - UI Callbacks -
    # ================

    loadNodesCmd = cmdPrefix + 'loadNodeList()'

    # Select Reference
    cmds.textScrollList(refListTSL, e=True, sc=loadNodesCmd)

    # Search Node Field
    cmds.textFieldButtonGrp(nodeSearchTFG, e=True, cc=cmdPrefix + 'filterNodeList()')
    cmds.textFieldButtonGrp(nodeSearchTFG, e=True, bc=cmdPrefix + 'clearSeachField()')

    # Show Details
    cmds.checkBoxGrp(showNamespaceCBG, e=True, cc=loadNodesCmd)
    cmds.checkBoxGrp(showLongNamesCBG, e=True, cc=loadNodesCmd)
    cmds.checkBoxGrp(showSuccessEditsCBG, e=True, cc=loadNodesCmd)
    cmds.checkBoxGrp(showFailedEditsCBG, e=True, cc=loadNodesCmd)

    # Edit Commands
    cmds.checkBoxGrp(parentCBG, e=True, cc=loadNodesCmd)
    cmds.checkBoxGrp(setAttrCBG, e=True, cc=loadNodesCmd)
    cmds.checkBoxGrp(addAttrCBG, e=True, cc=loadNodesCmd)
    cmds.checkBoxGrp(delAttrCBG, e=True, cc=loadNodesCmd)
    cmds.checkBoxGrp(conAttrCBG, e=True, cc=loadNodesCmd)
    cmds.checkBoxGrp(disconAttrCBG, e=True, cc=loadNodesCmd)

    # ===============
    # - Form Layout -
    # ===============

    cmds.formLayout(FL, e=True, af=[(refListTXT, 'top', 5), (refListTXT, 'left', 5)], ap=[(refListTXT, 'right', 5, 33)])
    cmds.formLayout(FL, e=True, af=[(refListTSL, 'bottom', 5), (refListTSL, 'left', 5)],
                  ac=[(refListTSL, 'top', 5, refListTXT)], ap=[(refListTSL, 'right', 5, 33)])
    cmds.formLayout(FL, e=True, af=[(nodeListTXT, 'top', 5)], ac=[(nodeListTXT, 'left', 5, refListTXT)],
                  ap=[(nodeListTXT, 'right', 5, 66)])
    cmds.formLayout(FL, e=True, af=[(nodeListTSL, 'bottom', 5)],
                  ac=[(nodeListTSL, 'left', 5, refListTSL), (nodeListTSL, 'top', 5, nodeListTXT)],
                  ap=[(nodeListTSL, 'right', 5, 66)])
    cmds.formLayout(FL, e=True, af=[(nodeSearchTFG, 'top', 5), (nodeSearchTFG, 'right', 5)],
                  ac=[(nodeSearchTFG, 'left', 5, nodeListTXT)])

    cmds.formLayout(FL, e=True, af=[(nodeSearchSEP, 'right', 5)],
                  ac=[(nodeSearchSEP, 'top', 5, nodeSearchTFG), (nodeSearchSEP, 'left', 5, nodeListTXT)])

    cmds.formLayout(FL, e=True, af=[(showNamespaceCBG, 'right', 5)], ac=[(showNamespaceCBG, 'top', 5, nodeSearchSEP)])
    cmds.formLayout(FL, e=True, af=[(showLongNamesCBG, 'right', 5)], ac=[(showLongNamesCBG, 'top', 5, showNamespaceCBG)])
    cmds.formLayout(FL, e=True, af=[(showSuccessEditsCBG, 'right', 5)],
                  ac=[(showSuccessEditsCBG, 'top', 5, showLongNamesCBG)])
    cmds.formLayout(FL, e=True, af=[(showFailedEditsCBG, 'right', 5)],
                  ac=[(showFailedEditsCBG, 'top', 5, showSuccessEditsCBG)])

    cmds.formLayout(FL, e=True, af=[(showDetailsSEP, 'right', 5)],
                  ac=[(showDetailsSEP, 'top', 5, showFailedEditsCBG), (showDetailsSEP, 'left', 5, nodeListTXT)])

    cmds.formLayout(FL, e=True, af=[(parentCBG, 'right', 5)], ac=[(parentCBG, 'top', 5, showDetailsSEP)])
    cmds.formLayout(FL, e=True, af=[(setAttrCBG, 'right', 5)], ac=[(setAttrCBG, 'top', 5, parentCBG)])
    cmds.formLayout(FL, e=True, af=[(addAttrCBG, 'right', 5)], ac=[(addAttrCBG, 'top', 5, setAttrCBG)])
    cmds.formLayout(FL, e=True, af=[(delAttrCBG, 'right', 5)], ac=[(delAttrCBG, 'top', 5, addAttrCBG)])
    cmds.formLayout(FL, e=True, af=[(conAttrCBG, 'right', 5)], ac=[(conAttrCBG, 'top', 5, delAttrCBG)])
    cmds.formLayout(FL, e=True, af=[(disconAttrCBG, 'right', 5)], ac=[(disconAttrCBG, 'top', 5, conAttrCBG)])

    cmds.formLayout(FL, e=True, af=[(printEditsAttrB, 'right', 5)],
                  ac=[(printEditsAttrB, 'bottom', 5, printEditsCmdsB), (printEditsAttrB, 'left', 5, nodeListTSL)])
    cmds.formLayout(FL, e=True, af=[(printEditsCmdsB, 'right', 5)],
                  ac=[(printEditsCmdsB, 'bottom', 5, removeEditsB), (printEditsCmdsB, 'left', 5, nodeListTSL)])
    cmds.formLayout(FL, e=True, af=[(removeEditsB, 'right', 5)],
                  ac=[(removeEditsB, 'bottom', 5, closeB), (removeEditsB, 'left', 5, nodeListTSL)])
    cmds.formLayout(FL, e=True, af=[(closeB, 'right', 5), (closeB, 'bottom', 5)], ac=[(closeB, 'left', 5, nodeListTSL)])

    # ===============
    # - Show Window -
    # ===============

    cmds.showWindow(window)

    # Load Reference List
    loadReferenceList()


def reloadReferenceFromUI():
    """
    Reload selected reference
    """
    refList = cmds.textScrollList('refEdits_refListTSL', q=True, si=True) or []
    for ref in refList: glTools.utils.reference.reloadReference(ref, verbose=True)


def unloadReferenceFromUI():
    """
    Unload selected reference
    """
    refList = cmds.textScrollList('refEdits_refListTSL', q=True, si=True) or []
    for ref in refList: glTools.utils.reference.unloadReference(ref, verbose=True)


def removeReferenceFromUI():
    """
    Remove selected reference
    """
    refList = cmds.textScrollList('refEdits_refListTSL', q=True, si=True) or []
    for ref in refList: glTools.utils.reference.removeReference(ref, verbose=True)
    loadReferenceList()
    loadNodeList()


def importReferenceFromUI():
    """
    Import selected reference
    """
    refList = cmds.textScrollList('refEdits_refListTSL', q=True, si=True) or []
    for ref in refList: glTools.utils.reference.importReference(ref, verbose=True)
    loadReferenceList()
    loadNodeList()


def clearSeachField():
    """
    """
    # Clear Text Field
    cmds.textFieldButtonGrp('refEdits_nodeSearchTFG', e=True, text='')
    # Reload Node List
    loadNodeList()


def selectNode():
    """
    Select node from reference edits UI.
    """
    # Get Selected Ref Node
    refNode = cmds.textScrollList('refEdits_refListTSL', q=True, si=True)
    if not refNode: return
    refNS = glTools.utils.reference.getNamespace(refNode[0]) + ':'

    # Get Selected Nodes
    nodeList = cmds.textScrollList('refEdits_nodeListTSL', q=True, si=True)
    if not nodeList: return

    # Select Nodes
    selNodes = []
    for node in nodeList:

        # Check Node
        editNode = node
        if not cmds.objExists(node): node = node.split('|')[-1]
        if not cmds.objExists(node): node = refNS + node
        if not cmds.objExists(node): raise Exception('Reference edit node "' + editNode + '" not found!')

        # Append to Selection List
        selNodes.append(node)

    # Select Node
    if selNodes: cmds.select(selNodes)


def loadReferenceList():
    """
    List all existing reference nodes to the UI textScrollList
    """
    refList = cmds.ls(type='reference')
    if 'sharedReferenceNode' in refList: refList.remove('sharedReferenceNode')
    for ref in refList: cmds.textScrollList('refEdits_refListTSL', e=True, a=ref)


def loadNodeList():
    """
    """
    # Get Selected Ref Node
    refNode = cmds.textScrollList('refEdits_refListTSL', q=True, si=True) or []

    # Check Ref Node
    if not refNode:
        # No Reference Selected, Clear Node List
        cmds.textScrollList('refEdits_nodeListTSL', e=True, ra=True)
        return

    # Get Show Details
    showNamespace = cmds.checkBoxGrp('refEdits_showNamespaceCBG', q=True, v1=True)
    showDagPath = cmds.checkBoxGrp('refEdits_showLongNamesCBG', q=True, v1=True)
    successfulEdits = cmds.checkBoxGrp('refEdits_showSuccessEditsCBG', q=True, v1=True)
    failedEdits = cmds.checkBoxGrp('refEdits_showFailedEditsCBG', q=True, v1=True)

    # Get Edit Commands
    editCmd_parent = cmds.checkBoxGrp('refEdits_parentCBG', q=True, v1=True)
    editCmd_setAttr = cmds.checkBoxGrp('refEdits_setAttrCBG', q=True, v1=True)
    editCmd_addAttr = cmds.checkBoxGrp('refEdits_addAttrCBG', q=True, v1=True)
    editCmd_delAttr = cmds.checkBoxGrp('refEdits_delAttrCBG', q=True, v1=True)
    editCmd_conAttr = cmds.checkBoxGrp('refEdits_conAttrCBG', q=True, v1=True)
    editCmd_disconAttr = cmds.checkBoxGrp('refEdits_disconAttrCBG', q=True, v1=True)
    if not (
                        editCmd_parent or editCmd_setAttr or editCmd_addAttr or editCmd_delAttr or editCmd_conAttr or editCmd_disconAttr):
        # No Edit Commands Checked, Clear Node List
        cmds.textScrollList('refEdits_nodeListTSL', e=True, ra=True)
        return

    # Get Reference Edit Nodes
    nodeList = glTools.utils.reference.getEditNodes(refNode[0],
                                                    showNamespace=showNamespace,
                                                    showDagPath=showDagPath,
                                                    successfulEdits=successfulEdits,
                                                    failedEdits=failedEdits,
                                                    parent=editCmd_parent,
                                                    setAttr=editCmd_setAttr,
                                                    addAttr=editCmd_addAttr,
                                                    deleteAttr=editCmd_delAttr,
                                                    connectAttr=editCmd_conAttr,
                                                    disconnectAttr=editCmd_disconAttr)

    # Remove Duplicates and Sort
    nodeList = list(set([i for i in nodeList])) or []
    nodeList.sort()

    # Apply Node List
    cmds.textScrollList('refEdits_nodeListTSL', e=True, ra=True)
    for node in nodeList: cmds.textScrollList('refEdits_nodeListTSL', e=True, a=node)

    # Filter List
    filterNodeList()


def filterNodeList():
    """
    """
    # Filter List
    nodeSearchStr = cmds.textFieldButtonGrp('refEdits_nodeSearchTFG', q=True, text=True)
    if not nodeSearchStr: return

    # Get Node List
    nodeList = cmds.textScrollList('refEdits_nodeListTSL', q=True, ai=True)
    if not nodeList: return

    # Check Negative Filter
    if nodeSearchStr.startswith('!'):
        if nodeSearchStr.startswith('!*'):
            nodeList = list(set([i for i in nodeList if not i.endswith(nodeSearchStr[2:])]))
        elif nodeSearchStr.endswith('*'):
            nodeList = list(set([i for i in nodeList if not i.startswith(nodeSearchStr[1:-1])]))
        else:
            nodeList = list(set([i for i in nodeList if not nodeSearchStr[1:] in i]))
    else:
        if nodeSearchStr.startswith('*'):
            nodeList = list(set([i for i in nodeList if i.endswith(nodeSearchStr[1:])]))
        elif nodeSearchStr.endswith('*'):
            nodeList = list(set([i for i in nodeList if i.startswith(nodeSearchStr[:-1])]))
        else:
            nodeList = list(set([i for i in nodeList if nodeSearchStr in i]))

    # Apply Filtered Node List
    cmds.textScrollList('refEdits_nodeListTSL', e=True, ra=True)
    for node in sorted(nodeList): cmds.textScrollList('refEdits_nodeListTSL', e=True, a=node)


def printNodeEditAttributes():
    """
    Print list of node attributes that have reference edits.
    """
    # Get Reference and Node Selection
    refList = cmds.textScrollList('refEdits_refListTSL', q=True, si=True) or []
    nodeList = cmds.textScrollList('refEdits_nodeListTSL', q=True, si=True) or []

    # Get Show Details
    showNamespace = cmds.checkBoxGrp('refEdits_showNamespaceCBG', q=True, v1=True)
    showDagPath = cmds.checkBoxGrp('refEdits_showLongNamesCBG', q=True, v1=True)
    successfulEdits = cmds.checkBoxGrp('refEdits_showSuccessEditsCBG', q=True, v1=True)
    failedEdits = cmds.checkBoxGrp('refEdits_showFailedEditsCBG', q=True, v1=True)

    # Get Edit Commands
    editCmd_parent = cmds.checkBoxGrp('refEdits_parentCBG', q=True, v1=True)
    editCmd_setAttr = cmds.checkBoxGrp('refEdits_setAttrCBG', q=True, v1=True)
    editCmd_addAttr = cmds.checkBoxGrp('refEdits_addAttrCBG', q=True, v1=True)
    editCmd_delAttr = cmds.checkBoxGrp('refEdits_delAttrCBG', q=True, v1=True)
    editCmd_conAttr = cmds.checkBoxGrp('refEdits_conAttrCBG', q=True, v1=True)
    editCmd_disconAttr = cmds.checkBoxGrp('refEdits_disconAttrCBG', q=True, v1=True)

    # Get Edit Commands
    for refNode in refList:

        # Get Reference Namespace
        ns = ''
        if showNamespace: ns = glTools.utils.reference.getNamespace(refNode) + ':'

        for node in nodeList:

            # Get Edit Attributes
            attrList = glTools.utils.reference.getEditAttrs(refNode,
                                                            node,
                                                            showNamespace=showNamespace,
                                                            showDagPath=showDagPath,
                                                            successfulEdits=successfulEdits,
                                                            failedEdits=failedEdits,
                                                            parent=editCmd_parent,
                                                            setAttr=editCmd_setAttr,
                                                            addAttr=editCmd_addAttr,
                                                            deleteAttr=editCmd_delAttr,
                                                            connectAttr=editCmd_conAttr,
                                                            disconnectAttr=editCmd_disconAttr)

            # Append Output List
            if attrList:

                # Remove Duplicates and Sort
                attrList = list(set(attrList))
                attrList.sort()

                # Print Result
                print('\n=== Edit Attributes: ' + node + ' ===\n')
                for attr in attrList: print attr


def printNodeEditCommands():
    """
    Print list of node edit commands.
    """
    # Get Reference and Node Selection
    refList = cmds.textScrollList('refEdits_refListTSL', q=True, si=True) or []
    nodeList = cmds.textScrollList('refEdits_nodeListTSL', q=True, si=True) or []

    # Get Show Details
    showNamespace = cmds.checkBoxGrp('refEdits_showNamespaceCBG', q=True, v1=True)
    showDagPath = cmds.checkBoxGrp('refEdits_showLongNamesCBG', q=True, v1=True)
    successfulEdits = cmds.checkBoxGrp('refEdits_showSuccessEditsCBG', q=True, v1=True)
    failedEdits = cmds.checkBoxGrp('refEdits_showFailedEditsCBG', q=True, v1=True)

    # Get Edit Commands
    editCmd_parent = cmds.checkBoxGrp('refEdits_parentCBG', q=True, v1=True)
    editCmd_setAttr = cmds.checkBoxGrp('refEdits_setAttrCBG', q=True, v1=True)
    editCmd_addAttr = cmds.checkBoxGrp('refEdits_addAttrCBG', q=True, v1=True)
    editCmd_delAttr = cmds.checkBoxGrp('refEdits_delAttrCBG', q=True, v1=True)
    editCmd_conAttr = cmds.checkBoxGrp('refEdits_conAttrCBG', q=True, v1=True)
    editCmd_disconAttr = cmds.checkBoxGrp('refEdits_disconAttrCBG', q=True, v1=True)

    # Get Edit Commands
    for refNode in refList:

        # Get Reference Namespace
        ns = ''
        if showNamespace: ns = glTools.utils.reference.getNamespace(refNode) + ':'

        for node in nodeList:
            cmdList = glTools.utils.reference.getEditCommands(refNode,
                                                              ns + node,
                                                              showNamespace=showNamespace,
                                                              showDagPath=showDagPath,
                                                              successfulEdits=successfulEdits,
                                                              failedEdits=failedEdits,
                                                              parent=editCmd_parent,
                                                              setAttr=editCmd_setAttr,
                                                              addAttr=editCmd_addAttr,
                                                              deleteAttr=editCmd_delAttr,
                                                              connectAttr=editCmd_conAttr,
                                                              disconnectAttr=editCmd_disconAttr)

            # Append Output List
            if cmdList:

                # Remove Duplicates and Sort
                cmdList = list(set(cmdList))

                # Print Result
                print('\n=== Edit Commands: ' + node + ' ===\n')
                for cmd in cmdList: print cmd


def removeReferenceEditsFromUI():
    """
    Remove Reference Edits
    """
    # =======================
    # - Get Details From UI -
    # =======================

    # Get Reference and Node Selection
    refList = cmds.textScrollList('refEdits_refListTSL', q=True, si=True) or []
    nodeList = cmds.textScrollList('refEdits_nodeListTSL', q=True, si=True) or []

    # Get Edit Details
    successfulEdits = cmds.checkBoxGrp('refEdits_showSuccessEditsCBG', q=True, v1=True)
    failedEdits = cmds.checkBoxGrp('refEdits_showFailedEditsCBG', q=True, v1=True)

    # Get Edit Commands
    editCmd_parent = cmds.checkBoxGrp('refEdits_parentCBG', q=True, v1=True)
    editCmd_setAttr = cmds.checkBoxGrp('refEdits_setAttrCBG', q=True, v1=True)
    editCmd_addAttr = cmds.checkBoxGrp('refEdits_addAttrCBG', q=True, v1=True)
    editCmd_delAttr = cmds.checkBoxGrp('refEdits_delAttrCBG', q=True, v1=True)
    editCmd_conAttr = cmds.checkBoxGrp('refEdits_conAttrCBG', q=True, v1=True)
    editCmd_disconAttr = cmds.checkBoxGrp('refEdits_disconAttrCBG', q=True, v1=True)

    # Get Show Namespace
    showNamespace = cmds.checkBoxGrp('refEdits_showNamespaceCBG', q=True, v1=True)

    # ==========================
    # - Remove Reference Edits -
    # ==========================

    for refNode in refList:

        # Check Reference Loaded
        refLoaded = glTools.utils.reference.isLoaded(refNode)
        if refLoaded: cmds.file(unloadReference=refNode)

        # Get Reference Namespace
        ns = ''
        if not showNamespace: ns = glTools.utils.reference.getNamespace(refNode) + ':'

        if not nodeList:
            # Remove All Reference Edits
            glTools.utils.reference.removeReferenceEdits(refNode,
                                                         node='',
                                                         successfulEdits=successfulEdits,
                                                         failedEdits=failedEdits,
                                                         parent=editCmd_parent,
                                                         setAttr=editCmd_setAttr,
                                                         addAttr=editCmd_addAttr,
                                                         deleteAttr=editCmd_delAttr,
                                                         connectAttr=editCmd_conAttr,
                                                         disconnectAttr=editCmd_disconAttr)

        for node in nodeList:
            # Remove Node Edits
            glTools.utils.reference.removeReferenceEdits(refNode,
                                                         ns + node,
                                                         successfulEdits=successfulEdits,
                                                         failedEdits=failedEdits,
                                                         parent=editCmd_parent,
                                                         setAttr=editCmd_setAttr,
                                                         addAttr=editCmd_addAttr,
                                                         deleteAttr=editCmd_delAttr,
                                                         connectAttr=editCmd_conAttr,
                                                         disconnectAttr=editCmd_disconAttr)

        # Reload Reference
        if refLoaded: cmds.file(loadReference=refNode)
