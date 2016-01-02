import maya.cmds as cmds
import glTools.ui.utils
import glTools.utils.attach
import glTools.utils.curve
import glTools.tools.createAlongCurve
import glTools.utils.transform


class UserInputError(Exception): pass


class UIError(Exception): pass


# Locator Curve --

def locatorCurveUI():
    """
    UI for locatorCurve()
    """
    # Window
    window = 'locatorCurveUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Locator Curve')
    # Layout
    cl = cmds.columnLayout()
    # UI Elements
    # ---
    # Curve
    curveTFB = cmds.textFieldButtonGrp('locatorCurveTFB', label='Source Curve', text='', buttonLabel='Load Selected')
    # Prefix
    prefixTFG = cmds.textFieldGrp('locatorCurvePrefixTFG', label='Prefix', text='')
    # Scale
    scaleFSG = cmds.floatSliderGrp('locatorCurveScaleFSG', label='Locator Scale', field=True, minValue=0.0, maxValue=1.0,
                                 fieldMinValue=0.0, fieldMaxValue=10.0, value=0.05, pre=3)
    # Edit Points
    editPointCBG = cmds.checkBoxGrp('locatorCurveEditPointCBG', numberOfCheckBoxes=1, label='Use Edit Points', v1=False)
    # Buttons
    createB = cmds.button('locatorCurveCreateB', l='Create', c='glTools.ui.curve.locatorCurveFromUI(False)')
    cancelB = cmds.button('locatorCurveCancelB', l='Cancel', c='cmds.deleteUI("' + window + '")')

    # TFB commands
    cmds.textFieldButtonGrp(curveTFB, e=True, bc='glTools.ui.utils.loadCurveSel("' + curveTFB + '","' + prefixTFG + '")')

    # Show Window
    cmds.showWindow(window)


def locatorCurveFromUI(close=False):
    """
    Execute locatorCurve() from UI
    """
    # Window
    window = 'locatorCurveUI'
    if not cmds.window(window, q=True, ex=1): raise UIError('LocatorCurve UI does not exist!!')
    # Get UI data
    curve = cmds.textFieldGrp('locatorCurveTFB', q=True, text=True)
    prefix = cmds.textFieldGrp('locatorCurvePrefixTFG', q=True, text=True)
    scale = cmds.floatSliderGrp('locatorCurveScaleFSG', q=True, v=True)
    editPoints = cmds.checkBoxGrp('locatorCurveEditPointCBG', q=True, v1=True)
    # Check curve
    if not glTools.utils.curve.isCurve(curve):
        raise UserInputError('Object "' + curve + '" is not a valid nurbs curve!!')
    # Execute
    if editPoints:
        glTools.utils.curve.locatorEpCurve(curve=curve, locatorScale=scale, prefix=prefix)
    else:
        glTools.utils.curve.locatorCurve(curve=curve, locatorScale=scale, prefix=prefix)
    # Cleanup
    if close: cmds.deleteUI(window)


# Attach to Curve --

