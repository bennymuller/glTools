import maya.cmds as cmds
import glTools.tools.spaces


class UserInputError(Exception): pass


def charUI():
    """
    """
    # Window
    win = 'spacesCharUI'
    if cmds.window(win, q=True, ex=True): cmds.deleteUI(win)
    win = cmds.window(win, t='Spaces - Character UI')
    # Form Layout
    spacesCharFL = cmds.formLayout(numberOfDivisions=100)

    # UI Elements
    # -
    # Character Prefix
    charTFG = cmds.textFieldGrp('spacesCharTFG', label='Character Prefix', text='', cw=[(1, 120), (2, 150)])
    # Button
    openB = cmds.button(l='Open', c='glTools.ui.spaces.charUIFromUI()')

    cmds.formLayout(spacesCharFL, e=True, af=[(charTFG, 'left', 5), (charTFG, 'top', 5), (charTFG, 'right', 5)])
    cmds.formLayout(spacesCharFL, e=True, ac=[(openB, 'top', 5, charTFG)])
    cmds.formLayout(spacesCharFL, e=True, af=[(openB, 'left', 5), (openB, 'bottom', 5), (openB, 'right', 5)])

    # Open window
    cmds.showWindow(win)


def charUIFromUI():
    """
    """
    win = 'spacesCharUI'
    if not cmds.window(win, q=True, ex=True):
        raise UserInputError('Spaces CharcterUI is not currently open!')
    char = str(cmds.textFieldGrp('spacesCharTFG', q=True, text=True))
    glTools.tools.Spaces().ui(char)


def createAddUI():
    """
    User interface for creation/addition of spaces.
    """
    # Window
    win = 'spacesAddCreateUI'
    if cmds.window(win, q=True, ex=True): cmds.deleteUI(win)
    win = cmds.window(win, t='Spaces - Create/Add UI')
    # Form Layout
    spacesFL = cmds.formLayout(numberOfDivisions=100)

    # UI Elements
    # -
    # Text Field Grps
    controlTFG = cmds.textFieldGrp('spacesControlTFG', label='Control', text='', cw=[(1, 80), (2, 150)])
    controlTagTFG = cmds.textFieldGrp('spacesControlTagTFG', label='Control Tag', text='', cw=[(1, 80), (2, 150)])
    targetTagTFG = cmds.textFieldGrp('spacesTargetTagTFG', label='Target Tag:', text='', cw=[(1, 85), (2, 150)],
                                   cc='glTools.ui.spaces.addTargetTagToList()')
    # Text Scroll List
    targetTSL = cmds.textScrollList('spacesTargetTSL', w=120, numberOfRows=8, allowMultiSelection=False,
                                  dkc='glTools.ui.spaces.removeFromList()', sc='glTools.ui.spaces.updateTagField()')
    # Target List Text
    targetListTXT = cmds.text(l='Target List:', al='left')
    # Create Button
    createBTN = cmds.button(l='Create / Add', c='glTools.ui.spaces.createAddFromUI()')
    # Separator
    controlSEP = cmds.separator(h=5, style='single')

    # Form Layout - MAIM
    # -
    # controlTFG
    cmds.formLayout(spacesFL, e=True, af=[(controlTFG, 'left', 5), (controlTFG, 'top', 5)])
    cmds.formLayout(spacesFL, e=True, ap=[(controlTFG, 'right', 5, 50)])

    # controlTagTFG
    cmds.formLayout(spacesFL, e=True, af=[(controlTagTFG, 'right', 5), (controlTagTFG, 'top', 5)])
    cmds.formLayout(spacesFL, e=True, ap=[(controlTagTFG, 'left', 5, 50)])

    # controlSEP
    cmds.formLayout(spacesFL, e=True, af=[(controlSEP, 'left', 5), (controlSEP, 'right', 5)])
    cmds.formLayout(spacesFL, e=True, ac=[(controlSEP, 'top', 5, controlTFG)])

    # targetListTXT
    cmds.formLayout(spacesFL, e=True, af=[(targetListTXT, 'left', 5)])
    cmds.formLayout(spacesFL, e=True, ac=[(targetListTXT, 'top', 5, controlSEP)])
    cmds.formLayout(spacesFL, e=True, ap=[(targetListTXT, 'right', 5, 50)])

    # targetTSL
    cmds.formLayout(spacesFL, e=True, af=[(targetTSL, 'left', 5), (targetTSL, 'bottom', 5)])
    cmds.formLayout(spacesFL, e=True, ap=[(targetTSL, 'right', 5, 50)])
    cmds.formLayout(spacesFL, e=True, ac=[(targetTSL, 'top', 5, targetListTXT)])

    # targetTagTFG
    cmds.formLayout(spacesFL, e=True, af=[(targetTagTFG, 'right', 5)])
    cmds.formLayout(spacesFL, e=True, ap=[(targetTagTFG, 'left', 5, 50), (targetTagTFG, 'top', 5, 50)])

    # createBTN
    cmds.formLayout(spacesFL, e=True, af=[(createBTN, 'bottom', 5), (createBTN, 'right', 5)])
    cmds.formLayout(spacesFL, e=True, ap=[(createBTN, 'left', 5, 66)])

    # Poup menus
    targetListPUM = cmds.popupMenu(parent=targetTSL)
    cmds.menuItem('Add selected objects', c='glTools.ui.spaces.addSelectedToList()')
    cmds.menuItem('Remove Highlighted objects', c='glTools.ui.spaces.removeFromList()')

    controlPUM = cmds.popupMenu(parent=controlTFG)
    cmds.menuItem('Get selected object', c='glTools.ui.spaces.getControlNameFromSel()')

    # Open window
    cmds.showWindow(win)


