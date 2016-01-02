import maya.cmds as cmds
import glTools.tools.faceForward
import glTools.ui.utils


class UserInputError(Exception): pass


def faceForwardUI():
    """
    """
    # Window
    win = 'faceForwardUI'
    if cmds.window(win, q=True, ex=True): cmds.deleteUI(win)
    win = cmds.window(win, t='Face Forward')

    # Layout
    formLayout = cmds.formLayout(numberOfDivisions=100)

    # Transform
    transformTFB = cmds.textFieldButtonGrp('faceForwardTransformTFB', label='Transform', text='',
                                         buttonLabel='Load Selected')

    # Axis'
    axisList = ['X', 'Y', 'Z', '-X', '-Y', '-Z']
    aimOMG = cmds.optionMenuGrp('faceForwardAimOMG', label='Aim Axis')
    for axis in axisList: cmds.menuItem(label=axis)
    upOMG = cmds.optionMenuGrp('faceForwardUpOMG', label='Up Axis')
    for axis in axisList: cmds.menuItem(label=axis)

    # Up Vector
    upVecFFG = cmds.floatFieldGrp('faceForwardUpVecFFG', label='Up Vector', numberOfFields=3, value1=0.0, value2=1.0,
                                value3=0.0)
    upVecTypeOMG = cmds.optionMenuGrp('faceForwardUpVecTypeOMG', label='Up Vector Type')
    for method in ['Current', 'Vector', 'Object', 'ObjectUp']: cmds.menuItem(label=method)
    upVecObjTFB = cmds.textFieldButtonGrp('faceForwardUpVecObjTFB', label='Up Vector Object', text='',
                                        buttonLabel='Load Selected')

    # Previous Frame
    prevFrameCBG = cmds.checkBoxGrp('faceForwardPrevFrameCBG', label='Prev Frame Velocity', numberOfCheckBoxes=1)
    # Key
    keyframeCBG = cmds.checkBoxGrp('faceForwardKeyCBG', label='Set Keyframe', numberOfCheckBoxes=1)

    # Buttons
    faceForwardB = cmds.button(label='Face Forward', c='glTools.ui.faceForward.faceForwardFromUI()')
    cancelB = cmds.button(label='Cancel', c='cmds.deleteUI("' + win + '")')

    # UI Callbacks
    cmds.textFieldButtonGrp(transformTFB, e=True,
                          bc='glTools.ui.utils.loadTypeSel("' + transformTFB + '","","transform")')
    cmds.textFieldButtonGrp(upVecObjTFB, e=True, bc='glTools.ui.utils.loadTypeSel("' + upVecObjTFB + '","","transform")')

    # Form Layout - MAIN
    cmds.formLayout(formLayout, e=True,
                  af=[(transformTFB, 'left', 5), (transformTFB, 'top', 5), (transformTFB, 'right', 5)])
    cmds.formLayout(formLayout, e=True, af=[(aimOMG, 'left', 5), (aimOMG, 'right', 5)])
    cmds.formLayout(formLayout, e=True, ac=[(aimOMG, 'top', 5, transformTFB)])
    cmds.formLayout(formLayout, e=True, af=[(upOMG, 'left', 5), (upOMG, 'right', 5)])
    cmds.formLayout(formLayout, e=True, ac=[(upOMG, 'top', 5, aimOMG)])
    cmds.formLayout(formLayout, e=True, af=[(upVecFFG, 'left', 5), (upVecFFG, 'right', 5)])
    cmds.formLayout(formLayout, e=True, ac=[(upVecFFG, 'top', 5, upOMG)])
    cmds.formLayout(formLayout, e=True, af=[(upVecTypeOMG, 'left', 5), (upVecTypeOMG, 'right', 5)])
    cmds.formLayout(formLayout, e=True, ac=[(upVecTypeOMG, 'top', 5, upVecFFG)])
    cmds.formLayout(formLayout, e=True, af=[(upVecObjTFB, 'left', 5), (upVecObjTFB, 'right', 5)])
    cmds.formLayout(formLayout, e=True, ac=[(upVecObjTFB, 'top', 5, upVecTypeOMG)])
    cmds.formLayout(formLayout, e=True, af=[(prevFrameCBG, 'left', 5), (prevFrameCBG, 'right', 5)])
    cmds.formLayout(formLayout, e=True, ac=[(prevFrameCBG, 'top', 5, upVecObjTFB)])
    cmds.formLayout(formLayout, e=True, af=[(keyframeCBG, 'left', 5), (keyframeCBG, 'right', 5)])
    cmds.formLayout(formLayout, e=True, ac=[(keyframeCBG, 'top', 5, prevFrameCBG)])

    cmds.formLayout(formLayout, e=True, af=[(faceForwardB, 'right', 5), (faceForwardB, 'bottom', 5)])
    cmds.formLayout(formLayout, e=True, ac=[(faceForwardB, 'top', 5, keyframeCBG)])
    cmds.formLayout(formLayout, e=True, ap=[(faceForwardB, 'left', 5, 50)])

    cmds.formLayout(formLayout, e=True, af=[(cancelB, 'left', 5), (cancelB, 'bottom', 5)])
    cmds.formLayout(formLayout, e=True, ac=[(cancelB, 'top', 5, keyframeCBG)])
    cmds.formLayout(formLayout, e=True, ap=[(cancelB, 'right', 5, 50)])

    # Show Window
    cmds.showWindow(win)


def faceForwardFromUI():
    """
    """
    pass


