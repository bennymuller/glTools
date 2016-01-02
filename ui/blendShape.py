import maya.cmds as cmds
import glTools.tools.blendShape
import glTools.utils.blendShape
import glTools.ui.utils


def blendShapeManagerUI():
    """
    """
    # Window
    window = 'blendShapeManagerUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='BlendShape Manager')

    # Layout
    FL = cmds.formLayout()

    # ===============
    # - UI Elements -
    # ===============

    cw = 100

    # TextScrollList
    blendShapeTXT = cmds.text(label='BlendShape')
    blendShapeTSL = cmds.textScrollList('bsMan_blendShapeTSL', allowMultiSelection=False)
    baseGeomTXT = cmds.text(label='Base Geometry')
    baseGeomTSL = cmds.textScrollList('bsMan_baseGeomTSL', allowMultiSelection=True)
    targetListTXT = cmds.text(label='Target List')
    targetListTSL = cmds.textScrollList('bsMan_targetsTSL', allowMultiSelection=True)
    closeB = cmds.button(label='Close', c='cmds.deleteUI("' + window + '")')

    # Scroll Layout
    scrollLayout = cmds.scrollLayout(horizontalScrollBarThickness=16, verticalScrollBarThickness=16, cr=1)
    scrollFL = cmds.formLayout(numberOfDivisions=100)

    # Info Box
    infoFRL = cmds.frameLayout(label='BlendShape Info', collapsable=True, cl=False, p=scrollFL)
    infoFL = cmds.formLayout(numberOfDivisions=100)
    infoSF = cmds.scrollField('bsMan_infoSF', wordWrap=False, ed=False, text='', nl=6, h=105)

    # Add Target
    addTargetFRL = cmds.frameLayout(label='Add Target', collapsable=True, cl=True, p=scrollFL)
    addTargetCL = cmds.columnLayout()
    addTargetGeoTFB = cmds.textFieldButtonGrp('bsMan_addTargetGeoTFB', label='Target Geo', text='', buttonLabel='<<<',
                                            cw=(1, cw))
    addTargetNameTFG = cmds.textFieldGrp('bsMan_addTargetNameTFG', label='Target Name', text='', cw=(1, cw))
    addTargetB = cmds.button(label='Add Target', c='glTools.ui.blendShape.addTargetFromUI()')

    # Add Inbetween
    addInbetweenFRL = cmds.frameLayout(label='Add Target Inbetween', collapsable=True, cl=True, p=scrollFL)
    addInbetweenCL = cmds.columnLayout()
    addInbetweenTFB = cmds.textFieldButtonGrp('bsMan_addInbetweenTFB', label='Inbetween Geo', text='', buttonLabel='<<<',
                                            cw=(1, cw))
    addInbetweenFSG = cmds.floatSliderGrp('bsMan_addInbetweenFSG', label='Target Weight', field=True, minValue=0.0,
                                        maxValue=1.0, pre=2, fieldMinValue=-100.0, fieldMaxValue=100.0, value=0.5,
                                        cw=(1, cw))
    addInbetweenB = cmds.button(label='Add Target Inbetween', c='glTools.ui.blendShape.addTargetInbetweenFromUI()')

    # Connect To Target
    connectTargetFRL = cmds.frameLayout(label='Connect To Target', collapsable=True, cl=True, p=scrollFL)
    connectTargetCL = cmds.columnLayout()
    connectTargetTFB = cmds.textFieldButtonGrp('bsMan_connectTargetTFB', label='Target Geo', text='', buttonLabel='<<<',
                                             cw=(1, cw))
    connectTargetFSG = cmds.floatSliderGrp('bsMan_connectTargetFSG', label='Target Weight', field=True, minValue=0.0,
                                         maxValue=1.0, pre=2, fieldMinValue=-100.0, fieldMaxValue=100.0, value=1.0,
                                         cw=(1, cw))
    connectTargetB = cmds.button(label='Connect To Target', c='glTools.ui.blendShape.connectToTargetFromUI()')

    # Remove Target
    removeTargetFRL = cmds.frameLayout(label='Remove Targets', collapsable=True, cl=True, p=scrollFL)
    removeTargetCL = cmds.columnLayout()
    removeTargetB = cmds.button(label='Remove Targets', c='glTools.ui.blendShape.removeTargetFromUI()')

    # Rename Target
    renameTargetFRL = cmds.frameLayout(label='Rename Target', collapsable=True, cl=True, p=scrollFL)
    renameTargetCL = cmds.columnLayout()
    renameTargetTFG = cmds.textFieldGrp('bsMan_renameTargetTFB', label='Target Name', text='', cw=(1, cw))
    renameTargetB = cmds.button(label='Rename Target', c='glTools.ui.blendShape.renameTargetFromUI()')

    # Update Targets
    updateTargetFRL = cmds.frameLayout(label='Update Targets', collapsable=True, cl=True, p=scrollFL)
    updateTargetCL = cmds.columnLayout()
    updateTargetTFB = cmds.textFieldButtonGrp('bsMan_updateTargetTFB', label='New Base Geo', text='', buttonLabel='<<<',
                                            cw=(1, cw))
    updateTargetB = cmds.button(label='Update Selected Targets', c='glTools.ui.blendShape.bsManUpdateTargetsFromUI()')

    # Regenerate Targets
    regenerateTargetFRL = cmds.frameLayout(label='Regenerate Targets', collapsable=True, cl=True, p=scrollFL)
    regenerateTargetCL = cmds.columnLayout()
    regenerateTargetCBG = cmds.checkBoxGrp('bsMan_regenerateTargetCBG', numberOfCheckBoxes=1, label='Reconnect Targets',
                                         v1=True, cw=(1, cw))
    regenerateTargetB = cmds.button(label='Regenerate Targets', c='glTools.ui.blendShape.regenerateTargetsFromUI()')

    # ========================
    # - UI Callback Commands -
    # ========================

    reloadCmd = 'import glTools.ui.blendShape;reload(glTools.ui.blendShape);glTools.ui.blendShape.reloadUI()'
    cmds.textScrollList(blendShapeTSL, e=True, sc=reloadCmd)
    cmds.textScrollList(baseGeomTSL, e=True, sc=reloadCmd)
    cmds.textScrollList(targetListTSL, e=True, sc=reloadCmd)

    cmds.textFieldButtonGrp(addTargetGeoTFB, e=True,
                          bc='glTools.ui.utils.loadObjectSel(textField="' + addTargetGeoTFB + '")')
    cmds.textFieldButtonGrp(addInbetweenTFB, e=True,
                          bc='glTools.ui.utils.loadObjectSel(textField="' + addInbetweenTFB + '")')
    cmds.textFieldButtonGrp(connectTargetTFB, e=True,
                          bc='glTools.ui.utils.loadObjectSel(textField="' + connectTargetTFB + '")')
    cmds.textFieldButtonGrp(updateTargetTFB, e=True,
                          bc='glTools.ui.utils.loadObjectSel(textField="' + updateTargetTFB + '")')

    # Auto apply (WIP)
    # cmds.textFieldButtonGrp(updateTargetTFB,e=True,cc=glTools.ui.blendShape.renameTargetFromUI())

    # ================
    # - Form Layouts -
    # ================

    cw1 = 25
    cw2 = 50

    cmds.formLayout(FL, e=True, af=[(closeB, 'bottom', 5), (closeB, 'left', 5), (closeB, 'right', 5)])
    cmds.formLayout(FL, e=True, af=[(blendShapeTXT, 'top', 5), (blendShapeTXT, 'left', 5)],
                  ap=[(blendShapeTXT, 'right', 5, cw1)])
    cmds.formLayout(FL, e=True, ac=[(blendShapeTSL, 'top', 5, blendShapeTXT)], af=[(blendShapeTSL, 'left', 5)],
                  ap=[(blendShapeTSL, 'right', 5, cw1), (blendShapeTSL, 'bottom', 5, 50)])
    cmds.formLayout(FL, e=True, ac=[(baseGeomTXT, 'top', 5, blendShapeTSL)], af=[(baseGeomTXT, 'left', 5)],
                  ap=[(baseGeomTXT, 'right', 5, cw1)])
    cmds.formLayout(FL, e=True, ac=[(baseGeomTSL, 'top', 5, baseGeomTXT), (baseGeomTSL, 'bottom', 5, closeB)],
                  af=[(baseGeomTSL, 'left', 5)], ap=[(baseGeomTSL, 'right', 5, cw1)])
    cmds.formLayout(FL, e=True, af=[(targetListTXT, 'top', 5)],
                  ap=[(targetListTXT, 'left', 5, cw1), (targetListTXT, 'right', 5, cw2)])
    cmds.formLayout(FL, e=True, ac=[(targetListTSL, 'top', 5, targetListTXT), (targetListTSL, 'bottom', 5, closeB)],
                  ap=[(targetListTSL, 'left', 5, cw1), (targetListTSL, 'right', 5, cw2)])
    cmds.formLayout(FL, e=True, ac=[(scrollLayout, 'bottom', 5, closeB)],
                  af=[(scrollLayout, 'top', 5), (scrollLayout, 'right', 5)], ap=[(scrollLayout, 'left', 5, cw2)])

    cmds.formLayout(scrollFL, e=True, af=[(infoFRL, 'top', 5), (infoFRL, 'left', 5), (infoFRL, 'right', 5)])
    cmds.formLayout(scrollFL, e=True, ac=[(addTargetFRL, 'top', 5, infoFRL)],
                  af=[(addTargetFRL, 'left', 5), (addTargetFRL, 'right', 5)])
    cmds.formLayout(scrollFL, e=True, ac=[(addInbetweenFRL, 'top', 5, addTargetFRL)],
                  af=[(addInbetweenFRL, 'left', 5), (addInbetweenFRL, 'right', 5)])
    cmds.formLayout(scrollFL, e=True, ac=[(connectTargetFRL, 'top', 5, addInbetweenFRL)],
                  af=[(connectTargetFRL, 'left', 5), (connectTargetFRL, 'right', 5)])
    cmds.formLayout(scrollFL, e=True, ac=[(removeTargetFRL, 'top', 5, connectTargetFRL)],
                  af=[(removeTargetFRL, 'left', 5), (removeTargetFRL, 'right', 5)])
    cmds.formLayout(scrollFL, e=True, ac=[(renameTargetFRL, 'top', 5, removeTargetFRL)],
                  af=[(renameTargetFRL, 'left', 5), (renameTargetFRL, 'right', 5)])
    cmds.formLayout(scrollFL, e=True, ac=[(updateTargetFRL, 'top', 5, renameTargetFRL)],
                  af=[(updateTargetFRL, 'left', 5), (updateTargetFRL, 'right', 5)])
    cmds.formLayout(scrollFL, e=True, ac=[(regenerateTargetFRL, 'top', 5, updateTargetFRL)],
                  af=[(regenerateTargetFRL, 'left', 5), (regenerateTargetFRL, 'right', 5)])

    cmds.formLayout(infoFL, e=True,
                  af=[(infoSF, 'top', 5), (infoSF, 'bottom', 5), (infoSF, 'left', 5), (infoSF, 'right', 5)])

    # ===============
    # - Show Window -
    # ===============

    reloadUI()

    cmds.showWindow(window)


