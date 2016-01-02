import maya.cmds as cmds
import glTools.ui.utils
import glTools.utils.ik
import glTools.tools.ikHandle
import glTools.tools.stretchyIkChain


class UIError(Exception): pass


# IK Handle --

def ikHandleUI():
    """
    UI for ikHandle()
    """
    # Window
    window = 'ikHandleUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Create IK Handle')
    # Layout
    FL = cmds.formLayout()
    # UI Elements
    # ---
    # Joints
    sJointTFB = cmds.textFieldButtonGrp('ikHandleStartJointTFB', label='Start Joint', text='',
                                      buttonLabel='Load Selected')
    eJointTFB = cmds.textFieldButtonGrp('ikHandleEndJointTFB', label='End Joint', text='', buttonLabel='Load Selected')
    # Prefix
    prefixTFG = cmds.textFieldGrp('ikHandlePrefixTFG', label='Prefix', text='')

    # IK Solver
    solverList = ['ikSplineSolver', 'ikSCsolver', 'ikRPsolver', 'ik2Bsolver']
    solverOMG = cmds.optionMenuGrp('ikHandleSolverOMG', label='IK Solver')
    for solver in solverList: cmds.menuItem(label=solver)
    cmds.optionMenuGrp(solverOMG, e=True, sl=3)

    # Spline IK
    splineFrameL = cmds.frameLayout('ikHandleSplineFL', l='Spline IK Options', cll=0, en=0)
    splineFormL = cmds.formLayout(numberOfDivisions=100)
    # Curve
    curveTFB = cmds.textFieldButtonGrp('ikHandleCurveTFB', label='Curve', text='', buttonLabel='Load Selected', en=0)
    offsetFSG = cmds.floatSliderGrp('ikHandleOffsetFSG', label='Offset', field=True, minValue=0.0, maxValue=1.0,
                                  fieldMinValue=0.0, fieldMaxValue=1.0, value=0, en=0)

    cmds.setParent('..')
    cmds.setParent('..')

    # Buttons
    createB = cmds.button('ikHandleCreateB', l='Create', c='glTools.ui.ik.ikHandleFromUI(False)')
    cancelB = cmds.button('ikHandleCancelB', l='Cancel', c='cmds.deleteUI("' + window + '")')

    # UI callback commands
    cmds.optionMenuGrp(solverOMG, e=True,
                     cc='cmds.frameLayout("' + splineFrameL + '",e=True,en=not(cmds.optionMenuGrp("' + solverOMG + '",q=True,sl=True)-1))')
    cmds.textFieldButtonGrp(sJointTFB, e=True,
                          bc='glTools.ui.ik.ikHandleUI_autoComplete("' + sJointTFB + '","' + eJointTFB + '","' + prefixTFG + '")')
    cmds.textFieldButtonGrp(eJointTFB, e=True, bc='glTools.ui.utils.loadTypeSel("' + eJointTFB + '",selType="joint")')
    cmds.textFieldButtonGrp(curveTFB, e=True, bc='glTools.ui.utils.loadCurveSel("' + curveTFB + '")')

    # Form Layout - MAIN
    cmds.formLayout(FL, e=True, af=[(sJointTFB, 'top', 5), (sJointTFB, 'left', 5), (sJointTFB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(eJointTFB, 'top', 5, sJointTFB)])
    cmds.formLayout(FL, e=True, af=[(eJointTFB, 'left', 5), (eJointTFB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(prefixTFG, 'top', 5, eJointTFB)])
    cmds.formLayout(FL, e=True, af=[(prefixTFG, 'left', 5), (prefixTFG, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(solverOMG, 'top', 5, prefixTFG)])
    cmds.formLayout(FL, e=True, af=[(solverOMG, 'left', 5), (solverOMG, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(splineFrameL, 'top', 5, solverOMG)])
    cmds.formLayout(FL, e=True, af=[(splineFrameL, 'left', 5), (splineFrameL, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(splineFrameL, 'bottom', 5, createB)])
    cmds.formLayout(FL, e=True, af=[(createB, 'left', 5), (createB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(createB, 'bottom', 5, cancelB)])
    cmds.formLayout(FL, e=True, af=[(cancelB, 'left', 5), (cancelB, 'right', 5), (cancelB, 'bottom', 5)])

    # Form Layout - Spline
    cmds.formLayout(splineFormL, e=True, af=[(curveTFB, 'top', 5), (curveTFB, 'left', 5), (curveTFB, 'right', 5)])
    cmds.formLayout(splineFormL, e=True, ac=[(offsetFSG, 'top', 5, curveTFB)])
    cmds.formLayout(splineFormL, e=True, af=[(offsetFSG, 'left', 5), (offsetFSG, 'right', 5)])

    # Show Window
    cmds.showWindow(window)


def ikHandleUI_autoComplete(sJointTFB, eJointTFB, prefixTFG):
    """
    """
    # Load selection to UI field
    glTools.ui.utils.loadTypeSel(sJointTFB, prefixTFG, selType="joint")

    # Get start joint and determine end joint
    sJoint = cmds.textFieldButtonGrp(sJointTFB, q=True, text=True)
    sJointChain = cmds.listRelatives(sJoint, ad=True)
    if not sJointChain: return
    eJointList = cmds.ls(sJointChain, type='joint')
    if not eJointList: return
    eJoint = str(eJointList[0])

    # Set End joint field value
    cmds.textFieldButtonGrp(eJointTFB, e=True, text=eJoint)


def ikHandleFromUI(close=False):
    """
    Execute ikHandle() from UI
    """
    # Window
    window = 'ikHandleUI'
    if not cmds.window(window, q=True, ex=1): raise UIError('IkHandle UI does not exist!!')

    # Get UI data
    startJ = cmds.textFieldButtonGrp('ikHandleStartJointTFB', q=True, text=True)
    endJ = cmds.textFieldButtonGrp('ikHandleEndJointTFB', q=True, text=True)
    pre = cmds.textFieldGrp('ikHandlePrefixTFG', q=True, text=True)
    solver = cmds.optionMenuGrp('ikHandleSolverOMG', q=True, v=True)
    curve = cmds.textFieldButtonGrp('ikHandleCurveTFB', q=True, text=True)
    offset = cmds.floatSliderGrp('ikHandleOffsetFSG', q=True, v=True)

    # Execute command
    glTools.tools.ikHandle.build(startJoint=startJ, endJoint=endJ, solver=solver, curve=curve, ikSplineOffset=offset,
                                 prefix=pre)

    # Cleanup
    if close: cmds.deleteUI(window)


# Stretchy IK Chain --

def stretchyIkChainUI():
    """
    UI for stretchyIkChain()
    """
    # Window
    window = 'stretchyIkChainUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Stretchy IK Chain')
    # Layout
    FL = cmds.formLayout()
    # UI Elements
    # ---
    # IK Handle
    handleTFB = cmds.textFieldButtonGrp('stretchyIkChainTFB', label='IK Handle', text='', buttonLabel='Load Selected')
    # Prefix
    prefixTFG = cmds.textFieldGrp('stretchyIkChainPrefixTFG', label='Prefix', text='')
    # Shrink
    shrinkCBG = cmds.checkBoxGrp('stretchyIkChainShrinkCBG', l='Shrink', ncb=1, v1=False)
    # Scale Axis
    axisList = ['X', 'Y', 'Z']
    scaleAxisOMG = cmds.optionMenuGrp('stretchyIkChainAxisOMG', label='Joint Scale Axis')
    for axis in axisList: cmds.menuItem(label=axis)
    cmds.optionMenuGrp(scaleAxisOMG, e=True, sl=1)
    # Scale Attr
    scaleAttrTFB = cmds.textFieldButtonGrp('stretchyIkChainScaleAttrTFB', label='Scale Attribute', text='',
                                         buttonLabel='Load Selected')
    # Blend
    blendCtrlTFB = cmds.textFieldButtonGrp('stretchyIkChainBlendCtrlTFB', label='Blend Control', text='',
                                         buttonLabel='Load Selected')
    blendAttrTFG = cmds.textFieldGrp('stretchyIkChainBlendAttrTFB', label='Blend Attribute', text='stretchScale')

    # Separator
    SEP = cmds.separator(height=10, style='single')

    # Buttons
    createB = cmds.button('stretchyIkChainCreateB', l='Create', c='glTools.ui.ik.stretchyIkChainFromUI(False)')
    cancelB = cmds.button('stretchyIkChainCancelB', l='Cancel', c='cmds.deleteUI("' + window + '")')

    # UI callback commands
    cmds.textFieldButtonGrp(handleTFB, e=True,
                          bc='glTools.ui.utils.loadTypeSel("' + handleTFB + '","' + prefixTFG + '",selType="ikHandle")')
    cmds.textFieldButtonGrp(blendCtrlTFB, e=True, bc='glTools.ui.utils.loadObjectSel("' + blendCtrlTFB + '")')
    cmds.textFieldButtonGrp(scaleAttrTFB, e=True, bc='glTools.ui.utils.loadChannelBoxSel("' + scaleAttrTFB + '")')

    # Form Layout - MAIN
    cmds.formLayout(FL, e=True, af=[(handleTFB, 'top', 5), (handleTFB, 'left', 5), (handleTFB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(prefixTFG, 'top', 5, handleTFB)])
    cmds.formLayout(FL, e=True, af=[(prefixTFG, 'left', 5), (prefixTFG, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(shrinkCBG, 'top', 5, prefixTFG)])
    cmds.formLayout(FL, e=True, af=[(shrinkCBG, 'left', 5), (shrinkCBG, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(scaleAxisOMG, 'top', 5, shrinkCBG)])
    cmds.formLayout(FL, e=True, af=[(scaleAxisOMG, 'left', 5), (scaleAxisOMG, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(scaleAttrTFB, 'top', 5, scaleAxisOMG)])
    cmds.formLayout(FL, e=True, af=[(scaleAttrTFB, 'left', 5), (scaleAttrTFB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(blendCtrlTFB, 'top', 5, scaleAttrTFB)])
    cmds.formLayout(FL, e=True, af=[(blendCtrlTFB, 'left', 5), (blendCtrlTFB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(blendAttrTFG, 'top', 5, blendCtrlTFB)])
    cmds.formLayout(FL, e=True, af=[(blendAttrTFG, 'left', 5), (blendAttrTFG, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(SEP, 'top', 5, blendAttrTFG)])
    cmds.formLayout(FL, e=True, af=[(SEP, 'left', 5), (SEP, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(createB, 'top', 5, SEP)])
    cmds.formLayout(FL, e=True, af=[(createB, 'left', 5), (createB, 'bottom', 5)])
    cmds.formLayout(FL, e=True, ap=[(createB, 'right', 5, 50)])
    cmds.formLayout(FL, e=True, ac=[(cancelB, 'top', 5, SEP)])
    cmds.formLayout(FL, e=True, af=[(cancelB, 'right', 5), (cancelB, 'bottom', 5)])
    cmds.formLayout(FL, e=True, ap=[(cancelB, 'left', 5, 50)])

    # Show Window
    cmds.showWindow(window)


def stretchyIkChainFromUI(close=False):
    """
    Execute stretchyIkChain() from UI
    """
    # Window
    window = 'stretchyIkChainUI'
    if not cmds.window(window, q=True, ex=1): raise UIError('StretchyIkChain UI does not exist!!')

    # Get UI data
    ik = cmds.textFieldButtonGrp('stretchyIkChainTFB', q=True, text=True)
    pre = cmds.textFieldGrp('stretchyIkChainPrefixTFG', q=True, text=True)
    shrink = cmds.checkBoxGrp('stretchyIkChainShrinkCBG', q=True, v1=True)
    scaleAxis = str.lower(str(cmds.optionMenuGrp('stretchyIkChainAxisOMG', q=True, v=True)))
    scaleAttr = cmds.textFieldButtonGrp('stretchyIkChainScaleAttrTFB', q=True, text=True)
    blendCtrl = cmds.textFieldButtonGrp('stretchyIkChainBlendCtrlTFB', q=True, text=True)
    blendAttr = cmds.textFieldGrp('stretchyIkChainBlendAttrTFB', q=True, text=True)

    # Execute command
    glTools.tools.stretchyIkChain.build(ikHandle=ik, scaleAttr=scaleAttr, scaleAxis=scaleAxis, blendControl=blendCtrl,
                                        blendAttr=blendAttr, shrink=shrink, prefix=pre)

    # Cleanup
    if close: cmds.deleteUI(window)


def stretchyIkLimbUI():
    """
    UI for stretchyIkLimb()
    """
    # Window
    window = 'stretchyIkLimbUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Stretchy IK Limb')
    # Layout
    FL = cmds.formLayout()
    # UI Elements
    # ---
    # IK Handle
    handleTFB = cmds.textFieldButtonGrp('stretchyIkLimbTFB', label='IK Handle', text='', buttonLabel='Load Selected')
    # Prefix
    prefixTFG = cmds.textFieldGrp('stretchyIkLimbPrefixTFG', label='Prefix', text='')
    # Control
    controlTFB = cmds.textFieldButtonGrp('stretchyIkLimbControlTFB', label='Control Object', text='',
                                       buttonLabel='Load Selected')
    # Scale Axis
    axisList = ['X', 'Y', 'Z']
    scaleAxisOMG = cmds.optionMenuGrp('stretchyIkLimbAxisOMG', label='Joint Scale Axis')
    for axis in axisList: cmds.menuItem(label=axis)
    cmds.optionMenuGrp(scaleAxisOMG, e=True, sl=1)
    # Scale Attr
    scaleAttrTFB = cmds.textFieldButtonGrp('stretchyIkLimbScaleAttrTFB', label='Scale Attribute', text='',
                                         buttonLabel='Load Selected')

    # Separator
    SEP = cmds.separator(height=10, style='single')

    # Buttons
    createB = cmds.button('stretchyIkLimbCreateB', l='Create', c='glTools.ui.ik.stretchyIkLimbFromUI(False)')
    cancelB = cmds.button('stretchyIkLimbCancelB', l='Cancel', c='cmds.deleteUI("' + window + '")')

    # UI callback commands
    cmds.textFieldButtonGrp(handleTFB, e=True,
                          bc='glTools.ui.utils.loadTypeSel("' + handleTFB + '","' + prefixTFG + '",selType="ikHandle")')
    cmds.textFieldButtonGrp(controlTFB, e=True, bc='glTools.ui.utils.loadObjectSel("' + controlTFB + '")')
    cmds.textFieldButtonGrp(scaleAttrTFB, e=True, bc='glTools.ui.utils.loadChannelBoxSel("' + scaleAttrTFB + '")')

    # Form Layout - MAIN
    cmds.formLayout(FL, e=True, af=[(handleTFB, 'top', 5), (handleTFB, 'left', 5), (handleTFB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(prefixTFG, 'top', 5, handleTFB)])
    cmds.formLayout(FL, e=True, af=[(prefixTFG, 'left', 5), (prefixTFG, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(controlTFB, 'top', 5, prefixTFG)])
    cmds.formLayout(FL, e=True, af=[(controlTFB, 'left', 5), (controlTFB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(scaleAxisOMG, 'top', 5, controlTFB)])
    cmds.formLayout(FL, e=True, af=[(scaleAxisOMG, 'left', 5), (scaleAxisOMG, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(scaleAttrTFB, 'top', 5, scaleAxisOMG)])
    cmds.formLayout(FL, e=True, af=[(scaleAttrTFB, 'left', 5), (scaleAttrTFB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(SEP, 'top', 5, scaleAttrTFB)])
    cmds.formLayout(FL, e=True, af=[(SEP, 'left', 5), (SEP, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(createB, 'top', 5, SEP)])
    cmds.formLayout(FL, e=True, af=[(createB, 'left', 5), (createB, 'bottom', 5)])
    cmds.formLayout(FL, e=True, ap=[(createB, 'right', 5, 50)])
    cmds.formLayout(FL, e=True, ac=[(cancelB, 'top', 5, SEP)])
    cmds.formLayout(FL, e=True, af=[(cancelB, 'right', 5), (cancelB, 'bottom', 5)])
    cmds.formLayout(FL, e=True, ap=[(cancelB, 'left', 5, 50)])

    # Show Window
    cmds.showWindow(window)


def stretchyIkLimbFromUI(close=False):
    """
    Execute stretchyIkLimb() from UI
    """
    # Window
    window = 'stretchyIkLimbUI'
    if not cmds.window(window, q=True, ex=1): raise UIError('StretchyIkChain UI does not exist!!')

    # Get UI data
    ik = cmds.textFieldButtonGrp('stretchyIkLimbTFB', q=True, text=True)
    pre = cmds.textFieldGrp('stretchyIkLimbPrefixTFG', q=True, text=True)
    ctrl = cmds.textFieldButtonGrp('stretchyIkLimbControlTFB', q=True, text=True)
    scaleAxis = str.lower(str(cmds.optionMenuGrp('stretchyIkLimbAxisOMG', q=True, v=True)))
    scaleAttr = cmds.textFieldButtonGrp('stretchyIkLimbScaleAttrTFB', q=True, text=True)

    # Execute command
    glTools.tools.stretchyIkLimb.StretchyIkLimb().build(ikHandle=ik, control=ctrl, scaleAttr=scaleAttr,
                                                        scaleAxis=scaleAxis, prefix=pre)

    # Cleanup
    if close: cmds.deleteUI(window)


def stretchyIkSplineUI():
    """
    UI for stretchyIkSpline()
    """
    # Window
    window = 'stretchyIkSplineUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Stretchy IK Spline')
    # Layout
    FL = cmds.formLayout()
    # UI Elements
    # ---
    # IK Handle
    handleTFB = cmds.textFieldButtonGrp('stretchyIkSplineTFB', label='IK Handle', text='', buttonLabel='Load Selected')
    # Prefix
    prefixTFG = cmds.textFieldGrp('stretchyIkSplinePrefixTFG', label='Prefix', text='')
    # Scale Axis
    axisList = ['X', 'Y', 'Z']
    scaleAxisOMG = cmds.optionMenuGrp('stretchyIkSplineAxisOMG', label='Joint Scale Axis')
    for axis in axisList: cmds.menuItem(label=axis)
    cmds.optionMenuGrp(scaleAxisOMG, e=True, sl=1)
    # Scale Attr
    scaleAttrTFB = cmds.textFieldButtonGrp('stretchyIkSplineScaleAttrTFB', label='Scale Attribute', text='',
                                         buttonLabel='Load Selected')
    # Blend
    blendCtrlTFB = cmds.textFieldButtonGrp('stretchyIkSplineBlendCtrlTFB', label='Blend Control', text='',
                                         buttonLabel='Load Selected')
    blendAttrTFG = cmds.textFieldGrp('stretchyIkSplineBlendAttrTFG', label='Blend Attribute', text='stretchScale')

    # Stretch Method
    methodList = ['Arc Length', 'Parametric']
    methodOMG = cmds.optionMenuGrp('stretchyIkSplineMethodOMG', label='Stretch Method')
    for method in methodList: cmds.menuItem(label=method)
    cmds.optionMenuGrp(methodOMG, e=True, sl=2)

    # Parametric Layout
    paramFrameL = cmds.frameLayout('stretchyIkSplineParamFL', l='Parametric Bounds', cll=0)
    paramFormL = cmds.formLayout(numberOfDivisions=100)

    # Min/Max Percent
    minPercentFSG = cmds.floatSliderGrp('stretchyIkSplineMinPFSG', label='Min Percent', field=True, minValue=0.0,
                                      maxValue=1.0, fieldMinValue=0.0, fieldMaxValue=1.0, value=0.0)
    maxPercentFSG = cmds.floatSliderGrp('stretchyIkSplineMaxPFSG', label='Max Percent', field=True, minValue=0.0,
                                      maxValue=1.0, fieldMinValue=0.0, fieldMaxValue=1.0, value=1.0)
    closestPointCBG = cmds.checkBoxGrp('stretchyIkSplineClosestPointCBG', l='Use Closest Point', ncb=1, v1=True)

    cmds.setParent('..')
    cmds.setParent('..')

    # Buttons
    createB = cmds.button('stretchyIkSplineCreateB', l='Create', c='glTools.ui.ik.stretchyIkSplineFromUI(False)')
    cancelB = cmds.button('stretchyIkSplineCancelB', l='Cancel', c='cmds.deleteUI("' + window + '")')

    # UI callback commands
    cmds.textFieldButtonGrp(handleTFB, e=True,
                          bc='glTools.ui.utils.loadTypeSel("' + handleTFB + '","' + prefixTFG + '",selType="ikHandle")')
    cmds.textFieldButtonGrp(scaleAttrTFB, e=True, bc='glTools.ui.utils.loadChannelBoxSel("' + scaleAttrTFB + '")')
    cmds.textFieldButtonGrp(blendCtrlTFB, e=True, bc='glTools.ui.utils.loadObjectSel("' + blendCtrlTFB + '")')
    cmds.optionMenuGrp(methodOMG, e=True,
                     cc='cmds.frameLayout("' + paramFrameL + '",e=True,en=cmds.optionMenuGrp("' + methodOMG + '",q=True,sl=True)-1)')

    # Form Layout - MAIN
    cmds.formLayout(FL, e=True, af=[(handleTFB, 'top', 5), (handleTFB, 'left', 5), (handleTFB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(prefixTFG, 'top', 5, handleTFB)])
    cmds.formLayout(FL, e=True, af=[(prefixTFG, 'left', 5), (prefixTFG, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(scaleAxisOMG, 'top', 5, prefixTFG)])
    cmds.formLayout(FL, e=True, af=[(scaleAxisOMG, 'left', 5), (scaleAxisOMG, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(scaleAttrTFB, 'top', 5, scaleAxisOMG)])
    cmds.formLayout(FL, e=True, af=[(scaleAttrTFB, 'left', 5), (scaleAttrTFB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(blendCtrlTFB, 'top', 5, scaleAttrTFB)])
    cmds.formLayout(FL, e=True, af=[(blendCtrlTFB, 'left', 5), (blendCtrlTFB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(blendAttrTFG, 'top', 5, blendCtrlTFB)])
    cmds.formLayout(FL, e=True, af=[(blendAttrTFG, 'left', 5), (blendAttrTFG, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(methodOMG, 'top', 5, blendAttrTFG)])
    cmds.formLayout(FL, e=True, af=[(methodOMG, 'left', 5), (methodOMG, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(paramFrameL, 'top', 5, methodOMG), (paramFrameL, 'bottom', 5, createB)])
    cmds.formLayout(FL, e=True, af=[(paramFrameL, 'left', 5), (paramFrameL, 'right', 5)])
    cmds.formLayout(FL, e=True, af=[(createB, 'left', 5), (createB, 'bottom', 5)])
    cmds.formLayout(FL, e=True, ap=[(createB, 'right', 5, 50)])
    cmds.formLayout(FL, e=True, af=[(cancelB, 'right', 5), (cancelB, 'bottom', 5)])
    cmds.formLayout(FL, e=True, ap=[(cancelB, 'left', 5, 50)])

    # Form Layout - Parametric
    cmds.formLayout(paramFormL, e=True,
                  af=[(minPercentFSG, 'top', 5), (minPercentFSG, 'left', 5), (minPercentFSG, 'right', 5)])
    cmds.formLayout(paramFormL, e=True, ac=[(maxPercentFSG, 'top', 5, minPercentFSG)])
    cmds.formLayout(paramFormL, e=True, af=[(maxPercentFSG, 'left', 5), (maxPercentFSG, 'right', 5)])
    cmds.formLayout(paramFormL, e=True, ac=[(closestPointCBG, 'top', 5, maxPercentFSG)])
    cmds.formLayout(paramFormL, e=True, af=[(closestPointCBG, 'left', 5), (closestPointCBG, 'right', 5)])

    # Show Window
    cmds.showWindow(window)


def stretchyIkSplineFromUI(close=False):
    """
    """
    # Window
    window = 'stretchyIkSplineUI'
    if not cmds.window(window, q=True, ex=1): raise UIError('StretchyIkSpline UI does not exist!!')

    # Get UI data
    ik = cmds.textFieldButtonGrp('stretchyIkSplineTFB', q=True, text=True)
    pre = cmds.textFieldGrp('stretchyIkSplinePrefixTFG', q=True, text=True)
    scaleAxis = str.lower(str(cmds.optionMenuGrp('stretchyIkSplineAxisOMG', q=True, v=True)))
    scaleAttr = cmds.textFieldButtonGrp('stretchyIkSplineScaleAttrTFB', q=True, text=True)
    blendCtrl = cmds.textFieldButtonGrp('stretchyIkSplineBlendCtrlTFB', q=True, text=True)
    blendAttr = cmds.textFieldGrp('stretchyIkSplineBlendAttrTFG', q=True, text=True)
    useClosestPnt = cmds.checkBoxGrp('stretchyIkSplineClosestPointCBG', q=True, v1=True)
    method = cmds.optionMenuGrp('stretchyIkSplineMethodOMG', q=True, sl=True) - 1
    minPercent = cmds.floatSliderGrp('stretchyIkSplineMinPFSG', q=True, v=True)
    maxPercent = cmds.floatSliderGrp('stretchyIkSplineMaxPFSG', q=True, v=True)

    # Execute command
    if method:  # Parametric
        glTools.tools.stretchyIkSpline.stretchyIkSpline_parametric(ikHandle=ik,
                                                                   scaleAxis=scaleAxis,
                                                                   scaleAttr=scaleAttr,
                                                                   blendControl=blendCtrl,
                                                                   blendAttr=blendAttr,
                                                                   useClosestPoint=useClosestPnt,
                                                                   minPercent=minPercent,
                                                                   maxPercent=maxPercent,
                                                                   prefix=pre)
    else:  # Arc Length
        glTools.tools.stretchyIkSpline.stretchyIkSpline_arcLength(ikHandle=ik,
                                                                  scaleAxis=scaleAxis,
                                                                  scaleAttr=scaleAttr,
                                                                  blendControl=blendCtrl,
                                                                  blendAttr=blendAttr,
                                                                  prefix=pre)

    # Cleanup
    if close: cmds.deleteUI(window)
