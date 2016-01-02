import maya.cmds as cmds
import glTools.utils.skinCluster


class UserInputError(Exception): pass


def makeRelativeUI():
    """
    User Interface for skinCluster.makeRelative()
    """
    # Window
    win = 'makeRelativeUI'
    if cmds.window(win, q=True, ex=True): cmds.deleteUI(win)
    win = cmds.window(win, t='SkinCluster - Make Relative')
    # Form Layout
    makeRelativeFL = cmds.formLayout(numberOfDivisions=100)

    # SkinCluster option menu
    skinClusterOMG = cmds.optionMenuGrp('makeRelativeSkinClusterOMG', label='SkinCluster')
    for skin in cmds.ls(type='skinCluster'): cmds.menuItem(label=skin)

    # Relative To TextField
    makeRelativeTFB = cmds.textFieldButtonGrp('makeRelativeToTFB', label='RelativeTo', text='',
                                            buttonLabel='Load Selected')

    # Button
    makeRelativeBTN = cmds.button(l='Make Relative', c='glTools.ui.skinCluster.makeRelativeFromUI()')

    # UI Callbacks
    cmds.textFieldButtonGrp(makeRelativeTFB, e=True,
                          bc='glTools.ui.utils.loadTypeSel("' + makeRelativeTFB + '","transform")')

    # Form Layout - MAIN
    cmds.formLayout(makeRelativeFL, e=True,
                  af=[(skinClusterOMG, 'left', 5), (skinClusterOMG, 'top', 5), (skinClusterOMG, 'right', 5)])
    cmds.formLayout(makeRelativeFL, e=True, af=[(makeRelativeTFB, 'left', 5), (makeRelativeTFB, 'right', 5)])
    cmds.formLayout(makeRelativeFL, e=True, ac=[(makeRelativeTFB, 'top', 5, skinClusterOMG)])
    cmds.formLayout(makeRelativeFL, e=True,
                  af=[(makeRelativeBTN, 'left', 5), (makeRelativeBTN, 'right', 5), (makeRelativeBTN, 'bottom', 5)])
    cmds.formLayout(makeRelativeFL, e=True, ac=[(makeRelativeBTN, 'top', 5, makeRelativeTFB)])

    # Open window
    cmds.showWindow(win)


def makeRelativeFromUI():
    """
    Execute makeRelative from the UI
    """
    # Window
    win = 'makeRelativeUI'
    if not cmds.window(win, q=True, ex=True):
        raise UserInputError('Make Relative UI is not currently open!!')
    # Get UI values
    skinCluster = cmds.optionMenuGrp('makeRelativeSkinClusterOMG', q=True, v=True)
    relativeTo = cmds.textFieldButtonGrp('makeRelativeToTFB', q=True, text=True)
    # Check UI values
    if not cmds.objExists(skinCluster):
        raise UserInputError('SkinCluster "' + skinCluster + '" does not exist!!')
    if not cmds.objExists(relativeTo):
        raise UserInputError('Object "' + relativeTo + '" does not exist!!')
    # Make Relative
    glTools.utils.skinCluster.makeRelative(skinCluster, relativeTo)


def resetFromUI():
    """
    Execute skinCluster.reset() from the UI
    """
    # Get Selection
    sel = cmds.ls(sl=True, type=['transform', 'mesh', 'nurbsSurface', 'nurbsCurve'])
    # Reset skinCluster
    for item in sel:
        try:
            glTools.utils.skinCluster.reset(item)
        except:
            pass


def cleanFromUI():
    """
    Execute skinCluster.reset() from the UI
    """
    # Get Selection
    sel = cmds.ls(sl=True, type=['transform', 'mesh', 'nurbsSurface', 'nurbsCurve'])
    # Reset skinCluster
    for item in sel:
        skinCluster = glTools.utils.skinCluster.findRelatedSkinCluster(item)
        try:
            glTools.utils.skinCluster.clean(skinCluster)
        except:
            pass