def reloadUI():
    """
    """
    # Reload Lists
    reloadBlendShapeList()
    reloadBaseGeoList()
    reloadTargetList()

    # Reload Info
    reloadInfo()


def reloadBlendShapeList():
    """
    """
    # Get Current List Selection
    bsSel = cmds.textScrollList('bsMan_blendShapeTSL', q=True, si=True)

    # Build BlendShape List
    bsList = cmds.ls(type='blendShape')

    # Clear List
    cmds.textScrollList('bsMan_blendShapeTSL', e=True, ra=True)

    # Rebuild List
    for bs in bsList: cmds.textScrollList('bsMan_blendShapeTSL', e=True, a=bs)

    # Rebuild List Selection
    if bsSel:
        if bsSel[0] in bsList:
            cmds.textScrollList('bsMan_blendShapeTSL', e=True, si=bs)
    if len(bsList) == 1: cmds.textScrollList('bsMan_blendShapeTSL', e=True, si=bsList[0])


def reloadBaseGeoList():
    """
    """
    # Get BlendShape Selection
    blendShape = cmds.textScrollList('bsMan_blendShapeTSL', q=True, si=True)

    # Get Current List Selection
    baseSel = cmds.textScrollList('bsMan_baseGeomTSL', q=True, si=True)

    # Clear List
    cmds.textScrollList('bsMan_baseGeomTSL', e=True, ra=True)
    if not blendShape: return

    # Populate List
    baseGeo = glTools.utils.blendShape.getBaseGeo(blendShape[0])
    for base in baseGeo: cmds.textScrollList('bsMan_baseGeomTSL', e=True, a=base)

    # Rebuild List Selection
    if baseSel: baseSel = list(set(baseSel) & set(baseGeo))
    if baseSel: cmds.textScrollList('bsMan_baseGeomTSL', e=True, si=baseSel)
    if len(baseGeo) == 1: cmds.textScrollList('bsMan_baseGeomTSL', e=True, si=baseGeo[0])


