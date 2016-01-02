import maya.mel as mel
import maya.cmds as cmds
import glTools.utils.component
import glTools.utils.selection
import glTools.utils.skinCluster
import gl_globals


class UserInterupted(Exception): pass


def copyPasteWeightsUI():
    """
    CopyPaste weights tool UI
    """
    # Define Window
    win = 'copyPasteWeightsUI'
    # Check Window
    if cmds.window(win, q=True, ex=True): cmds.deleteUI(win)

    # Build Window
    cmds.window(win, t='Copy/Paste Skin Weights')

    # layout
    cmds.columnLayout()

    # Buttons
    cmds.button(w=200, l='Copy Weights', c='glTools.tools.copyPasteWeights.copyWeights()')
    cmds.button(w=200, l='Paste Weights', c='glTools.tools.copyPasteWeights.pasteWeights()')
    cmds.button(w=200, l='Average Weights', c='glTools.tools.copyPasteWeights.averageWeights()')
    cmds.button(w=200, l='Auto Average', c='glTools.tools.copyPasteWeights.autoAverageWeights()')
    cmds.button(w=200, l='Close', c=('cmds.deleteUI("' + win + '")'))

    # Show Window
    cmds.showWindow(win)


def copyWeights(tol=0.000001):
    """
    Copy weights of selected vertices
    @param tol: Minimum influence weight tolerance
    @type tol: float
    """
    # Get Component Selection
    sel = cmds.filterExpand(ex=True, sm=[28, 31, 46])
    if not sel: return
    cv = sel[0]

    # Get Geometry from Component
    geo = cmds.ls(cv, o=True)[0]

    # Get SkinCluster from Geometry
    skin = glTools.utils.skinCluster.findRelatedSkinCluster(geo)
    if not skin: raise Exception('Geometry "' + geo + '" is not attached to a valid skinCluster!')

    # Get Influence List
    joints = cmds.skinCluster(skin, q=True, inf=True)

    # Copy Weights
    wt = cmds.skinPercent(skin, cv, q=True, v=True)
    cmd = 'skinPercent'
    for jnt in joints:

        # Get Influence Weight
        wt = cmds.skinPercent(skin, cv, q=True, v=True, transform=jnt)

        # Check Weight Tolerance
        if wt < tol: continue

        # Append skinPercent Command
        cmd += (' -tv ' + jnt + ' ' + str(round(wt, 5)));

    # Finalize skinPercent Command
    cmd += ' -zri true ###'

    # Set Global Weight Value
    gl_globals.glCopyPasteWeightCmd = cmd
    print gl_globals.glCopyPasteWeightCmd


def pasteWeights(showProgress=True):
    """
    @param showProgress: Show operation progress using the main progress bar
    @type showProgress: bool
    """
    # Global Weight Value
    wt = gl_globals.glCopyPasteWeightCmd

    # Get Component Selection
    sel = cmds.filterExpand(ex=True, sm=[28, 31, 46])
    if not sel: return

    # Begin Progress Bar
    gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')
    if showProgress:
        cmds.progressBar(gMainProgressBar, e=True, bp=True, ii=True, status=('Pasting Skin Weights...'),
                       maxValue=len(sel))

    selComp = glTools.utils.selection.componentListByObject(sel)
    for objComp in selComp:

        # Get Object from Component
        geo = cmds.ls(objComp[0], o=True)[0]

        # Get SkinCluster from Geometry
        skin = glTools.utils.skinCluster.findRelatedSkinCluster(geo)
        if not skin: raise Exception('Geometry "' + geo + '" is not attached to a valid skinCluster!')
        # Disable Weight Normalization
        cmds.setAttr(skin + '.normalizeWeights', 0)

        # For Each Component
        for cv in objComp:

            # Update skinPercent Command
            cmd = wt.replace('###', skin)

            # Evaluate skinPercent Command
            try:
                mel.eval(cmd)
            # print(cmd)
            except Exception, e:
                if showProgress: cmds.progressBar(gMainProgressBar, e=True, endProgress=True)
                raise Exception(str(s))

            # Update Progress Bar
            cvLen = len(cmds.ls(cv, fl=True))
            if showProgress:
                if cmds.progressBar(gMainProgressBar, q=True, isCancelled=True):
                    cmds.progressBar(gMainProgressBar, e=True, endProgress=True)
                    raise UserInterupted('Operation cancelled by user!')
                cmds.progressBar(gMainProgressBar, e=True, step=cvLen)

        # Normalize Weights
        cmds.setAttr(skin + '.normalizeWeights', 1)
        cmds.skinPercent(skin, normalize=True)

    # End Current Progress Bar
    if showProgress: cmds.progressBar(gMainProgressBar, e=True, endProgress=True)


