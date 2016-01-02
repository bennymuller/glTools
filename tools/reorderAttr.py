import maya.cmds as cmds
import glTools.ui.utils
import glTools.utils.attribute


def reorderAttrUI():
    """
    """
    # Window
    window = 'reorderAttrUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Reorder Attributes')

    # Layout
    fl = cmds.formLayout(numberOfDivisions=100)

    # UI Elements
    objTFB = cmds.textFieldButtonGrp('reorderAttrTFB', label='', text='', buttonLabel='Load Selected', cw=[1, 5])
    attrTSL = cmds.textScrollList('reorderAttrTSL', allowMultiSelection=True)
    moveUpB = cmds.button(label='Move Up', c='glTools.tools.reorderAttr.reorderAttrFromUI(0)')
    moveDnB = cmds.button(label='Move Down', c='glTools.tools.reorderAttr.reorderAttrFromUI(1)')
    moveTpB = cmds.button(label='Move to Top', c='glTools.tools.reorderAttr.reorderAttrFromUI(2)')
    moveBtB = cmds.button(label='Move to Bottom', c='glTools.tools.reorderAttr.reorderAttrFromUI(3)')
    cancelB = cmds.button(label='Cancel', c='cmds.deleteUI("' + window + '")')

    # Form Layout
    cmds.formLayout(fl, e=True, af=[(objTFB, 'left', 5), (objTFB, 'top', 5), (objTFB, 'right', 5)])
    cmds.formLayout(fl, e=True, af=[(moveUpB, 'left', 5), (moveUpB, 'right', 5)], ac=[(moveUpB, 'bottom', 5, moveDnB)])
    cmds.formLayout(fl, e=True, af=[(moveDnB, 'left', 5), (moveDnB, 'right', 5)], ac=[(moveDnB, 'bottom', 5, moveTpB)])
    cmds.formLayout(fl, e=True, af=[(moveTpB, 'left', 5), (moveTpB, 'right', 5)], ac=[(moveTpB, 'bottom', 5, moveBtB)])
    cmds.formLayout(fl, e=True, af=[(moveBtB, 'left', 5), (moveBtB, 'right', 5)], ac=[(moveBtB, 'bottom', 5, cancelB)])
    cmds.formLayout(fl, e=True, af=[(cancelB, 'left', 5), (cancelB, 'right', 5), (cancelB, 'bottom', 5)])
    cmds.formLayout(fl, e=True, af=[(attrTSL, 'left', 5), (attrTSL, 'right', 5)],
                  ac=[(attrTSL, 'top', 5, objTFB), (attrTSL, 'bottom', 5, moveUpB)])

    # UI callback commands
    cmds.textFieldButtonGrp('reorderAttrTFB', e=True, bc='glTools.tools.reorderAttr.reorderAttrLoadSelected()')

    # Load selection
    sel = cmds.ls(sl=1)
    if sel: reorderAttrLoadSelected()

    # Display UI
    cmds.showWindow(window)


def reorderAttrLoadSelected():
    """
    """
    # Load Selected to Text Field
    glTools.ui.utils.loadObjectSel('reorderAttrTFB')

    # Refresh attribute list
    reorderAttrRefreshList()


def reorderAttrRefreshList(selList=[]):
    """
    """
    # Get object
    obj = cmds.textFieldButtonGrp('reorderAttrTFB', q=True, text=True)

    # Get attr list
    udAttrList = cmds.listAttr(obj, ud=True)
    cbAttrList = []
    tmpAttrList = cmds.listAttr(obj, k=True)
    if tmpAttrList: cbAttrList.extend(tmpAttrList)
    tmpAttrList = cmds.listAttr(obj, cb=True)
    if tmpAttrList: cbAttrList.extend(tmpAttrList)
    allAttrList = [i for i in udAttrList if cbAttrList.count(i)]

    # Update attribute text scroll list
    cmds.textScrollList('reorderAttrTSL', e=True, ra=True)
    for attr in allAttrList: cmds.textScrollList('reorderAttrTSL', e=True, a=attr)

    # Select list items
    selAttrList = []
    if selList: selAttrList = list(set(selList).intersection(set(allAttrList)))
    if selAttrList: cmds.textScrollList('reorderAttrTSL', e=True, si=selAttrList)


def reorderAttrFromUI(dir):
    """
    Reorder attributes based on info from the control UI
    @param dir: Direction to move attribute in current oreder
    @type dir: int
    """
    # Get UI info
    obj = cmds.textFieldButtonGrp('reorderAttrTFB', q=True, text=True)
    attrList = cmds.textScrollList('reorderAttrTSL', q=True, si=True)

    # Check object
    if not cmds.objExists(obj):
        raise Exception('Object "' + obj + '" does not exist!')

    # Check attributes
    for attr in attrList:
        if not cmds.objExists(obj + '.' + attr):
            raise Exception('Attribute "' + obj + '.' + attr + '" does not exist!')

    # Reorder Attributes
    for attr in attrList:

        if dir == 0:  # Move Up
            glTools.utils.attribute.reorder(obj + '.' + attr, 'up')
        if dir == 1:  # Move Down
            glTools.utils.attribute.reorder(obj + '.' + attr, 'down')
        if dir == 2:  # Move to Top
            glTools.utils.attribute.reorder(obj + '.' + attr, 'top')
        if dir == 3:  # Move to Bottom
            glTools.utils.attribute.reorder(obj + '.' + attr, 'bottom')

    # Refresh attribute list
    reorderAttrRefreshList(attrList)

    # Refresh UI
    channelBox = 'mainChannelBox'
    cmds.channelBox(channelBox, e=True, update=True)
