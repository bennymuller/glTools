import maya.cmds as cmds
import copy


def setDrivenKeyToRemapValue(anicmdsurve, remapValueNode='', interpType=3, deleteAnicmdsurve=True, lockPosition=True,
                             lockValue=False):
    """
    Convert a set driven key setup to a remapValue node.
    Each key on the anicmdsurve node is represented as widget on the remapValue ramp control.
    Incoming and outgoing curve connections will be replaced with equivalent remapValue connections.
    @param anicmdsurve: The anicmdsurve to convert to a remapValue node
    @type anicmdsurve: str
    @param remapValueNode: Name an existing remapValue node to use instead of creating a new one.
    @type remapValueNode: str
    @param interpType: Default ramp interpolation type.
    @type interpType: int
    @param deleteAnicmdsurve: Delete anicmdsurve node after disconnection
    @type deleteAnicmdsurve: bool
    @param lockPosition: Lock ramp widget position values
    @type lockPosition: bool
    @param lockValue: Lock ramp widget float values
    @type lockValue: bool
    """
    # Checks
    if not cmds.objExists(anicmdsurve):
        raise Exception('Anicmdsurve node "' + anicmdsurve + '" does not exist!!')
    if remapValueNode and not cmds.objExists(remapValueNode):
        raise Exception('RemapValue node "' + remapValueNode + '" does not exist!!')

    # Get connections to anicmdsurve
    inConn = cmds.listConnections(anicmdsurve + '.input', s=True, d=False, p=True)
    outConn = cmds.listConnections(anicmdsurve + '.output', s=False, d=True, p=True)

    # Get keyframe data
    valList = cmds.keyframe(anicmdsurve, q=True, vc=True)
    floatList = cmds.keyframe(anicmdsurve, q=True, fc=True)

    # Get min/max input and output values
    orderValList = copy.deepcopy(valList)
    orderFloatList = copy.deepcopy(floatList)
    orderValList.sort()
    orderFloatList.sort()
    minVal = orderValList[0]
    maxVal = orderValList[-1]
    minFloat = orderFloatList[0]
    maxFloat = orderFloatList[-1]

    # Create remapValue node
    if not remapValueNode:
        remapValueNode = cmds.createNode('remapValue', n=anicmdsurve + '_remapValue')

    # Set Remap attribute values
    cmds.setAttr(remapValueNode + '.inputMin', minFloat)
    cmds.setAttr(remapValueNode + '.inputMax', maxFloat)
    cmds.setAttr(remapValueNode + '.outputMin', minVal)
    cmds.setAttr(remapValueNode + '.outputMax', maxVal)

    # Remove existing ramp widgets
    indexList = range(cmds.getAttr(remapValueNode + '.value', s=True))
    indexList.reverse()
    for i in indexList:
        cmds.removeMultiInstance(remapValueNode + '.value[' + str(i) + ']', b=True)

    # Set ramp widgets based on keys
    valRange = maxVal - minVal
    floatRange = maxFloat - minFloat
    # Check zero values
    if valRange < 0.0001: valRange = 0.0001
    if floatRange < 0.0001: floatRange = 0.0001
    # Iterate through keys
    for i in range(len(valList)):
        val = (valList[i] - minVal) / valRange
        flt = (floatList[i] - minFloat) / floatRange
        cmds.setAttr(remapValueNode + '.value[' + str(i) + '].value_Position', flt)
        cmds.setAttr(remapValueNode + '.value[' + str(i) + '].value_FloatValue', val)
        cmds.setAttr(remapValueNode + '.value[' + str(i) + '].value_Interp', interpType)
        if lockPosition:
            cmds.setAttr(remapValueNode + '.value[' + str(i) + '].value_Position', l=True)
        if lockValue:
            cmds.setAttr(remapValueNode + '.value[' + str(i) + '].value_FloatValue', l=True)

    # Replace anicmdsurve connections
    cmds.connectAttr(inConn[0], remapValueNode + '.inputValue', f=True)
    cmds.connectAttr(remapValueNode + '.outValue', outConn[0], f=True)

    # Delete unused anicmdsurve
    if deleteAnicmdsurve: cmds.delete(anicmdsurve)

    # Return result
    return remapValueNode