def averageWeights(tol=0.000001):
    """
    Average weights of selected vertices
    @param tol: Minimum influence weight tolerance
    @type tol: float
    """
    # Get Component Selection
    sel = cmds.filterExpand(ex=True, sm=[28, 31, 46])
    if not sel: return

    # Get Component Selection by Object
    sel = glTools.utils.selection.componentListByObject(sel)
    if not sel: return
    sel = sel[0]

    # Get Object from Components
    geo = cmds.ls(sel[0], o=True)[0]

    # Get SkinCluster
    skin = glTools.utils.skinCluster.findRelatedSkinCluster(geo)
    if not skin: raise Exception('Geometry "' + geo + '" is not attached to a valid skinCluster!')

    # Get Influence List
    joints = cmds.skinCluster(skin, q=True, inf=True)

    # Initialize skinPercent Command
    cmd = 'skinPercent'

    # For Each SkinCluster Influence
    for jnt in joints:

        # Initialize Average Influence Weight
        wt = 0.0

        # For each CV
        for cv in sel:
            wt += cmds.skinPercent(skin, cv, q=True, transform=jnt)

        # Average Weight
        wt /= len(joints)

        # Check Weight Tolerance
        if wt < tol: continue

        # Append to skinPercent Command
        cmd += (' -tv ' + jnt + ' ' + str(round(wt, 5)))

    # Finalize skinPercent Command
    cmd += (' -zri true ### ')

    # Return Result
    gl_globals.glCopyPasteWeightCmd = cmd
    print gl_globals.glCopyPasteWeightCmd


def autoAverageWeights():
    """
    """
    # Get Component Selection
    sel = cmds.filterExpand(ex=True, sm=[28, 31, 46])
    if not sel: return

    # For Each Vertex
    for vtx in sel:
        # Select Vert
        cmds.select(vtx)

        # Expand Selection
        mel.eval('PolySelectTraverse 1')
        cmds.select(vtx, d=True)

        # Calculate Average Weights from Neighbours
        averageWeights()
        cmds.select(vtx)
        # Paste Average Weights
        pasteWeights()


def hotkeySetup():
    """
    """
    # ====================
    # - Runtime Commands -
    # ====================

    # Copy Weights
    if mel.eval('runTimeCommand -q -ex rt_copyWeights'):
        mel.eval('runTimeCommand -e -del rt_copyWeights')
    mel.eval(
        'runTimeCommand -annotation "" -category "User" -commandLanguage "python" -command "import glTools.tools.copyPasteWeights;reload(glTools.tools.copyPasteWeights);glTools.tools.copyPasteWeights.copyWeights()" rt_copyWeights')

    # Paste Weights
    if mel.eval('runTimeCommand -q -ex rt_pasteWeights'):
        mel.eval('runTimeCommand -e -del rt_pasteWeights')
    mel.eval(
        'runTimeCommand -annotation "" -category "User" -commandLanguage "python" -command "import glTools.tools.copyPasteWeights;reload(glTools.tools.copyPasteWeights);glTools.tools.copyPasteWeights.pasteWeights()" rt_pasteWeights')

    # Average Weights
    if mel.eval('runTimeCommand -q -ex rt_averageWeights'):
        mel.eval('runTimeCommand -e -del rt_averageWeights')
    mel.eval(
        'runTimeCommand -annotation "" -category "User" -commandLanguage "python" -command "import glTools.tools.copyPasteWeights;reload(glTools.tools.copyPasteWeights);glTools.tools.copyPasteWeights.averageWeights()" rt_averageWeights')

    # Auto Average Weights
    if mel.eval('runTimeCommand -q -ex rt_autoAverageWeights'):
        mel.eval('runTimeCommand -e -del rt_autoAverageWeights')
    mel.eval(
        'runTimeCommand -annotation "" -category "User" -commandLanguage "python" -command "import glTools.tools.copyPasteWeights;reload(glTools.tools.copyPasteWeights);glTools.tools.copyPasteWeights.autoAverageWeights()" rt_autoAverageWeights')

    # ========================
    # - Create Name Commands -
    # ========================

    copyWtCmd = cmds.nameCommand('copyWeightsNameCommand',
                               ann='copyWeightsNameCommand',
                               sourceType='mel',
                               c='rt_copyWeights')

    pasteWtCmd = cmds.nameCommand('pasteWeightsNameCommand',
                                ann='pasteWeightsNameCommand',
                                sourceType='mel',
                                c='rt_pasteWeights')

    averageWtCmd = cmds.nameCommand('averageWeightsNameCommand',
                                  ann='averageWeightsNameCommand',
                                  sourceType='mel',
                                  c='rt_averageWeights')

    autoAverageWtCmd = cmds.nameCommand('autoAverageWeightsNameCommand',
                                      ann='autoAverageWeightsNameCommand',
                                      sourceType='mel',
                                      c='rt_autoAverageWeights')

    # =============================
    # - Create Hotkey Assignments -
    # =============================

    cmds.hotkey(keyShortcut='c', alt=True, name=copyWtCmd)
    cmds.hotkey(keyShortcut='v', alt=True, name=pasteWtCmd)
    cmds.hotkey(keyShortcut='x', alt=True, name=averageWtCmd)
    cmds.hotkey(keyShortcut='a', alt=True, name=autoAverageWtCmd)
