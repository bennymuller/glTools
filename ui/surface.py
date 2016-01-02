import maya.cmds as cmds
import glTools.ui.utils
import glTools.utils.surface


class UserInputError(Exception): pass


class UIError(Exception): pass


# Locator Surface --

def locatorSurfaceUI():
    """
    UI for locatorSurface()
    """
    # Window
    window = 'locatorSurfaceUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Locator Surface')
    # Layout
    FL = cmds.formLayout(numberOfDivisions=100)
    # UI Elements
    # ---
    # Surface
    surfaceTFB = cmds.textFieldButtonGrp('locatorSurfaceTFB', label='Source Surface', text='',
                                       buttonLabel='Load Selected')
    # Prefix
    prefixTFG = cmds.textFieldGrp('locatorSurfacePrefixTFG', label='Prefix', text='')
    # Scale
    scaleFSG = cmds.floatSliderGrp('locatorSurfaceScaleFSG', label='Locator Scale', field=True, minValue=0.0,
                                 maxValue=1.0, fieldMinValue=0.0, fieldMaxValue=10.0, value=0.75, pre=3)
    # Use Control Points
    useCvCBG = cmds.checkBoxGrp('locatorSurfaceUseCvCBG', l='Specify CVs', ncb=1, v1=False)

    # Control Points layout
    cvFrameL = cmds.frameLayout('locatorSurfaceCvFL', l='Control Points', cll=0, en=0)
    cvFormL = cmds.formLayout(numberOfDivisions=100)
    controlPointTSL = cmds.textScrollList('locatorSurfaceCpTSL', numberOfRows=8, allowMultiSelection=True)
    # TSL Buttons
    cvAddB = cmds.button('locatorSurfaceAddCvB', l='Add', c='glTools.ui.utils.addCvsToTSL("' + controlPointTSL + '")',
                       en=False)
    cvRemB = cmds.button('locatorSurfaceRecmdsvB', l='Remove',
                       c='glTools.ui.utils.removeFromTSL("' + controlPointTSL + '")', en=False)

    cmds.setParent('..')
    cmds.setParent('..')

    # Separator
    SEP = cmds.separator(height=10, style='single')
    # Buttons
    createB = cmds.button('locatorSurfaceCreateB', l='Create', c='glTools.ui.surface.locatorSurfaceFromUI()')
    cancelB = cmds.button('locatorSurfaceCancelB', l='Cancel', c='cmds.deleteUI("' + window + '")')

    # UI callback commands
    cmds.textFieldButtonGrp(surfaceTFB, e=True,
                          bc='glTools.ui.utils.loadSurfaceSel("' + surfaceTFB + '","' + prefixTFG + '")')
    cmds.checkBoxGrp('locatorSurfaceUseCvCBG', e=True,
                   cc='glTools.ui.utils.checkBoxToggleLayout("' + useCvCBG + '","' + cvFrameL + '")')

    # Form Layout - MAIN
    cmds.formLayout(FL, e=True, af=[(surfaceTFB, 'top', 5), (surfaceTFB, 'left', 5), (surfaceTFB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(prefixTFG, 'top', 5, surfaceTFB)])
    cmds.formLayout(FL, e=True, af=[(prefixTFG, 'left', 5), (prefixTFG, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(scaleFSG, 'top', 5, prefixTFG)])
    cmds.formLayout(FL, e=True, af=[(scaleFSG, 'left', 5), (scaleFSG, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(useCvCBG, 'top', 5, scaleFSG)])
    cmds.formLayout(FL, e=True, af=[(useCvCBG, 'left', 5)])
    cmds.formLayout(FL, e=True, ac=[(cvFrameL, 'top', 5, useCvCBG)])
    cmds.formLayout(FL, e=True, af=[(cvFrameL, 'left', 5), (cvFrameL, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(cvFrameL, 'bottom', 5, SEP)])
    cmds.formLayout(FL, e=True, ac=[(SEP, 'bottom', 5, createB)])
    cmds.formLayout(FL, e=True, af=[(SEP, 'left', 5), (SEP, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(createB, 'bottom', 5, cancelB)])
    cmds.formLayout(FL, e=True, af=[(createB, 'left', 5), (createB, 'right', 5)])
    cmds.formLayout(FL, e=True, af=[(cancelB, 'left', 5), (cancelB, 'right', 5), (cancelB, 'bottom', 5)])

    # Form Layout - Control Points
    cmds.formLayout(cvFormL, e=True,
                  af=[(controlPointTSL, 'top', 5), (controlPointTSL, 'left', 5), (controlPointTSL, 'right', 5)])
    cmds.formLayout(cvFormL, e=True, ac=[(controlPointTSL, 'bottom', 5, cvAddB)])
    cmds.formLayout(cvFormL, e=True, af=[(cvAddB, 'left', 5), (cvAddB, 'bottom', 5)])
    cmds.formLayout(cvFormL, e=True, ap=[(cvAddB, 'right', 5, 50)])
    cmds.formLayout(cvFormL, e=True, af=[(cvRemB, 'right', 5), (cvRemB, 'bottom', 5)])
    cmds.formLayout(cvFormL, e=True, ap=[(cvRemB, 'left', 5, 50)])

    # Show Window
    cmds.showWindow(window)


def locatorSurfaceFromUI():
    """
    Execute locatorSurface() from UI
    """
    # Window
    window = 'locatorSurfaceUI'
    if not cmds.window(window, q=True, ex=1): raise UIError('LocatorSurface UI does not exist!!')
    # Get UI data
    surface = cmds.textFieldGrp('locatorSurfaceTFB', q=True, text=True)
    # Check surface
    if not glTools.utils.surface.isSurface(surface):
        raise UserInputError('Object "' + surface + '" is not a valid nurbs surface!!')
    prefix = cmds.textFieldGrp('locatorSurfacePrefixTFG', q=True, text=True)
    scale = cmds.floatSliderGrp('locatorSurfaceScaleFSG', q=True, v=True)
    useCvs = cmds.checkBoxGrp('locatorSurfaceUseCvCBG', q=True, v1=True)
    cvList = cmds.textScrollList('locatorSurfaceCpTSL', q=True, ai=True)
    if useCvs and not cvList:
        raise UserInputError('No control points specified!!')

    # Execute command
    glTools.utils.surface.locatorSurface(surface=surface, controlPoints=cvList, locatorScale=scale * 0.1, prefix=prefix)

    # Cleanup
    cmds.deleteUI(window)


# Snap To Surface --

def snapToSurfaceUI():
    """
    UI for snapToSurface()
    """
    # Window
    window = 'snapToSurfaceUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Snap To Surface')
    # Layout
    FL = cmds.formLayout(numberOfDivisions=100)
    # UI Elements
    # ---
    # Surface
    surfaceTFB = cmds.textFieldButtonGrp('snapToSurfaceTFB', label='Source Surface', text='', buttonLabel='Load Selected')
    # Orient
    orientCBG = cmds.checkBoxGrp('snapToSurfaceOrientCBG', label='Orient To Surface', ncb=1, v1=False)

    # Orient Frame
    orientFrameL = cmds.frameLayout('snapToSurfaceOriFL', l='Orient Options', cll=0, en=0)
    orientFormL = cmds.formLayout(numberOfDivisions=100)
    # OMG
    axList = ['X', 'Y', 'Z', '-X', '-Y', '-Z']
    orientUAxisOMG = cmds.optionMenuGrp('snapToSurfaceUAxisOMG', label='TangentU Axis', en=False)
    for ax in axList: cmds.menuItem(label=ax)
    orientVAxisOMG = cmds.optionMenuGrp('snapToSurfaceVAxisOMG', label='TangentV Axis', en=False)
    for ax in axList: cmds.menuItem(label=ax)
    orientAlignToOMG = cmds.optionMenuGrp('snapToSurfaceAlignToOMG', label='Align To', en=False)
    for ax in ['U', 'V']: cmds.menuItem(label=ax)
    # Set Default Value
    cmds.optionMenuGrp('snapToSurfaceVAxisOMG', e=True, sl=2)

    cmds.setParent('..')
    cmds.setParent('..')

    # UI callback commands
    cmds.textFieldButtonGrp(surfaceTFB, e=True, bc='glTools.ui.utils.loadSurfaceSel("' + surfaceTFB + '")')
    cmds.checkBoxGrp(orientCBG, e=True,
                   cc='glTools.ui.utils.checkBoxToggleLayout("' + orientCBG + '","' + orientFrameL + '")')

    # Buttons
    snapB = cmds.button('snapToSurfaceSnapB', l='Snap!', c='glTools.ui.surface.snapToSurfaceFromUI(False)')
    snapCloseB = cmds.button('snapToSurfaceSnapCloseB', l='Snap and Close',
                           c='glTools.ui.surface.snapToSurfaceFromUI(True)')
    cancelB = cmds.button('snapToSurfaceCancelB', l='Cancel', c='cmds.deleteUI("' + window + '")')

    # Form Layout - MAIN
    cmds.formLayout(FL, e=True, af=[(surfaceTFB, 'top', 5), (surfaceTFB, 'left', 5), (surfaceTFB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(orientCBG, 'top', 5, surfaceTFB)])
    cmds.formLayout(FL, e=True, af=[(orientCBG, 'left', 5), (orientCBG, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(orientFrameL, 'top', 5, orientCBG)])
    cmds.formLayout(FL, e=True, af=[(orientFrameL, 'left', 5), (orientFrameL, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(orientFrameL, 'bottom', 5, snapB)])
    cmds.formLayout(FL, e=True, ac=[(snapB, 'bottom', 5, snapCloseB)])
    cmds.formLayout(FL, e=True, af=[(snapB, 'left', 5), (snapB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(snapCloseB, 'bottom', 5, cancelB)])
    cmds.formLayout(FL, e=True, af=[(snapCloseB, 'left', 5), (snapCloseB, 'right', 5)])
    cmds.formLayout(FL, e=True, af=[(cancelB, 'left', 5), (cancelB, 'right', 5), (cancelB, 'bottom', 5)])

    # Form Layout - Orient
    cmds.formLayout(orientFormL, e=True,
                  af=[(orientUAxisOMG, 'top', 5), (orientUAxisOMG, 'left', 5), (orientUAxisOMG, 'right', 5)])
    cmds.formLayout(orientFormL, e=True, ac=[(orientVAxisOMG, 'top', 5, orientUAxisOMG)])
    cmds.formLayout(orientFormL, e=True, af=[(orientVAxisOMG, 'left', 5), (orientVAxisOMG, 'right', 5)])
    cmds.formLayout(orientFormL, e=True, ac=[(orientAlignToOMG, 'top', 5, orientVAxisOMG)])
    cmds.formLayout(orientFormL, e=True, af=[(orientAlignToOMG, 'left', 5), (orientAlignToOMG, 'right', 5)])

    # Show Window
    cmds.showWindow(window)


def snapToSurfaceFromUI(close=False):
    """
    Execute snapToSurface() from UI
    """
    # Window
    window = 'snapToSurfaceUI'
    if not cmds.window(window, q=True, ex=1): raise UIError('SnapToSurface UI does not exist!!')
    # Get UI data
    surface = cmds.textFieldGrp('snapToSurfaceTFB', q=True, text=True)
    # Check surface
    if not glTools.utils.surface.isSurface(surface):
        raise UserInputError('Object "' + surface + '" is not a valid nurbs surface!!')
    # Orient
    orient = cmds.checkBoxGrp('snapToSurfaceOrientCBG', q=True, v1=True)
    # Orient Options
    tanU = str.lower(str(cmds.optionMenuGrp('snapToSurfaceUAxisOMG', q=True, v=True)))
    tanV = str.lower(str(cmds.optionMenuGrp('snapToSurfaceVAxisOMG', q=True, v=True)))
    align = str.lower(str(cmds.optionMenuGrp('snapToSurfaceAlignToOMG', q=True, v=True)))

    # Get User Selection
    sel = cmds.ls(sl=True, fl=True)

    # Execute Command
    glTools.utils.surface.snapPtsToSurface(surface, sel)
    # Orient
    if orient:
        for obj in sel:
            try:
                glTools.utils.surface.orientToSurface(surface=surface, obj=obj, useClosestPoint=True, tangentUAxis=tanU,
                                                      tangentVAxis=tanV, alignTo=align)
            except:
                print('Object "' + obj + '" is not a valid transform!! Unable to orient!')

    # Cleanup
    if close: cmds.deleteUI(window)


# Attach To Surface --

def attachToSurfaceUI():
    """
    UI for attachToSurface()
    """
    # Window
    window = 'attachToSurfaceUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Attach To Surface')
    # Layout
    FL = cmds.formLayout(numberOfDivisions=100)
    # UI Elements
    # ---
    # Surface
    surfaceTFB = cmds.textFieldButtonGrp('attachToSurfaceTFB', label='Target Surface', text='',
                                       buttonLabel='Load Selected')
    # Transform
    transformTFB = cmds.textFieldButtonGrp('attachToSurfaceTransformTFB', label='Transform', text='',
                                         buttonLabel='Load Selected')
    # Prefix
    prefixTFG = cmds.textFieldGrp('attachToSurfacePrefixTFG', label='Prefix', text='')
    # Use Closest Point
    closePointCBG = cmds.checkBoxGrp('attachToSurfaceClosePntCBG', label='Use Closest Point', ncb=1, v1=False)
    # U/V Parameter
    uvParamFFG = cmds.floatFieldGrp('attachToSurfaceParamTFB', label='UV Parameter', nf=2, v1=0, v2=0)
    # U/V Parameter Attributes
    uParamAttrTFG = cmds.textFieldGrp('attachToSurfaceUAttrTFG', label='U Param Attribute', text='uCoord')
    vParamAttrTFG = cmds.textFieldGrp('attachToSurfaceVAttrTFG', label='V Param Attribute', text='vCoord')
    # Orient
    orientCBG = cmds.checkBoxGrp('attachToSurfaceOrientCBG', label='Orient To Surface', ncb=1, v1=False)

    # Orient Frame
    orientFrameL = cmds.frameLayout('attachToSurfaceOriFL', l='Orient Options', cll=0, en=0)
    orientFormL = cmds.formLayout(numberOfDivisions=100)
    # OMG
    axList = ['X', 'Y', 'Z', '-X', '-Y', '-Z']
    orientUAxisOMG = cmds.optionMenuGrp('attachToSurfaceUAxisOMG', label='TangentU Axis', en=False)
    for ax in axList: cmds.menuItem(label=ax)
    orientVAxisOMG = cmds.optionMenuGrp('attachToSurfaceVAxisOMG', label='TangentV Axis', en=False)
    for ax in axList: cmds.menuItem(label=ax)
    orientAlignToOMG = cmds.optionMenuGrp('attachToSurfaceAlignToOMG', label='Align To', en=False)
    for ax in ['U', 'V']: cmds.menuItem(label=ax)
    # Set Default Value
    cmds.optionMenuGrp('attachToSurfaceVAxisOMG', e=True, sl=2)

    cmds.setParent('..')
    cmds.setParent('..')

    # Buttons
    attachB = cmds.button('attachToSurfaceAttachB', l='Attach', c='glTools.ui.surface.attachToSurfaceFromUI(False)')
    cancelB = cmds.button('snapToSurfaceCancelB', l='Cancel', c='cmds.deleteUI("' + window + '")')

    # UI callback commands
    cmds.textFieldButtonGrp(surfaceTFB, e=True, bc='glTools.ui.utils.loadSurfaceSel("' + surfaceTFB + '")')
    cmds.textFieldButtonGrp(transformTFB, e=True,
                          bc='glTools.ui.utils.loadObjectSel("' + transformTFB + '","' + prefixTFG + '")')
    cmds.checkBoxGrp(closePointCBG, e=True,
                   cc='glTools.ui.utils.checkBoxToggleControl("' + closePointCBG + '","' + uvParamFFG + '",invert=True)')
    cmds.checkBoxGrp(orientCBG, e=True,
                   cc='glTools.ui.utils.checkBoxToggleLayout("' + orientCBG + '","' + orientFrameL + '")')

    # Form Layout - Main
    cmds.formLayout(FL, e=True, af=[(surfaceTFB, 'top', 5), (surfaceTFB, 'left', 5), (surfaceTFB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(transformTFB, 'top', 5, surfaceTFB)])
    cmds.formLayout(FL, e=True, af=[(transformTFB, 'left', 5), (transformTFB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(prefixTFG, 'top', 5, transformTFB)])
    cmds.formLayout(FL, e=True, af=[(prefixTFG, 'left', 5), (prefixTFG, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(closePointCBG, 'top', 5, prefixTFG)])
    cmds.formLayout(FL, e=True, af=[(closePointCBG, 'left', 5), (closePointCBG, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(uvParamFFG, 'top', 5, closePointCBG)])
    cmds.formLayout(FL, e=True, af=[(uvParamFFG, 'left', 5), (uvParamFFG, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(uParamAttrTFG, 'top', 5, uvParamFFG)])
    cmds.formLayout(FL, e=True, af=[(uParamAttrTFG, 'left', 5), (uParamAttrTFG, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(vParamAttrTFG, 'top', 5, uParamAttrTFG)])
    cmds.formLayout(FL, e=True, af=[(vParamAttrTFG, 'left', 5), (vParamAttrTFG, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(orientCBG, 'top', 5, vParamAttrTFG)])
    cmds.formLayout(FL, e=True, af=[(orientCBG, 'left', 5), (orientCBG, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(orientFrameL, 'top', 5, orientCBG)])
    cmds.formLayout(FL, e=True, af=[(orientFrameL, 'left', 5), (orientFrameL, 'right', 5)])
    cmds.formLayout(FL, e=True, af=[(attachB, 'left', 5), (attachB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(attachB, 'bottom', 5, cancelB)])
    cmds.formLayout(FL, e=True, af=[(cancelB, 'left', 5), (cancelB, 'right', 5), (cancelB, 'bottom', 5)])

    # Form Layout - Orient
    cmds.formLayout(orientFormL, e=True,
                  af=[(orientUAxisOMG, 'top', 5), (orientUAxisOMG, 'left', 5), (orientUAxisOMG, 'right', 5)])
    cmds.formLayout(orientFormL, e=True, ac=[(orientVAxisOMG, 'top', 5, orientUAxisOMG)])
    cmds.formLayout(orientFormL, e=True, af=[(orientVAxisOMG, 'left', 5), (orientVAxisOMG, 'right', 5)])
    cmds.formLayout(orientFormL, e=True, ac=[(orientAlignToOMG, 'top', 5, orientVAxisOMG)])
    cmds.formLayout(orientFormL, e=True, af=[(orientAlignToOMG, 'left', 5), (orientAlignToOMG, 'right', 5)])

    # Show Window
    cmds.showWindow(window)


def attachToSurfaceFromUI(close=True):
    """
    Execute attachToSurface() from UI
    """
    # Window
    window = 'attachToSurfaceUI'
    if not cmds.window(window, q=True, ex=1): raise UIError('AttachToSurface UI does not exist!!')
    # Get UI data
    surf = cmds.textFieldGrp('attachToSurfaceTFB', q=True, text=True)
    # Check surface
    if not glTools.utils.surface.isSurface(surf):
        raise UserInputError('Object "' + surf + '" is not a valid nurbs surface!!')
    trans = cmds.textFieldGrp('attachToSurfaceTransformTFB', q=True, text=True)
    pre = cmds.textFieldGrp('attachToSurfacePrefixTFG', q=True, text=True)
    uParam = cmds.floatFieldGrp('attachToSurfaceParamTFB', q=True, v1=True)
    vParam = cmds.floatFieldGrp('attachToSurfaceParamTFB', q=True, v2=True)
    closePnt = cmds.checkBoxGrp('attachToSurfaceClosePntCBG', q=True, v1=True)
    uAttr = cmds.textFieldGrp('attachToSurfaceUAttrTFG', q=True, text=True)
    vAttr = cmds.textFieldGrp('attachToSurfaceVAttrTFG', q=True, text=True)
    # Orient
    orient = cmds.checkBoxGrp('attachToSurfaceOrientCBG', q=True, v1=True)
    # Orient Options
    tanU = str.lower(str(cmds.optionMenuGrp('attachToSurfaceUAxisOMG', q=True, v=True)))
    tanV = str.lower(str(cmds.optionMenuGrp('attachToSurfaceVAxisOMG', q=True, v=True)))
    align = str.lower(str(cmds.optionMenuGrp('attachToSurfaceAlignToOMG', q=True, v=True)))

    # Execute command
    result = glTools.utils.attach.attachToSurface(surface=surf, transform=trans, uValue=uParam, vValue=vParam,
                                                  useClosestPoint=closePnt, orient=orient, uAxis=tanU, vAxis=tanV,
                                                  uAttr=uAttr, vAttr=vAttr, alignTo=align, prefix=pre)

    # Cleanup
    if close: cmds.deleteUI(window)
