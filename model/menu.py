import maya.cmds as cmds
import maya.mel as mel


def create():
    """
    This generates the menu for all modelTools.
    """
    # This is a temporary hack to get maya to evaluate $gMainWindow
    gMainWindow = mel.eval('string $temp = $gMainWindow')
    if cmds.menu('modelToolsMenu', q=True, ex=True):
        cmds.deleteUI('modelToolsMenu')

    if gMainWindow:
        cmds.setParent(gMainWindow)
        cmds.menu('modelToolsMenu', label='Model Tools', tearOff=True, allowOptionBoxes=True)

        # ----------------------------------------#

        cmds.menuItem(label='Checks', subMenu=True, tearOff=True)

        cmds.menuItem(label='Run Checks',
                    command='import glTools.spotcheck.runChecks;reload(glTools.spotcheck.runChecks);glTools.spotcheck.runChecks.run(envKey="IKA_MODEL_SPOTCHECKS",checkTitle="Rig Checks",selectedNodes=False)')
        cmds.menuItem(label='Run Checks On Selected',
                    command='import glTools.spotcheck.runChecks;reload(glTools.spotcheck.runChecks);glTools.spotcheck.runChecks.run(envKey="IKA_MODEL_SPOTCHECKS",checkTitle="Rig Checks",selectedNodes=True)')

        cmds.setParent('..', menu=True)

        # ----------------------------------------#

        cmds.menuItem(divider=True)

        # GENERAL
        cmds.menuItem(allowOptionBoxes=True, label='General', subMenu=True, tearOff=True)

        cmds.menuItem(label='Align to Ground Plane',
                    command='import glTools.model.utils;reload(glTools.model.utils);[glTools.model.utils.setVerticalPlacement(i) for i in cmds.ls(sl=True)]')
        cmds.menuItem(label='Build Poly Edge Curves',
                    command='import glTools.tools.polyEdgeCurve;reload(glTools.tools.polyEdgeCurve);glTools.tools.polyEdgeCurve.buildEdgeCurvesUI()')

        cmds.setParent('..', menu=True)

        cmds.menuItem(divider=True)

        # TOOLS
        cmds.menuItem(allowOptionBoxes=True, label='Tools', subMenu=True, tearOff=True)

        cmds.menuItem(label='Slide Deformer',
                    command='import glTools.model.utils;reload(glTools.model.utils);[glTools.model.utils.slideDeformer(i) for i in cmds.ls(sl=1)]')
        cmds.menuItem(label='Strain Relaxer',
                    command='import glTools.model.utils;reload(glTools.model.utils);[glTools.model.utils.strainRelaxer(i) for i in cmds.ls(sl=1)]')
        cmds.menuItem(label='Directional Smooth',
                    command='import glTools.model.utils;reload(glTools.model.utils);[glTools.model.utils.directionalSmooth(i) for i in cmds.ls(sl=1)]')
        cmds.menuItem(label='Straighten Vertices...',
                    command='import glTools.model.straightenVerts;reload(glTools.model.straightenVerts);glTools.model.straightenVerts.straightenVertsUI()')
        cmds.menuItem(label='Even Edge Spacing...',
                    command='import glTools.model.straightenVerts;reload(glTools.model.straightenVerts);glTools.model.straightenVerts.evenEdgeSpacingUI()')
        cmds.menuItem(label='Smooth Edge Line...',
                    command='import glTools.model.straightenVerts;reload(glTools.model.straightenVerts);glTools.model.straightenVerts.smoothEdgeLineUI()')

        cmds.menuItem(allowOptionBoxes=True, label='Mirror Tools', subMenu=True, tearOff=True)

        cmds.menuItem(label='Auto Mirror',
                    command='import glTools.utils.edgeFlowMirror;reload(glTools.utils.edgeFlowMirror);glTools.utils.edgeFlowMirror.autoMirror()')
        cmds.menuItem(label='Mirror X (+ -> -)',
                    command='import glTools.utils.edgeFlowMirror;reload(glTools.utils.edgeFlowMirror);glTools.utils.edgeFlowMirror.mirrorGeo(cmds.ls(sl=True,fl=True)[0])')
        cmds.menuItem(label='Mirror X (- -> +)',
                    command='import glTools.utils.edgeFlowMirror;reload(glTools.utils.edgeFlowMirror);glTools.utils.edgeFlowMirror.mirrorGeo(cmds.ls(sl=True,fl=True)[0],posToNeg=False)')
        cmds.menuItem(label='Mirror Y (+ -> -)',
                    command='import glTools.utils.edgeFlowMirror;reload(glTools.utils.edgeFlowMirror);glTools.utils.edgeFlowMirror.mirrorGeo(cmds.ls(sl=True,fl=True)[0]),axis="y"')
        cmds.menuItem(label='Mirror Y (- -> +)',
                    command='import glTools.utils.edgeFlowMirror;reload(glTools.utils.edgeFlowMirror);glTools.utils.edgeFlowMirror.mirrorGeo(cmds.ls(sl=True,fl=True)[0],axis="y",posToNeg=False)')
        cmds.menuItem(label='Mirror Z (+ -> -)',
                    command='import glTools.utils.edgeFlowMirror;reload(glTools.utils.edgeFlowMirror);glTools.utils.edgeFlowMirror.mirrorGeo(cmds.ls(sl=True,fl=True)[0]),axis="z"')
        cmds.menuItem(label='Mirror Z (- -> +)',
                    command='import glTools.utils.edgeFlowMirror;reload(glTools.utils.edgeFlowMirror);glTools.utils.edgeFlowMirror.mirrorGeo(cmds.ls(sl=True,fl=True)[0],axis="z",posToNeg=False)')

        cmds.setParent('..', menu=True)

        cmds.menuItem(allowOptionBoxes=True, label='Align Tools', subMenu=True, tearOff=True)

        cmds.menuItem(label='Align to Best Fit',
                    command='import glTools.model.utils;reload(glTools.model.utils);glTools.model.utils.alignControlPoints(cmds.ls(sl=True,fl=True),axis="bestFitPlane",localAxis=False)')

        cmds.menuItem(label='Align (+X) Local',
                    command='import glTools.model.utils;reload(glTools.model.utils);glTools.model.utils.alignControlPoints(cmds.ls(sl=True,fl=True),axis="+x",localAxis=True)')
        cmds.menuItem(label='Align (-X) Local',
                    command='import glTools.model.utils;reload(glTools.model.utils);glTools.model.utils.alignControlPoints(cmds.ls(sl=True,fl=True),axis="-x",localAxis=True)')
        cmds.menuItem(label='Align (+Y) Local',
                    command='import glTools.model.utils;reload(glTools.model.utils);glTools.model.utils.alignControlPoints(cmds.ls(sl=True,fl=True),axis="+y",localAxis=True)')
        cmds.menuItem(label='Align (-Y) Local',
                    command='import glTools.model.utils;reload(glTools.model.utils);glTools.model.utils.alignControlPoints(cmds.ls(sl=True,fl=True),axis="-y",localAxis=True)')
        cmds.menuItem(label='Align (+Z) Local',
                    command='import glTools.model.utils;reload(glTools.model.utils);glTools.model.utils.alignControlPoints(cmds.ls(sl=True,fl=True),axis="+z",localAxis=True)')
        cmds.menuItem(label='Align (-Z) Local',
                    command='import glTools.model.utils;reload(glTools.model.utils);glTools.model.utils.alignControlPoints(cmds.ls(sl=True,fl=True),axis="-z",localAxis=True)')

        cmds.menuItem(label='Align (+X) World',
                    command='import glTools.model.utils;reload(glTools.model.utils);glTools.model.utils.alignControlPoints(cmds.ls(sl=True,fl=True),axis="+x",localAxis=False)')
        cmds.menuItem(label='Align (-X) World',
                    command='import glTools.model.utils;reload(glTools.model.utils);glTools.model.utils.alignControlPoints(cmds.ls(sl=True,fl=True),axis="-x",localAxis=False)')
        cmds.menuItem(label='Align (+Y) World',
                    command='import glTools.model.utils;reload(glTools.model.utils);glTools.model.utils.alignControlPoints(cmds.ls(sl=True,fl=True),axis="+y",localAxis=False)')
        cmds.menuItem(label='Align (-Y) World',
                    command='import glTools.model.utils;reload(glTools.model.utils);glTools.model.utils.alignControlPoints(cmds.ls(sl=True,fl=True),axis="-y",localAxis=False)')
        cmds.menuItem(label='Align (+Z) World',
                    command='import glTools.model.utils;reload(glTools.model.utils);glTools.model.utils.alignControlPoints(cmds.ls(sl=True,fl=True),axis="+z",localAxis=False)')
        cmds.menuItem(label='Align (-Z) World',
                    command='import glTools.model.utils;reload(glTools.model.utils);glTools.model.utils.alignControlPoints(cmds.ls(sl=True,fl=True),axis="-z",localAxis=False)')

        cmds.setParent('..', menu=True)

        cmds.setParent('..', menu=True)

        # ----------------------------------------#

        cmds.menuItem(divider=True)
        cmds.menuItem(label='Refresh Menu',
                    command='import glTools.model.menu;reload(glTools.model.menu);glTools.model.menu.create()')
        cmds.setParent('..')

        print 'MODEL MENU GENERATED'