def attachToCurveUI():
    """
    UI for attachToCurve()
    """
    # Window
    window = 'attachToCurveUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Attach To Curve')
    # Layout
    cl = cmds.columnLayout()
    # UI Elements
    # ---
    # Curve
    curveTFB = cmds.textFieldButtonGrp('attachToCurveTFB', label='Target Curve', text='', buttonLabel='Load Selected')
    # Transform
    transformTFB = cmds.textFieldButtonGrp('attachToCurveTransformTFB', label='Attach Transform', text='',
                                         buttonLabel='Load Selected')
    # Prefix
    prefixTFG = cmds.textFieldGrp('attachToCurvePrefixTFG', label='Prefix', text='')
    # Closest Point
    closestPointCBG = cmds.checkBoxGrp('attachToCurveClosestPointCBG', numberOfCheckBoxes=1, label='Use Closest Point',
                                     v1=False)
    # Parameter
    parameterFSG = cmds.floatSliderGrp('attachToCurveParamFSG', label='Parameter', field=True, minValue=0.0, maxValue=1.0,
                                     fieldMinValue=0.0, fieldMaxValue=10.0, value=0.05, pre=3)
    # Parameter Attribute
    paramAttrTFG = cmds.textFieldGrp('attachToCurveParamAttrTFG', label='Parameter Attribute', text='param')
    # Orient
    orientCBG = cmds.checkBoxGrp('attachToCurveOrientCBG', label='Orient', numberOfCheckBoxes=1, v1=True)
    # Up Vector
    upVectorFFG = cmds.floatFieldGrp('attachToCurveUpVecFFG', label='UpVector', nf=3, v1=0, v2=1, v3=0)
    upVectorObjectTFB = cmds.textFieldButtonGrp('attachToCurveUpVecObjTFG', label='WorldUpObject', text='',
                                              buttonLabel='Load Selected')
    # Buttons
    createB = cmds.button('attachToCurveCreateB', l='Create', c='glTools.ui.curve.attachToCurveFromUI(False)')
    cancelB = cmds.button('attachToCurveCancelB', l='Cancel', c='cmds.deleteUI("' + window + '")')

    # UI callback commands
    cmds.textFieldButtonGrp(curveTFB, e=True, bc='glTools.ui.utils.loadCurveSel("' + curveTFB + '")')
    cmds.textFieldButtonGrp(transformTFB, e=True,
                          bc='glTools.ui.utils.loadObjectSel("' + transformTFB + '","' + prefixTFG + '")')
    cmds.textFieldButtonGrp(upVectorObjectTFB, e=True, bc='glTools.ui.utils.loadObjectSel("' + upVectorObjectTFB + '")')
    cmds.checkBoxGrp(closestPointCBG, e=True,
                   cc='glTools.ui.utils.checkBoxToggleControl("' + closestPointCBG + '","' + parameterFSG + '",invert=True)')

    # Show Window
    cmds.showWindow(window)


def attachToCurveFromUI(close=False):
    """
    Execute attachToCurve() from UI
    """
    # Window
    window = 'attachToCurveUI'
    if not cmds.window(window, q=True, ex=1): raise UIError('AttachToCurve UI does not exist!!')
    # Get UI data
    curve = cmds.textFieldGrp('attachToCurveTFB', q=True, text=True)
    transform = cmds.textFieldGrp('attachToCurveTransformTFB', q=True, text=True)
    prefix = cmds.textFieldGrp('attachToCurvePrefixTFG', q=True, text=True)
    closestPoint = cmds.checkBoxGrp('attachToCurveClosestPointCBG', q=True, v1=True)
    param = cmds.floatSliderGrp('attachToCurveParamFSG', q=True, v=True)
    paramAttr = cmds.textFieldGrp('attachToCurveParamAttrTFG', q=True, text=True)
    orient = cmds.checkBoxGrp('attachToCurveOrientCBG', q=True, v1=True)
    upVec = (cmds.floatFieldGrp('attachToCurveUpVecFFG', q=True, v1=True),
             cmds.floatFieldGrp('attachToCurveUpVecFFG', q=True, v2=True),
             cmds.floatFieldGrp('attachToCurveUpVecFFG', q=True, v3=True))
    upVecObj = cmds.textFieldButtonGrp('attachToCurveUpVecObjTFG', q=True, text=True)
    # Check curve
    if not glTools.utils.curve.isCurve(curve):
        raise UserInputError('Object "' + curve + '" is not a valid nurbs curve!!')
    glTools.utils.attach.attachToCurve(curve=curve, transform=transform, uValue=param, useClosestPoint=closestPoint,
                                       orient=orient, upVector=upVec, worldUpObject=upVecObj, uAttr=paramAttr,
                                       prefix=prefix)
    # Cleanup
    if close: cmds.deleteUI(window)


# Curve To Locators --