def createAddFromUI():
    """
    Wrapper method for creation/addition of spaces. Run from the creation UI.
    """
    testCreateAddUI()
    ctrl = cmds.textFieldGrp('spacesControlTFG', q=True, text=True)
    nameTag = cmds.textFieldGrp('spacesControlTagTFG', q=True, text=True)
    targetList = cmds.textScrollList('spacesTargetTSL', q=True, ai=True)
    targetNameList = []
    targetTagList = []
    for target in targetList:
        if not target.count('::'):
            targetNameList.append(target)
            targetTagList.append(target)
        else:
            targetNameList.append(target.split('::')[0])
            targetTagList.append(target.split('::')[1])
    glTools.tools.spaces.Spaces().create(ctrl, targetNameList, targetTagList, nameTag)


def testCreateAddUI():
    """
    Test if Spaces Create/Add UI is open.
    """
    win = 'spacesAddCreateUI'
    if not cmds.window(win, q=True, ex=True):
        raise UserInputError('Spaces Create/AddUI is not currently open!')


def getControlNameFromSel():
    """
    Set control textField value to the name of the forst selected object
    """
    # Check UI
    testCreateAddUI()
    selection = cmds.ls(sl=True, type=['transform', 'joint'])
    if not selection:
        return
    else:
        cmds.textFieldGrp('spacesControlTFG', e=True, text=str(selection[0]))


def addSelectedToList():
    """
    Add selected transform names to the spaces target text scroll list.
    """
    # Check UI
    testCreateAddUI()
    currentTargetList = cmds.textScrollList('spacesTargetTSL', q=True, ai=True)
    for obj in cmds.ls(sl=True, type=['transform', 'joint']):
        if type(currentTargetList) == list:
            if currentTargetList.count(obj): continue
        # Add target to list
        cmds.textScrollList('spacesTargetTSL', e=True, a=obj)


def removeFromList():
    """
    Remove hilighted transform names from the spaces target text scroll list.
    """
    # Check UI
    testCreateAddUI()
    currentTargetList = cmds.textScrollList('spacesTargetTSL', q=True, ai=True)
    selectedTargets = cmds.textScrollList('spacesTargetTSL', q=True, si=True)
    for obj in selectedTargets:
        itemIndex = currentTargetList.index(obj)
        cmds.textScrollList('spacesTargetTSL', e=True, rii=itemIndex + 1)


def addTargetTagToList():
    """
    Add a tag string value to the selected target in the spaces target text scroll list.
    """
    # Check UI
    testCreateAddUI()
    tag = str(cmds.textFieldGrp('spacesTargetTagTFG', q=True, text=True))
    if not len(tag): return
    targetName = cmds.textScrollList('spacesTargetTSL', q=True, si=True)
    targetIndex = cmds.textScrollList('spacesTargetTSL', q=True, sii=True)
    if not targetName or not targetIndex:
        print('Select a target from the target list to add a tag to!!')
        return
    cmds.textScrollList('spacesTargetTSL', e=True, rii=targetIndex)
    cmds.textScrollList('spacesTargetTSL', e=True, ap=(targetIndex[0], targetName[0] + '::' + tag))


def updateTagField():
    """
    Update the target tag textField based on the value of the selected entry in the spaces target text scroll list.
    """
    # Check UI
    testCreateAddUI()
    targetName = cmds.textScrollList('spacesTargetTSL', q=True, si=True)
    if not targetName: return
    if not targetName[0].count('::'):
        cmds.textFieldGrp('spacesTargetTagTFG', e=True, text='')
    else:
        cmds.textFieldGrp('spacesTargetTagTFG', e=True, text=targetName[0].split('::')[1])