def reloadTargetList():
    """
    """
    # Get BlendShape Selection
    blendShape = cmds.textScrollList('bsMan_blendShapeTSL', q=True, si=True)

    # Get Current List Selection
    targetSel = cmds.textScrollList('bsMan_targetsTSL', q=True, si=True)

    # Clear List
    cmds.textScrollList('bsMan_targetsTSL', e=True, ra=True)
    if not blendShape: return

    # Populate List
    targetList = glTools.utils.blendShape.getTargetList(blendShape[0])
    for target in targetList: cmds.textScrollList('bsMan_targetsTSL', e=True, a=target)

    # Rebuild List Selection
    if targetSel: targetSel = list(set(targetSel) & set(targetList))
    if targetSel: cmds.textScrollList('bsMan_targetsTSL', e=True, si=targetSel)
    if len(targetList) == 1: cmds.textScrollList('bsMan_targetsTSL', e=True, si=targetList[0])


def reloadInfo():
    """
    """
    # Get UI Data
    blendShape = cmds.textScrollList('bsMan_blendShapeTSL', q=True, si=True)
    if not blendShape: blendShape = ['']
    base = cmds.textScrollList('bsMan_baseGeomTSL', q=True, si=True)
    if not base: base = ['']
    target = cmds.textScrollList('bsMan_targetsTSL', q=True, si=True)
    if not target: target = ['']

    # Get Derived Data
    baseIndex = ''
    targetGeo = ''
    targetIndex = ''
    if base[0]: baseIndex = glTools.utils.blendShape.getBaseIndex(blendShape[0], base[0])
    if target[0]: targetGeo = glTools.utils.blendShape.getTargetGeo(blendShape[0], target[0], base[0])
    if target[0]: targetIndex = glTools.utils.blendShape.getTargetIndex(blendShape[0], target[0])

    infoTxt = 'BlendShape: ' + blendShape[0] + '\n'
    infoTxt += 'Base Geometry: ' + base[0] + '\n'
    infoTxt += 'Base Index: ' + str(baseIndex) + '\n'
    infoTxt += 'Target Name: ' + target[0] + '\n'
    infoTxt += 'Target Geometry: ' + targetGeo + '\n'
    infoTxt += 'Target Index: ' + str(targetIndex)

    cmds.scrollField('bsMan_infoSF', e=True, text=infoTxt)