def curveToLocatorsUI():
    """
    UI for curveToLocators()
    """
    # Window
    window = 'curveToLocatorsUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Curve To Locators')
    # Layout
    fl = cmds.formLayout(numberOfDivisions=100)
    # UI Elements
    # ---
    # Curve
    curveTFB = cmds.textFieldButtonGrp('curveToLocatorsTFB', label='Target Curve', text='', buttonLabel='Load Selected')
    # Locator List
    locListTSL = cmds.textScrollList('curveToLocatorsTSL', numberOfRows=8, allowMultiSelection=True)
    # TSL Buttons
    locAddB = cmds.button('attachToCurveAddLocB', l='Add', c='glTools.ui.utils.addToTSL("' + locListTSL + '")')
    locRemB = cmds.button('attachToCurveRemLocB', l='Remove', c='glTools.ui.utils.removeFromTSL("' + locListTSL + '")')
    # Buttons
    createB = cmds.button('attachToCurveCreateB', l='Create', c='glTools.ui.curve.curveToLocatorsFromUI(False)')
    cancelB = cmds.button('attachToCurveCancelB', l='Cancel', c='cmds.deleteUI("' + window + '")')

    # Form Layout
    cmds.formLayout(fl, e=True, af=[(curveTFB, 'top', 5), (curveTFB, 'left', 5), (curveTFB, 'right', 5)])
    cmds.formLayout(fl, e=True, ac=[(locListTSL, 'top', 5, curveTFB), (locListTSL, 'bottom', 5, locAddB)])
    cmds.formLayout(fl, e=True, af=[(locListTSL, 'left', 5), (locListTSL, 'right', 5)])
    cmds.formLayout(fl, e=True, ac=[(locAddB, 'bottom', 1, locRemB)])
    cmds.formLayout(fl, e=True, af=[(locAddB, 'left', 5), (locAddB, 'right', 5)])
    cmds.formLayout(fl, e=True, ac=[(locRemB, 'bottom', 1, createB)])
    cmds.formLayout(fl, e=True, af=[(locRemB, 'left', 5), (locRemB, 'right', 5)])
    cmds.formLayout(fl, e=True, ac=[(createB, 'bottom', 1, cancelB)])
    cmds.formLayout(fl, e=True, af=[(createB, 'left', 5), (createB, 'right', 5)])
    cmds.formLayout(fl, e=True, af=[(cancelB, 'bottom', 5), (cancelB, 'left', 5), (cancelB, 'right', 5)])

    # TFB commands
    cmds.textFieldButtonGrp(curveTFB, e=True, bc='glTools.ui.utils.loadCurveSel("' + curveTFB + '")')

    # Show Window
    cmds.showWindow(window)


def curveToLocatorsFromUI(close=False):
    """
    Execute curveToLocators() from UI
    """
    # Window
    window = 'curveToLocatorsUI'
    if not cmds.window(window, q=True, ex=1): raise UIError('CurveToLocators UI does not exist!!')
    curve = cmds.textFieldGrp('curveToLocatorsTFB', q=True, text=True)
    locList = cmds.textScrollList('curveToLocatorsTSL', q=True, ai=True)
    # Check curve
    if not glTools.utils.curve.isCurve(curve):
        raise UserInputError('Object "' + curve + '" is not a valid nurbs curve!!')
    # Execute command
    glTools.utils.curve.curveToLocators(curve=curve, locatorList=locList)
    # Cleanup
    if close: cmds.deleteUI(window)


# Create Along Curve --

def createAlongCurveUI():
    """
    UI for createAlongCurve()
    """
    # Window
    window = 'createAlongCurveUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Create Along Curve')

    # Layout
    cl = cmds.columnLayout()
    # Curve
    curveTFB = cmds.textFieldButtonGrp('createAlongCurveTFB', label='Target Curve', text='', buttonLabel='Load Selected')
    # Prefix
    prefixTFG = cmds.textFieldGrp('createAlongCurvePrefixTFG', label='Prefix', text='')
    # Object Type
    typeOMG = cmds.optionMenuGrp('createAlongCurveTypeOMG', label='Object Type')
    for item in ['joint', 'transform', 'locator']: cmds.menuItem(label=item)
    # Object Count
    countISG = cmds.intSliderGrp('createAlongCurveCountISG', field=True, label='Object Count', minValue=0, maxValue=10,
                               fieldMinValue=0, fieldMaxValue=100, value=0)
    # Parent Objects
    parentCBG = cmds.checkBoxGrp('createAlongCurveParentCBG', numberOfCheckBoxes=1, label='Parent Objects', v1=True)
    # Use Distance
    distanceCBG = cmds.checkBoxGrp('createAlongCurveDistCBG', numberOfCheckBoxes=1, label='Use Distance', v1=False)
    # Min/Max Percent
    minPercentFFG = cmds.floatSliderGrp('createAlongCurveMinFSG', label='Min Percent', field=True, minValue=0.0,
                                      maxValue=1.0, fieldMinValue=0.0, fieldMaxValue=1.0, value=0.0)
    maxPercentFFG = cmds.floatSliderGrp('createAlongCurveMaxFSG', label='Max Percent', field=True, minValue=0.0,
                                      maxValue=1.0, fieldMinValue=0.0, fieldMaxValue=1.0, value=1.0)

    # Buttons
    createB = cmds.button('createAlongCurveCreateB', l='Create', c='glTools.ui.curve.createAlongCurveFromUI(False)')
    createCloseB = cmds.button('createAlongCurveCreateCloseB', l='Create and Close',
                             c='glTools.ui.curve.createAlongCurveFromUI(True)')
    cancelB = cmds.button('createAlongCurveCancelB', l='Cancel', c='cmds.deleteUI("' + window + '")')

    # TFB commands
    cmds.textFieldButtonGrp(curveTFB, e=True, bc='glTools.ui.utils.loadCurveSel("' + curveTFB + '","' + prefixTFG + '")')

    # Show Window
    cmds.showWindow(window)


