import maya.cmds as cmds
import glTools.tools.transformDrivenBlend
import glTools.ui.utils


def ui():
    """
    """
    # Window
    window = 'transformDrivenBlendUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Transform Driven Blend')

    # Layout
    cl = cmds.columnLayout()

    # UI Elements
    driveAttrTFG = cmds.textFieldGrp('tdb_driveAttrTFG', label='Drive Attr', text='')
    blendShapeTFG = cmds.textFieldGrp('tdb_blendShapeTFG', label='BlendShape', text='')
    target1TFG = cmds.textFieldGrp('tdb_target1TFG', label='Target 1', text='',
                                 cc='glTools.ui.transformDrivenBlend.refreshUI()')
    target2TFG = cmds.textFieldGrp('tdb_target2TFG', label='Target 2', text='',
                                 cc='glTools.ui.transformDrivenBlend.refreshUI()')
    weight1FFG = cmds.floatFieldGrp('tdb_weight1FFG', numberOfFields=1, label='Weight 1', v1=1.0)
    weight2FFG = cmds.floatFieldGrp('tdb_weight2FFG', numberOfFields=1, label='Weight 2', v1=-1.0)
    overlapFFG = cmds.floatFieldGrp('tdb_overlapFFG', numberOfFields=1, label='Overlap', v1=0.0)
    prefixTFG = cmds.textFieldGrp('tdb_prefixTFG', label='Prefix', text='')
    createB = cmds.button('tdb_createB', label='Create', c='glTools.ui.transformDrivenBlend.executeFromUI()')
    refreshB = cmds.button('tdb_refreshB', label='Refresh', c='glTools.ui.transformDrivenBlend.refreshUI()')
    cancelB = cmds.button('tdb_cancelB', label='Cancel', c='cmds.deleteUI(' + window + ')')

    # Popup Menus
    cmds.popupMenu('tdb_blendShapePUM', p=blendShapeTFG)
    cmds.popupMenu('tdb_target1PUM', p=target1TFG)
    cmds.popupMenu('tdb_target2PUM', p=target2TFG)
    cmds.popupMenu('tdb_driveAttrPUM', p=driveAttrTFG)
    cmds.menuItem(label='Set from selected', c='glTools.ui.utils.loadChannelBoxSel("' + driveAttrTFG + '")')

    # Show Window
    refreshUI()
    cmds.showWindow(window)


def refreshUI():
    """
    """
    # Get UI input values
    blendShape = cmds.textFieldGrp('tdb_blendShapeTFG', q=True, text=True)
    target1 = cmds.textFieldGrp('tdb_target1TFG', q=True, text=True)
    target2 = cmds.textFieldGrp('tdb_target1TFG', q=True, text=True)

    # Update blendShape menu list
    blendShapeList = cmds.ls(type='blendShape')
    cmds.popupMenu('tdb_blendShapePUM', e=True, deleteAllItems=True)
    cmds.setParent('tdb_blendShapePUM', m=True)
    for item in blendShapeList:
        cmds.menuItem(label=item,
                    c='cmds.textFieldGrp("tdb_blendShapeTFG",e=True,text="' + item + '");glTools.ui.transformDrivenBlend.refreshUI()')

    # Check BlendShape
    if blendShape and cmds.objExists('blendShape') and (cmds.objectType(blendShape) == 'blendShape'):
        targetList = cmds.listAttr(blendShape + '.w', m=True)
        cmds.popupMenu('tdb_target1PUM', e=True, deleteAllItems=True)
        cmds.popupMenu('tdb_target2PUM', e=True, deleteAllItems=True)
        for target in targetList:
            targetCon = cmds.listConnections(blendShape + '.' + target, s=True, d=False)
            if target == target1: targetCon = True
            if target == target2: targetCon = True
            cmds.setParent('tdb_target1PUM', m=True)
            cmds.menuItem(label=target,
                        c='cmds.textFieldGrp("tdb_target1TFG",e=True,text="' + target + '");glTools.ui.transformDrivenBlend.refreshUI()',
                        en=not bool(targetCon))
            cmds.setParent('tdb_target2PUM', m=True)
            cmds.menuItem(label=target,
                        c='cmds.textFieldGrp("tdb_target1TFG",e=True,text="' + target + '");glTools.ui.transformDrivenBlend.refreshUI()',
                        en=not bool(targetCon))


def executeFromUI():
    """
    """
    # Set Default Values
    minValue = 0.0
    maxValue = 1.0

    # Get UI input values
    driveAttr = cmds.textFieldGrp('tdb_driveAttrTFG', q=True, text=True)
    blendShape = cmds.textFieldGrp('tdb_blendShapeTFG', q=True, text=True)
    target1 = cmds.textFieldGrp('tdb_target1TFG', q=True, text=True)
    target2 = cmds.textFieldGrp('tdb_target1TFG', q=True, text=True)
    weight1 = cmds.floatFieldGrp('tdb_weight1FFG', q=True, v1=True)
    weight2 = cmds.floatFieldGrp('tdb_weight2FFG', q=True, v1=True)
    overlap = cmds.floatFieldGrp('tdb_overlapFFG', q=True, v1=True)
    prefix = cmds.textFieldGrp('tdb_prefixTFG', q=True, text=True)

    # Check Arguments
    if not blendShape: raise Exception('No blendShape specified!')
    if not target1: raise Exception('Target 1 not specified!')
    if target1 and target2:
        minValue = weight1
        maxValue = weight2
    else:
        maxValue = weight1

    # Execute Command
    if target1 and target2:
        glTools.tools.transformDrivenBlend.drive2Shapes(blendShape, target1, target2, driveAttr, minValue, maxValue,
                                                        overlap, prefix)
    else:
        glTools.tools.transformDrivenBlend.driveShape(blendShape, target, driveAttr, minValue, maxValue, prefix)