def addTargetFromUI():
    """
    """
    # Get UI Data
    blendShape = cmds.textScrollList('bsMan_blendShapeTSL', q=True, si=True)
    if not blendShape:
        print('No blendShape node selected!')
        return
    base = cmds.textScrollList('bsMan_baseGeomTSL', q=True, si=True)
    if not base: base = ['']
    targetGeo = cmds.textFieldButtonGrp('bsMan_addTargetGeoTFB', q=True, text=True)
    targetName = cmds.textFieldGrp('bsMan_addTargetNameTFG', q=True, text=True)

    # Checks
    if not glTools.utils.blendShape.isBlendShape(blendShape[0]):
        raise Exception('BlendShape "' + blendShape[0] + '" does not exist!')
    if base[0] and not cmds.objExists(base[0]):
        raise Exception('Base geometry "' + base[0] + '" does not exist!')
    if not cmds.objExists(targetGeo):
        raise Exception('Target geometry "' + targetGeo + '" does not exist!')

    # Add BlendShape Target
    glTools.utils.blendShape.addTarget(blendShape=blendShape[0],
                                       target=targetGeo,
                                       base=base[0],
                                       targetIndex=-1,
                                       targetAlias=targetName,
                                       targetWeight=0.0,
                                       topologyCheck=False)

    # Reload
    reloadUI()


