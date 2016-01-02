import maya.cmds as cmds
import glTools.utils.base
import glTools.utils.stringUtils


class UIError(Exception):
    pass


def jointPerVertex(ptList, orientSurface='', prefix='', suffix='jnt'):
    """
    """
    # Generate position list from input point
    posList = []
    for pt in ptList: posList.append(glTools.utils.base.getPosition(pt))

    # Create joints
    jntList = []
    for i in range(len(posList)):

        # Clear selection
        cmds.select(cl=1)

        # Get string index
        strInd = glTools.utils.stringUtils.stringIndex(i + 1, 2)

        # Create joint
        jnt = cmds.joint(n=prefix + '_' + strInd + '_' + suffix)
        # Position joint
        cmds.move(posList[i][0], posList[i][1], posList[i][2], jnt, ws=True, a=True)

        # Orient joint
        if cmds.objExists(orientSurface): cmds.delete(cmds.normalConstraint(orientSurface, jnt))

        # Append return list
        jntList.append(jnt)

    # Return Result
    return jntList


def jointPerVertexUI():
    """
    UI for jointPerVertex()
    """
    # Window
    win = 'jntPerVtxUI'
    if cmds.window(win, q=True, ex=1): cmds.deleteUI(win)
    win = cmds.window(win, t='Create Joint Per Vertex')

    # Layout
    cl = cmds.columnLayout()

    # UI Elements
    prefixTFG = cmds.textFieldGrp('jntPerVtx_prefixTFG', label='Prefix', text='')
    suffixTFG = cmds.textFieldGrp('jntPerVtx_suffixTFG', label='Suffix', text='jnt')
    oriSurfaceTFB = cmds.textFieldButtonGrp('jntPerVtx_oriSurfaceTFB', label='Orient Surface', text='',
                                          buttonLabel='Load Selected')

    # Buttons
    createB = cmds.button('jntPerVtx_createB', l='Create', c='glTools.tools.jointPerVertex.jointPerVertexFromUI(False)')
    cancelB = cmds.button('jntPerVtx_cancelB', l='Cancel', c='cmds.deleteUI("' + win + '")')

    # UI callbacks
    cmds.textFieldButtonGrp(oriSurfaceTFB, e=True, bc='glTools.ui.utils.loadObjectSel("' + oriSurfaceTFB + '","")')

    # Show Window
    cmds.showWindow(win)


def jointPerVertexFromUI(close=False):
    """
    Execute jointPerVertex() from UI
    """
    # Window
    win = 'jntPerVtxUI'
    if not cmds.window(win, q=True, ex=1): raise UIError('jointPerVertex UI does not exist!!')

    # Get UI data
    pre = cmds.textFieldGrp('jntPerVtx_prefixTFG', q=True, text=True)
    suf = cmds.textFieldGrp('jntPerVtx_suffixTFG', q=True, text=True)
    oriSurface = cmds.textFieldButtonGrp('jntPerVtx_oriSurfaceTFB', q=True, text=True)

    # Execute command
    ptList = cmds.ls(sl=1, fl=True)
    jointPerVertex(ptList, orientSurface=oriSurface, prefix=pre, suffix=suf)

    # Cleanup
    if close: cmds.deleteUI(win)