def createAlongCurveFromUI(close=False):
    """
    Execute createAlongCurve() from UI
    """
    # Window
    window = 'createAlongCurveUI'
    if not cmds.window(window, q=True, ex=1): raise UIError('CreateAlongCurve UI does not exist!!')
    curve = str(cmds.textFieldGrp('createAlongCurveTFB', q=True, text=True))
    prefix = str(cmds.textFieldGrp('createAlongCurvePrefixTFG', q=True, text=True))
    objType = str(cmds.optionMenuGrp('createAlongCurveTypeOMG', q=True, v=True))
    objCount = cmds.intSliderGrp('createAlongCurveCountISG', q=True, v=True)
    parent = cmds.checkBoxGrp('createAlongCurveParentCBG', q=True, v1=True)
    useDist = cmds.checkBoxGrp('createAlongCurveDistCBG', q=True, v1=True)
    minVal = cmds.floatSliderGrp('createAlongCurveMinFSG', q=True, v=True)
    maxVal = cmds.floatSliderGrp('createAlongCurveMaxFSG', q=True, v=True)

    # Execute command
    glTools.tools.createAlongCurve.create(curve, objType, objCount, parent, useDist, minVal, maxVal, prefix)

    # Cleanup
    if close: cmds.deleteUI(window)


# Edge Loop Curve --

def edgeLoopCurveUI():
    """
    UI for edgeLoopCurve()
    """
    # Window
    window = 'edgeLoopCurveUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Edge Loop Curve')

    # Layout
    CL = cmds.columnLayout()
    # Prefix
    prefixTFG = cmds.textFieldGrp('edgeLoopCurvePrefixTFG', label='Prefix', text='')
    # Rebuild
    rebuildCBG = cmds.checkBoxGrp('edgeLoopCurveRebuildCBG', numberOfCheckBoxes=1, label='Rebuild Curve', v1=True)
    # Span Count
    spanISG = cmds.intSliderGrp('edgeLoopCurveSpanISG', field=True, label='Rebuild Spans', minValue=0, maxValue=10,
                              fieldMinValue=0, fieldMaxValue=100, value=0, en=1)

    # Toggle UI element
    cmds.checkBoxGrp('edgeLoopCurveRebuildCBG', e=True,
                   cc='cmds.intSliderGrp("edgeLoopCurveSpanISG",e=1,en=(not cmds.intSliderGrp("edgeLoopCurveSpanISG",q=1,en=1)))')

    # Buttons
    createB = cmds.button('edgeLoopCurveCreateB', l='Create', c='glTools.ui.curve.edgeLoopCurveFromUI(False)')
    createCloseB = cmds.button('edgeLoopCurveCreateCloseB', l='Create and Close',
                             c='glTools.ui.curve.edgeLoopCurveFromUI(True)')
    cancelB = cmds.button('edgeLoopCurveCancelB', l='Cancel', c='cmds.deleteUI("' + window + '")')

    # Show Window
    cmds.showWindow(window)


def edgeLoopCurveFromUI(close=False):
    """
    Execute createAlongCurve() from UI
    """
    # Get mesh edge selection
    selection = cmds.filterExpand(sm=32)
    if not selection: raise UserInputError('No current valid mesh edge selection!!')
    # Window
    window = 'edgeLoopCurveUI'
    if not cmds.window(window, q=True, ex=1): raise UIError('EdgeLoopCurve UI does not exist!!')
    prefix = str(cmds.textFieldGrp('edgeLoopCurvePrefixTFG', q=True, text=True))
    rebuildCrv = cmds.checkBoxGrp('edgeLoopCurveRebuildCBG', q=True, v1=True)
    spans = cmds.intSliderGrp('edgeLoopCurveSpanISG', q=True, v=True)

    # Execute command
    glTools.utils.curve.edgeLoopCrv(selection, rebuild=rebuildCrv, rebuildSpans=spans, prefix=prefix)

    # Cleanup
    if close: cmds.deleteUI(window)