def addTargetInbetweenFromUI():
    """
    """
    # Get UI Data
    blendShape = cmds.textScrollList('bsMan_blendShapeTSL', q=True, si=True)
    if not blendShape:
        print('No blendShape node selected!')
        return
    base = cmds.textScrollList('bsMan_baseGeomTSL', q=True, si=True)
    if not base: base = ['']
    targetName = cmds.textScrollList('bsMan_targetsTSL', q=True, si=True)
    if not targetName:
        print('No blendShape target selected!')
        return
    targetGeo = cmds.textFieldButtonGrp('bsMan_addInbetweenTFB', q=True, text=True)
    targetWt = cmds.floatSliderGrp('bsMan_addInbetweenFSG', q=True, v=True)

    # Checks
    if not glTools.utils.blendShape.isBlendShape(blendShape[0]):
        raise Exception('BlendShape "' + blendShape[0] + '" does not exist!')
    if base[0] and not cmds.objExists(base[0]):
        raise Exception('Base geometry "' + base[0] + '" does not exist!')
    if not cmds.objExists(targetGeo):
        raise Exception('Target geometry "' + targetGeo + '" does not exist!')

    # Add BlendShape Target Inbetween
    glTools.utils.blendShape.addTargetInbetween(blendShape=blendShape[0],
                                                targetGeo=targetGeo,
                                                targetName=targetName[0],
                                                base=base[0],
                                                targetWeight=targetWt)

    # Reload
    reloadUI()


def connectToTargetFromUI():
    """
    """
    # Get UI Data
    blendShape = cmds.textScrollList('bsMan_blendShapeTSL', q=True, si=True)
    if not blendShape:
        print('No blendShape node selected!')
        return
    base = cmds.textScrollList('bsMan_baseGeomTSL', q=True, si=True)
    if not base: base = ['']
    target = cmds.textScrollList('bsMan_targetsTSL', q=True, si=True)
    if not target:
        print('No blendShape target selected!')
        return
    targetGeo = cmds.textFieldButtonGrp('bsMan_connectTargetTFB', q=True, text=True)
    targetWt = cmds.floatSliderGrp('bsMan_connectTargetFSG', q=True, v=True)

    # Checks
    if not glTools.utils.blendShape.isBlendShape(blendShape[0]):
        raise Exception('BlendShape "' + blendShape[0] + '" does not exist!')
    if base[0] and not cmds.objExists(base[0]):
        raise Exception('Base geometry "' + base[0] + '" does not exist!')
    if not cmds.objExists(targetGeo):
        raise Exception('Target geometry "' + targetGeo + '" does not exist!')

    # Add BlendShape Target Inbetween
    glTools.utils.blendShape.connectToTarget(blendShape=blendShape[0],
                                             targetGeo=targetGeo,
                                             targetName=targetName[0],
                                             baseGeo=base[0],
                                             weight=1.0)

    # Reload
    reloadUI()


