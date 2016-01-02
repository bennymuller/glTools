import maya.cmds as cmds


def freezeCtrlScale(ctrl):
    """
    """
    grp = cmds.listRelatives(ctrl, p=True)[0]
    mdn = ctrl.replace('ctrl', 'multiplyDivide')
    mdn = cmds.createNode('multiplyDivide', n=mdn)
    cmds.connectAttr(grp + '.s', mdn + '.input2', f=True)
    cmds.setAttr(mdn + '.input1', 1.0, 1.0, 1.0)
    cmds.setAttr(mdn + '.operation', 2)
    cmds.connectAttr(mdn + '.output', ctrl + '.s', f=True)


def unfreezeCtrlScale(ctrl):
    """
    """
    mdn = cmds.listConnections(ctrl + '.s', s=True, d=False)
    if mdn: cmds.delete(mdn)


def setTranslateLimits(ctrl, tx=True, ty=True, tz=True):
    """
    """
    if (tx): cmds.transformLimits(ctrl, tx=(-1.0, 1.0), etx=(1, 1))
    if (ty): cmds.transformLimits(ctrl, ty=(-1.0, 1.0), ety=(1, 1))
    if (tz):   cmds.transformLimits(ctrl, tz=(-1.0, 1.0), etz=(1, 1))


def driveShape(blendShape, target, driveAttr, minValue=-1.5, maxValue=1.5, prefix=''):
    """
    @param blendShape: The blendShape node to drive
    @type blendShape: str
    @param target: The blendShape target that will be driven
    @type target: str
    @param driveAttr: The object.attribute that will drive the blendShape target
    @type driveAttr: str
    @param minValue: Minimum value for the blendShape target
    @type minValue: float
    @param maxValue: Maximum value for the blendShape target
    @type maxValue: float
    @param prefix: Name prefix for all created nodes
    @type prefix: str
    """
    # Check drive object
    driveObj = cmds.ls(driveAttr, o=True)
    if not driveObj:
        raise Exception('Invalid drive attribute "driveAttr"!')
    else:
        driveObj = driveObj[0]
    # Check drive attribute
    driveAttr = driveAttr.replace(driveObj + '.', '')
    if not cmds.objExists(driveObj + '.' + driveAttr):
        cmds.addAttr(driveObj, ln=driveAttr, min=minValue, max=maxValue, dv=0, k=True)

    # Create remapValue node
    remapNode = cmds.createNode('remapValue', n=prefix + '_remapValue')

    # Connect drive attribute
    cmds.connectAttr(driveObj + '.' + driveAttr, remapNode + '.inputValue')

    # Remap input value to target limits
    cmds.setAttr(remapNode + '.inputMin', minValue)
    cmds.setAttr(remapNode + '.inputMax', maxValue)
    cmds.setAttr(remapNode + '.outputMin', minValue)
    cmds.setAttr(remapNode + '.outputMax', maxValue)

    # Connect to blendShape target attributes
    cmds.connectAttr(remapNode + '.outValue', blendShape + '.' + target)

    # Return result
    return remapNode


def drive2Shapes(blendShape, target1, target2, driveAttr, minValue=-1.5, maxValue=1.5, overlap=0.0, prefix=''):
    """
    @param blendShape: The blendShape node to drive
    @type blendShape: str
    @param target1: The blendShape target that will be driven with negative value
    @type target1: str
    @param target2: The blendShape target that will be driven with positive value
    @type target2: str
    @param driveAttr: The object.attribute that will drive the blendShape targets
    @type driveAttr: str
    @param minValue: Minimum value to drive target1
    @type minValue: float
    @param maxValue: Maximum value to drive target2
    @type maxValue: float
    @param overlap: The amount that the 2 blendShape target will overlap at a neutral drive value
    @type overlap: float
    @param prefix: Name prefix for all created nodes
    @type prefix: str
    """
    # Check drive object
    driveObj = cmds.ls(driveAttr, o=True)
    if not driveObj:
        raise Exception('Invalid drive attribute "driveAttr"!')
    else:
        driveObj = driveObj[0]
    # Check drive attribute
    driveAttr = driveAttr.replace(driveObj + '.', '')
    if not cmds.objExists(driveObj + '.' + driveAttr):
        cmds.addAttr(driveObj, ln=driveAttr, min=minValue, max=maxValue, dv=0, k=True)

    # Create remapValue nodes
    remapNode1 = cmds.createNode('remapValue', n=prefix + '_target1neg_remapValue')
    remapNode2 = cmds.createNode('remapValue', n=prefix + '_target2pos_remapValue')

    # Connect drive attribute
    cmds.connectAttr(driveObj + '.' + driveAttr, remapNode1 + '.inputValue')
    cmds.connectAttr(driveObj + '.' + driveAttr, remapNode2 + '.inputValue')

    # Remap input value to target limits
    cmds.setAttr(remapNode1 + '.inputMin', minValue)
    cmds.setAttr(remapNode1 + '.inputMax', overlap)
    cmds.setAttr(remapNode1 + '.outputMin', -minValue)
    cmds.setAttr(remapNode1 + '.outputMax', 0.0)

    cmds.setAttr(remapNode2 + '.inputMin', -overlap)
    cmds.setAttr(remapNode2 + '.inputMax', maxValue)
    cmds.setAttr(remapNode2 + '.outputMin', 0.0)
    cmds.setAttr(remapNode2 + '.outputMax', maxValue)

    # Connect to blendShape target attributes
    cmds.connectAttr(remapNode1 + '.outValue', blendShape + '.' + target1)
    cmds.connectAttr(remapNode2 + '.outValue', blendShape + '.' + target2)

    # Return result
    return [remapNode1, remapNode2]
