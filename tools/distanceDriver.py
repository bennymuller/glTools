import maya.cmds as cmds
import glTools.utils.stringUtils
import glTools.utils.transform


def addDistanceAttrs(attrObject, dist=0.0):
    """
    Add basic distance attributes to the specified object
    @param attrObject: Object to add distance attributes to
    @type attrObject: str
    @param dist: Rest distance value
    @type dist: int or float
    """
    # ==========
    # - Checks -
    # ==========

    if not cmds.objExists(attrObject):
        raise Exception('Attribute object "' + attrObject + '" does not exist!')

    # ===========================
    # - Add Distance Attributes -
    # ===========================

    if not cmds.attributeQuery('distance', n=attrObject, ex=True):
        cmds.addAttr(attrObject, ln='distance', min=0, dv=dist, k=True)
    if not cmds.attributeQuery('restDistance', n=attrObject, ex=True):
        cmds.addAttr(attrObject, ln='restDistance', min=0, dv=dist, k=True)

    # =================
    # - Return Result -
    # =================

    return attrObject + '.distance'


def buildDistanceNode(pt1,
                      pt2,
                      prefix=None):
    """
    Build distance node between 2 specified transforms.
    @param pt1: Transform 1 in distance calculation
    @type pt1: str
    @param pt2: Transform 2 in distance calculation
    @type pt2: str
    """
    # ==========
    # - Checks -
    # ==========

    if not cmds.objExists(pt1): raise Exception('Point 1 "' + pt1 + '" does not exist!')
    if not glTools.utils.transform.isTransform(pt1): raise Exception('Point 1 "' + pt1 + '" is not a valid tranform!')
    if not cmds.objExists(pt2): raise Exception('Point 2 "' + pt2 + '" does not exist!')
    if not glTools.utils.transform.isTransform(pt2): raise Exception('Point 2 "' + pt2 + '" is not a valid tranform!')

    # ========================
    # - Build Distance Setup -
    # ========================

    distNode = cmds.createNode('distanceBetween', n=prefix + '_distanceBetween')
    cmds.connectAttr(pt1 + '.worldMatrix[0]', distNode + '.inMatrix1', f=True)
    cmds.connectAttr(pt2 + '.worldMatrix[0]', distNode + '.inMatrix2', f=True)

    # =================
    # - Return Result -
    # =================

    return distNode


def distanceSetup(pt1,
                  pt2,
                  attrObject=None,
                  prefix=None):
    """
    Create basic distance setup based on 2 specified transforms.
    @param pt1: Transform 1 in distance calculation
    @type pt1: str
    @param pt2: Transform 2 in distance calculation
    @type pt2: str
    @param attrObject: Object to add distance attributes to
    @type attrObject: str or None
    @param prefix: Naming prefix
    @type prefix: str or None
    """
    # ==========
    # - Checks -
    # ==========

    if not cmds.objExists(pt1): raise Exception('Point 1 "' + pt1 + '" does not exist!')
    if not glTools.utils.transform.isTransform(pt1): raise Exception('Point 1 "' + pt1 + '" is not a valid tranform!')
    if not cmds.objExists(pt2): raise Exception('Point 2 "' + pt2 + '" does not exist!')
    if not glTools.utils.transform.isTransform(pt2): raise Exception('Point 2 "' + pt2 + '" is not a valid tranform!')

    if attrObject:
        if not cmds.objExists(attrObject):
            raise Exception('Attribute object "' + attrObject + '" does not exist!')

    if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(pt1)

    # ========================
    # - Build Distance Setup -
    # ========================

    distNode = cmds.createNode('distanceBetween', n=prefix + '_distanceBetween')
    cmds.connectAttr(pt1 + '.worldMatrix[0]', distNode + '.inMatrix1', f=True)
    cmds.connectAttr(pt2 + '.worldMatrix[0]', distNode + '.inMatrix2', f=True)
    dist = cmds.getAttr(distNode + '.distance')

    distAttr = None
    if attrObject:
        distAttr = addDistanceAttrs(attrObject, dist)
        cmds.connectAttr(distNode + '.distance', distAttr, f=True)
    else:
        for attrObject in [pt1, pt2]:
            distAttr = addDistanceAttrs(attrObject, dist)
            cmds.connectAttr(distNode + '.distance', distAttr, f=True)

    # =================
    # - Return Result -
    # =================

    return distAttr, distNode