def removeTargetFromUI():
    """
    """
    # Get UI Data
    blendShape = cmds.textScrollList('bsMan_blendShapeTSL', q=True, si=True)
    if not blendShape:
        print('No blendShape node selected!')
        return
    base = cmds.textScrollList('bsMan_baseGeomTSL', q=True, si=True)
    if not base: base = ['']
    targetList = cmds.textScrollList('bsMan_targetsTSL', q=True, si=True)
    if not targetList:
        print('No blendShape targets selected!')
        return

    # Checks
    if not glTools.utils.blendShape.isBlendShape(blendShape[0]):
        raise Exception('BlendShape "' + blendShape[0] + '" does not exist!')
    if base[0] and not cmds.objExists(base[0]):
        raise Exception('Base geometry "' + base[0] + '" does not exist!')

    # Remove BlendShape Targets
    for target in targetList:
        if not glTools.utils.blendShape.hasTarget(blendShape[0], target):
            print('BlendShape "' + blendShape[0] + '" has no target "' + target + '"! Skipping...')
            continue
        glTools.utils.blendShape.removeTarget(blendShape=blendShape[0], target=target, baseGeo=base[0])

    # Reload
    reloadUI()


def renameTargetFromUI():
    """
    """
    # Get UI Data
    blendShape = cmds.textScrollList('bsMan_blendShapeTSL', q=True, si=True)
    if not blendShape:
        print('No blendShape node selected!')
        return
    target = cmds.textScrollList('bsMan_targetsTSL', q=True, si=True)
    if not target:
        print('No blendShape target selected!')
        return
    targetName = cmds.textFieldGrp('bsMan_renameTargetTFB', q=True, text=True)
    if not targetName:
        print('No target name specified!')
        return

    # Checks
    if not glTools.utils.blendShape.isBlendShape(blendShape[0]):
        raise Exception('BlendShape "' + blendShape[0] + '" does not exist!')
    if not glTools.utils.blendShape.hasTarget(blendShape[0], target[0]):
        raise Exception('BlendShape "" has not target "' + target + '"!')

    # Rename BlendShape Target
    glTools.utils.blendShape.renameTarget(blendShape=blendShape[0], target=target[0], newName=targetName)

    # Reload
    reloadUI()


def bsManUpdateTargetsFromUI():
    """
    """
    # Get UI Data
    blendShape = cmds.textScrollList('bsMan_blendShapeTSL', q=True, si=True)
    if not blendShape:
        print('No blendShape node selected!')
        return
    base = cmds.textScrollList('bsMan_baseGeomTSL', q=True, si=True)
    if not base: raise Exception('No base (old) geometry specified!')
    oldBase = base[0]
    newBase = cmds.textFieldButtonGrp('bsMan_updateTargetTFB', q=True, text=True)
    targetList = cmds.textScrollList('bsMan_targetsTSL', q=True, si=True)

    # Checks
    if not glTools.utils.blendShape.isBlendShape(blendShape[0]):
        raise Exception('BlendShape "' + blendShape[0] + '" does not exist!')
    if not cmds.objExists(oldBase):
        raise Exception('Old base geometry "' + oldBase + '" does not exist!')
    if not cmds.objExists(newBase):
        raise Exception('New base geometry "' + newBase + '" does not exist!')
    if not targetList: raise Exception('Empty target list!')

    # Get Target Geometry
    targetGeoList = []
    for target in targetList:
        targetGeo = glTools.utils.blendShape.getTargetGeo(blendShape[0], target, baseGeo=oldBase)
        if not targetGeo:
            print('No target geometry found for target name"' + target + '"! Skipping')
            continue
        targetGeoList.append(targetGeo)

    # Update Targets
    glTools.tools.blendShape.updateTargets(oldBase, newBase, targetGeoList)


def regenerateTargetsFromUI():
    """
    """
    # ===============
    # - Get UI Data -
    # ===============

    # BlendShape
    blendShape = cmds.textScrollList('bsMan_blendShapeTSL', q=True, si=True)
    if not blendShape:
        print('No blendShape node selected!')
        return

    # Base Geo
    base = cmds.textScrollList('bsMan_baseGeomTSL', q=True, si=True)
    if not base: base = ['']

    # Target List
    targetList = cmds.textScrollList('bsMan_targetsTSL', q=True, si=True)
    if not targetList:
        print('No blendShape targets selected!')
        return

    # Reconnect Targets
    connect = cmds.checkBoxGrp('bsMan_regenerateTargetCBG', q=True, v1=True)

    # ==========
    # - Checks -
    # ==========

    if not glTools.utils.blendShape.isBlendShape(blendShape[0]):
        raise Exception('BlendShape "' + blendShape[0] + '" does not exist!')
    if base[0] and not cmds.objExists(base[0]):
        raise Exception('Base geometry "' + base[0] + '" does not exist!')

    # ==============================
    # - Regenerate Target Geometry -
    # ==============================

    for target in targetList:
        if not glTools.utils.blendShape.hasTarget(blendShape[0], target):
            print('BlendShape "' + blendShape[0] + '" has no target "' + target + '"! Skipping...')
            continue
        glTools.tools.blendShape.regenerateTarget(blendShape=blendShape[0], target=target, base=base[0],
                                                  connect=connect)