def faceForwardAnimUI():
    """
    """
    # Window
    win = 'faceForwardAnimUI'
    if cmds.window(win, q=True, ex=True): cmds.deleteUI(win)
    win = cmds.window(win, t='Face Forward Anim')

    # Layout
    formLayout = cmds.formLayout(numberOfDivisions=100)

    # Transform
    transformTFB = cmds.textFieldButtonGrp('faceForwardAnimTransformTFB', label='Transform', text='',
                                         buttonLabel='Load Selected')

    # Axis'
    axisList = ['X', 'Y', 'Z', '-X', '-Y', '-Z']
    aimOMG = cmds.optionMenuGrp('faceForwardAnimAimOMG', label='Aim Axis')
    for axis in axisList: cmds.menuItem(label=axis)
    upOMG = cmds.optionMenuGrp('faceForwardAnimUpOMG', label='Up Axis')
    for axis in axisList: cmds.menuItem(label=axis)

    # Up Vector
    upVecFFG = cmds.floatFieldGrp('faceForwardAnimUpVecFFG', label='Up Vector', numberOfFields=3, value1=0.0, value2=1.0,
                                value3=0.0)
    upVecTypeOMG = cmds.optionMenuGrp('faceForwardAnimUpVecTypeOMG', label='Up Vector Type')
    for method in ['Current', 'Vector', 'Object', 'ObjectUp']: cmds.menuItem(label=method)
    upVecObjTFB = cmds.textFieldButtonGrp('faceForwardAnimUpVecObjTFB', label='Up Vector Object', text='',
                                        buttonLabel='Load Selected')

    # Start / End Frame
    rangeFFG = cmds.floatFieldGrp('faceForwardAnimRangeFFG', label='Start/End Frame', numberOfFields=2, value1=-1.0,
                                value2=-1.0)

    # Samples
    samplesIFG = cmds.intFieldGrp('faceForwardAnimSampleIFG', label='Samples', numberOfFields=1)

    # Previous Frame
    prevFrameCBG = cmds.checkBoxGrp('faceForwardAnimPrevFrameCBG', label='Prev Frame Velocity', numberOfCheckBoxes=1)

    # Buttons
    faceForwardAnimB = cmds.button(label='Face Forward', c='glTools.ui.faceForward.faceForwardAnimFromUI()')
    cancelB = cmds.button(label='Cancel', c='cmds.deleteUI("' + win + '")')

    # UI Callbacks
    cmds.textFieldButtonGrp(transformTFB, e=True,
                          bc='glTools.ui.utils.loadTypeSel("' + transformTFB + '","","transform")')
    cmds.textFieldButtonGrp(upVecObjTFB, e=True, bc='glTools.ui.utils.loadTypeSel("' + upVecObjTFB + '","","transform")')

    # Form Layout - MAIN
    cmds.formLayout(formLayout, e=True,
                  af=[(transformTFB, 'left', 5), (transformTFB, 'top', 5), (transformTFB, 'right', 5)])
    cmds.formLayout(formLayout, e=True, af=[(aimOMG, 'left', 5), (aimOMG, 'right', 5)])
    cmds.formLayout(formLayout, e=True, ac=[(aimOMG, 'top', 5, transformTFB)])
    cmds.formLayout(formLayout, e=True, af=[(upOMG, 'left', 5), (upOMG, 'right', 5)])
    cmds.formLayout(formLayout, e=True, ac=[(upOMG, 'top', 5, aimOMG)])
    cmds.formLayout(formLayout, e=True, af=[(upVecFFG, 'left', 5), (upVecFFG, 'right', 5)])
    cmds.formLayout(formLayout, e=True, ac=[(upVecFFG, 'top', 5, upOMG)])
    cmds.formLayout(formLayout, e=True, af=[(upVecTypeOMG, 'left', 5), (upVecTypeOMG, 'right', 5)])
    cmds.formLayout(formLayout, e=True, ac=[(upVecTypeOMG, 'top', 5, upVecFFG)])
    cmds.formLayout(formLayout, e=True, af=[(upVecObjTFB, 'left', 5), (upVecObjTFB, 'right', 5)])
    cmds.formLayout(formLayout, e=True, ac=[(upVecObjTFB, 'top', 5, upVecTypeOMG)])
    cmds.formLayout(formLayout, e=True, af=[(rangeFFG, 'left', 5), (rangeFFG, 'right', 5)])
    cmds.formLayout(formLayout, e=True, ac=[(rangeFFG, 'top', 5, upVecObjTFB)])
    cmds.formLayout(formLayout, e=True, af=[(samplesIFG, 'left', 5), (samplesIFG, 'right', 5)])
    cmds.formLayout(formLayout, e=True, ac=[(samplesIFG, 'top', 5, rangeFFG)])
    cmds.formLayout(formLayout, e=True, af=[(prevFrameCBG, 'left', 5), (prevFrameCBG, 'right', 5)])
    cmds.formLayout(formLayout, e=True, ac=[(prevFrameCBG, 'top', 5, samplesIFG)])

    cmds.formLayout(formLayout, e=True, af=[(faceForwardAnimB, 'right', 5), (faceForwardAnimB, 'bottom', 5)])
    cmds.formLayout(formLayout, e=True, ac=[(faceForwardAnimB, 'top', 5, prevFrameCBG)])
    cmds.formLayout(formLayout, e=True, ap=[(faceForwardAnimB, 'left', 5, 50)])

    cmds.formLayout(formLayout, e=True, af=[(cancelB, 'left', 5), (cancelB, 'bottom', 5)])
    cmds.formLayout(formLayout, e=True, ac=[(cancelB, 'top', 5, prevFrameCBG)])
    cmds.formLayout(formLayout, e=True, ap=[(cancelB, 'right', 5, 50)])

    # Show Window
    cmds.showWindow(win)


def faceForwardAnimFromUI():
    """
    """
    pass