# Uniform Rebuild Curve --

def uniformRebuildCurveUI():
    """
    UI for uniformRebuild()
    """
    # Window
    window = 'uniformRebuildCurveUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Uniform Rebuild Curve')

    # Layout
    cl = cmds.columnLayout()
    # Curve
    curveTFB = cmds.textFieldButtonGrp('uniformRebuildCurveTFB', label='Source Curve', text='',
                                     buttonLabel='Load Selected')
    # Prefix
    prefixTFG = cmds.textFieldGrp('uniformRebuildCurvePrefixTFG', label='Prefix', text='')
    # Replace Original
    replaceCBG = cmds.checkBoxGrp('uniformRebuildCurveReplaceCBG', numberOfCheckBoxes=1, label='Replace Original',
                                v1=False)
    # Spans
    spanISG = cmds.intSliderGrp('uniformRebuildCurveSpansISG', field=True, label='Rebuild Spans', minValue=2, maxValue=10,
                              fieldMinValue=2, fieldMaxValue=100, value=6)

    # Buttons
    createB = cmds.button('uniformRebuildCurveCreateB', l='Create', c='glTools.ui.curve.uniformRebuildCurveFromUI(False)')
    createCloseB = cmds.button('uniformRebuildCurveCreateCloseB', l='Create and Close',
                             c='glTools.ui.curve.uniformRebuildCurveFromUI(True)')
    cancelB = cmds.button('uniformRebuildCurveCancelB', l='Cancel', c='cmds.deleteUI("' + window + '")')

    # TFB commands
    cmds.textFieldButtonGrp(curveTFB, e=True, bc='glTools.ui.utils.loadCurveSel("' + curveTFB + '","' + prefixTFG + '")')

    # Show Window
    cmds.showWindow(window)


def uniformRebuildCurveFromUI(close=False):
    """
    Execute uniformRebuild() from UI
    """
    # Window
    window = 'uniformRebuildCurveUI'
    if not cmds.window(window, q=True, ex=1): raise UIError('uniformRebuildCurve UI does not exist!!')
    curve = str(cmds.textFieldGrp('uniformRebuildCurveTFB', q=True, text=True))
    if not glTools.utils.curve.isCurve(curve):
        raise UserInputError('Object "' + curve + '" is not a valid nurbs curve!!')
    prefix = str(cmds.textFieldGrp('uniformRebuildCurvePrefixTFG', q=True, text=True))
    replace = cmds.checkBoxGrp('uniformRebuildCurveReplaceCBG', q=True, v1=True)
    spans = cmds.intSliderGrp('uniformRebuildCurveSpansISG', q=True, v=True)

    # Execute command
    glTools.utils.curve.uniformRebuild(curve=curve, spans=spans, replaceOriginal=replace, prefix=prefix)

    # Cleanup
    if close: cmds.deleteUI(window)


# Mirror Curve

def mirrorCurveFromSel():
    """
    Mirror curve shape based on selection
    """
    # Get Selection
    sel = cmds.ls(sl=1, type=['transform', 'joint', 'nurbsCurve'])
    if not sel: return

    # For Each Item in Selection
    for item in sel:

        # Define Curve Shape
        crv = ''

        # Check Transform
        if glTools.utils.transform.isTransform(item):
            # Get Shapes
            itemShapes = cmds.listRelatives(item, s=True, pa=True)
            # Check Shapes
            if not itemShapes:
                print('Object "" is not a valid nurbsCurve! Skipping...')
                continue
            # Find Curve Shape
            for shape in itemShapes:
                if glTools.utils.curve.isCurve(shape):
                    crv = shape
                    break
            # Check Curve
            if not crv:
                print('Object "" is not a valid nurbsCurve! Skipping...')
                continue
        else:
            # Set Curve
            crv = item

        # Find Mirror
        mirrorCrv = ''
        if crv.startswith('lf_'):
            mirrorCrv = crv.replace('lf_', 'rt_')
        elif crv.startswith('rt_'):
            mirrorCrv = crv.replace('rt_', 'lf_')
        else:
            print('Unable to determine mirror curve for "' + crv + '"! Skipping...')

    # Mirror Curve
    glTools.utils.curve.mirrorCurve(crv, mirrorCrv)