# === BlendShape Manager End ==

def updateTargetsUI():
    """
    """
    # Window
    window = 'updateTargetsUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Update BlendShape Targets')

    # Layout
    FL = cmds.formLayout()

    # UI Elements
    oldBaseTFB = cmds.textFieldButtonGrp('updateTarget_oldBaseTFB', label='Old Base', text='', buttonLabel='<<<')
    newBaseTFB = cmds.textFieldButtonGrp('updateTarget_newBaseTFB', label='New Base', text='', buttonLabel='<<<')
    targetListTXT = cmds.text(label='Target List')
    targetListTSL = cmds.textScrollList('updateTarget_targetsTSL', allowMultiSelection=True)
    updateB = cmds.button(label='Update Targets', c='glTools.ui.blendShape.updateTargetsFromUI()')
    cancelB = cmds.button(label='Cancel', c='cmds.deleteUI("' + window + '")')

    # PopUp Menu Items
    cmds.popupMenu(parent=targetListTSL)
    cmds.menuItem(label='Add Selected', c='glTools.ui.utils.addToTSL(TSL="' + targetListTSL + '")')
    cmds.menuItem(label='Remove Selected', c='glTools.ui.utils.removeFromTSL(TSL="' + targetListTSL + '")')

    # UI Callback Commands
    cmds.textFieldButtonGrp(oldBaseTFB, e=True, bc='glTools.ui.utils.loadObjectSel(textField="' + oldBaseTFB + '")')
    cmds.textFieldButtonGrp(newBaseTFB, e=True, bc='glTools.ui.utils.loadObjectSel(textField="' + newBaseTFB + '")')

    # Form Layouts
    cmds.formLayout(FL, e=True, af=[(oldBaseTFB, 'top', 5), (oldBaseTFB, 'left', 5), (oldBaseTFB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(newBaseTFB, 'top', 5, oldBaseTFB)],
                  af=[(newBaseTFB, 'left', 5), (newBaseTFB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(targetListTXT, 'top', 5, newBaseTFB)],
                  af=[(targetListTXT, 'left', 5), (targetListTXT, 'right', 5)])
    cmds.formLayout(FL, e=True, af=[(cancelB, 'bottom', 5), (cancelB, 'left', 5), (cancelB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(updateB, 'bottom', 5, cancelB)], af=[(updateB, 'left', 5), (updateB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(targetListTSL, 'top', 5, targetListTXT), (targetListTSL, 'bottom', 5, updateB)],
                  af=[(targetListTSL, 'left', 5), (targetListTSL, 'right', 5)])

    # Show Window
    cmds.showWindow(window)


def updateTargetsFromUI():
    """
    """
    # Get UI Data
    oldBase = cmds.textFieldButtonGrp('updateTarget_oldBaseTFB', q=True, text=True)
    newBase = cmds.textFieldButtonGrp('updateTarget_newBaseTFB', q=True, text=True)
    targetList = cmds.textScrollList('updateTarget_targetsTSL', q=True, ai=True)

    # Checks
    if not cmds.objExists(oldBase):
        raise Exception('Old base geometry "' + oldBase + '" does not exist!')
    if not cmds.objExists(newBase):
        raise Exception('New base geometry "' + newBase + '" does not exist!')
    if not targetList: raise Exception('Empty target list!')
    for target in targetList:
        if not cmds.objExists(target):
            raise Exception('Target geometry "' + target + '" does not exist!')

    # Update Targets
    glTools.tools.blendShape.updateTargets(oldBase, newBase, targetList)
