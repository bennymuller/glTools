import maya.cmds as cmds
import glTools.tools.mirrorDeformerWeights


def ui():
    """
    """
    #
    win = 'mirrorDeformerWeightsUI'
    if cmds.window(win, q=True, ex=True):
        cmds.deleteUI(win)
    win = cmds.window(win, l=win)

    FL = cmds.formLayout()