def remapDistance(distNode,
                  minDist=None,
                  maxDist=None,
                  minValue=None,
                  maxValue=None,
                  restValue=None,
                  attrObject=None,
                  interpType=3,
                  prefix=None):
    """
    Remap the output of the specified distance node.
    @param distNode: distanceBetween node to remap output from.
    @type distNode: str
    @param minDist: Minimum distance
    @type minDist: float or None
    @param maxDist: Maximum distance
    @type maxDist: float or None
    @param minValue: Minimum output value
    @type minValue: float
    @param maxValue: Maximum output value
    @type maxValue: float
    @param restValue: Rest distance output value
    @type restValue: float or None
    @param attrObject: Object to add remap output attributes to
    @type attrObject: str or None
    @param interpType: Remap interpolation type. 0=None, 1=Linear, 2=Smooth, 3=Spline
    @type interpType: int
    @param prefix: Naming prefix
    @type prefix: str or None
    """
    # ==========
    # - Checks -
    # ==========

    # Check Attribute Object
    if attrObject:
        if not cmds.objExists(attrObject):
            raise Exception('Attribute object "' + attrObject + '" does not exist!')
    else:
        attrObject = distNode

    # Min/Max Value
    if minValue == None: minValue = restValue
    if maxValue == None: maxValue = restValue

    # ========================
    # - Build Distance Remap -
    # ========================

    # Get Distance
    dist = cmds.getAttr(distNode + '.distance')
    distAttr = addDistanceAttrs(attrObject, dist)
    try:
        cmds.connectAttr(distNode + '.distance', distAttr, f=True)
    except:
        print('Distance already connected...skipping!')

    # Add Min/Max Distance Attrs
    if minDist == None: minDist = 0
    if not cmds.objExists(attrObject + '.minDistance'):
        cmds.addAttr(attrObject, ln='minDistance', min=0, max=dist, dv=minDist, k=True)
    if maxDist == None: maxDist = dist * 2
    if not cmds.objExists(attrObject + '.maxDistance'):
        cmds.addAttr(attrObject, ln='maxDistance', min=dist, dv=maxDist, k=True)

    # Add Rest Value Attr
    if not restValue == None:
        if not cmds.objExists(attrObject + '.restValue'):
            cmds.addAttr(attrObject, ln='restValue', dv=restValue, k=True)

    # Add Min/Max Value Attr
    if not cmds.attributeQuery('minValue', n=attrObject, ex=True):
        cmds.addAttr(attrObject, ln='minValue', dv=minValue, k=True)
    if not cmds.attributeQuery('maxValue', n=attrObject, ex=True):
        cmds.addAttr(attrObject, ln='maxValue', dv=maxValue, k=True)

    # Build Remap Value
    remapNode = cmds.createNode('remapValue', n=prefix + '_remapValue')
    cmds.connectAttr(distAttr, remapNode + '.inputValue', f=True)

    cmds.setAttr(remapNode + '.value[0].value_Interp', interpType)  # Spline
    cmds.connectAttr(attrObject + '.minDistance', remapNode + '.value[0].value_Position', f=True)
    cmds.connectAttr(attrObject + '.minValue', remapNode + '.value[0].value_FloatValue', f=True)

    cmds.setAttr(remapNode + '.value[1].value_Interp', interpType)  # Spline
    cmds.connectAttr(attrObject + '.maxDistance', remapNode + '.value[1].value_Position', f=True)
    cmds.connectAttr(attrObject + '.maxValue', remapNode + '.value[1].value_FloatValue', f=True)

    # Set Rest Value
    if not restValue == None:
        cmds.setAttr(remapNode + '.value[2].value_Interp', interpType)  # Spline
        cmds.connectAttr(attrObject + '.restDistance', remapNode + '.value[2].value_Position', f=True)
        cmds.connectAttr(attrObject + '.restValue', remapNode + '.value[2].value_FloatValue', f=True)

    # Connect Output
    if not cmds.objExists(attrObject + '.outValue'):
        cmds.addAttr(attrObject, ln='outValue', dv=0.0, k=True)
    cmds.connectAttr(remapNode + '.outValue', attrObject + '.outValue', f=True)
    outAttr = attrObject + '.outValue'

    # =================
    # - Return Result -
    # =================

    return outAttr, remapNode


def distanceRemapOutput(pt1,
                        pt2,
                        minDist=None,
                        maxDist=None,
                        minValue=None,
                        maxValue=None,
                        restValue=None,
                        attrObject=None,
                        interpType=3,
                        prefix=None):
    """
    Create distance remap output setup for specified points.
    @param pt1: Transform 1 for distance setup
    @type pt1: str
    @param pt2: Transform 2 for distance setup
    @type pt2: str
    @param minDist: Minimum curve length
    @type minDist: float or None
    @param maxDist: Maximum curve length
    @type maxDist: float or None
    @param minValue: Minimum output value
    @type minValue: float
    @param maxValue: Maximum output value
    @type maxValue: float
    @param restValue: Rest length output value
    @type restValue: float or None
    @param attrObject: Object to add remap output attributes to
    @type attrObject: str or None
    @param interpType: Remap interpolation type. 0=None, 1=Linear, 2=Smooth, 3=Spline
    @type interpType: int
    @param prefix: Naming prefix
    @type prefix: str or None
    """
    # ==========
    # - Checks -
    # ==========

    if not cmds.objExists(pt1): raise Exception('Point 1 "' + pt1 + '" does not exist!')
    if not glTools.utils.transform.isTransform(pt1): raise Exception('Point 1 "' + pt1 + '" is not a valid tranform!')
    if not cmds.objExists(pt2): raise Exception('Point 2 "' + pt2 + '" does not exist!')
    if not glTools.utils.transform.isTransform(pt2): raise Exception('Point 2 "' + pt2 + '" is not a valid tranform!')

    # Check Attribute Object
    if attrObject:
        if not cmds.objExists(attrObject):
            raise Exception('Attribute object "' + attrObject + '" does not exist!')
    else:
        attrObject = pt1

    # Check Prefix
    if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(attrObject)

    # Check Distance Setup
    distNode = None
    distAttr = attrObject + '.length'
    if not cmds.objExists(distAttr):
        distAttr, distNode = distanceSetup(pt1, pt2, attrObject, prefix)
    else:
        distNode = cmds.listConnections(distAttr, s=True, d=False)
        if distNode: distNode = distNode[0]

    # Check Values
    if minDist == None: minDist = 0
    if restValue == None: restValue = 0
    if minValue == None: minValue = restValue
    if maxValue == None: maxValue = restValue

    # ========================
    # - Build Distance Remap -
    # ========================

    outAttr, remapNode = remapDistance(distNode,
                                       minDist,
                                       maxDist,
                                       minValue,
                                       maxValue,
                                       restValue,
                                       attrObject,
                                       interpType,
                                       prefix)

    # =================
    # - Return Result -
    # =================

    return outAttr, distNode, remapNode
