import maya.cmds as cmds
import glTools.utils.attribute
import glTools.utils.deformer


def isTangentBlend(tangentBlend):
    """
    Test if node is a valid tangentBlendDeformer
    @param tangentBlend: Name of tangentBlend node to query
    @type tangentBlend: str
    """
    # Check blendShape exists
    if not cmds.objExists(tangentBlend): return False
    # Check object type
    if cmds.objectType(tangentBlend) != 'tangentBlendDeformer':
        return False
    # Return result
    return True


def unlockTransform(node):
    """
    Unlock transform channels
    @param node: Transform to unlock channels for
    @type node: str
    """
    # Define attribute list
    attrList = ['tx', 'ty', 'tz', 't', 'rx', 'ry', 'rz', 'r', 'sx', 'sy', 'sz', 's']
    # Unlock attributes
    for attr in attrList:
        cmds.setAttr(node + '.' + attr, l=False)


def findTangentBlendDeformer(geo):
    """
    Return the tangentBlend deformer attached to the specified geometry
    @param geo: Geometry to find attached tangentBlend deformer for
    @type geo: str
    """
    # Get Geometry History
    tangentBlend = ''
    history = cmds.listHistory(geo)

    # Check for tangentBlendDeformer
    for i in range(len(history)):
        if (cmds.objectType(history[i], isAType='tangentBlendDeformer')):
            # Capture result
            tangentBlend = history[i]

    # Return result
    return tangentBlend


def findAffectedGeometry(tangentBlend):
    """
    @param tangentBlend:
    """
    # Check deformer
    if not isTangentBlend(tangentBlend):
        raise Exception('Object "' + tangentBlend + '" is not a valid tangentBlend deformer node!')

    # Get affected geometry
    geometry = glTools.utils.deformer.getAffectedGeometry(tangentBlend).keys()[0]

    # Return result
    return geometry


def geomAttrName(shapeNode):
    """
    @param shapeNode:
    """
    # Get shape attribute based on geometry type
    attrType = cmds.nodeType(shapeNode, api=True)
    if attrType == 'kNurbsCurve': return '.local'
    if attrType == 'kMesh': return '.outMesh'
    return '.'


def duplicateGeo(obj, name):
    """
    @param obj:
    @param name:
    @return:
    """
    # Duplicate Geometry
    dup = cmds.duplicate(obj, name=name)[0]

    # Removed unused shapes
    dupShapes = cmds.listRelatives(dup, s=True, ni=True)
    dupShapesAll = cmds.listRelatives(dup, s=True)
    deleteShapes = list(set(dupShapesAll) - set(dupShapes))
    cmds.delete(deleteShapes)

    # Unlock transforms
    unlockTransform(dup)

    # Return result
    return dup


def create(geo, name=''):
    """
    @param geo:
    @param name:
    @return:
    """
    # Load Plugin
    if not cmds.pluginInfo('tangentBlendDeformer', q=True, l=True):
        cmds.loadPlugin('tangentBlendDeformer')

    # Create Deformer
    if not name:
        name = geo + '_tangentBlendDeformer'
    tangentBlend = cmds.deformer(geo, type='tangentBlendDeformer', n=name)[0]

    # Return Result
    return tangentBlend


def connectPose(baseXForm, offsetXForm, deformer):
    """
    @param baseXForm:
    @param offsetXForm:
    @param deformer:
    @return:
    """
    # Get next available deformer index
    index = glTools.utils.attribute.nextAvailableMultiIndex(deformer + '.pose', useConnectedOnly=False)

    # Get pose geometry shapes
    baseShape = cmds.listRelatives(baseXForm, s=True, ni=True, pa=True)
    offsetShape = cmds.listRelatives(offsetXForm, s=True, ni=True, pa=True)

    # Connect pose base
    attrName = geomAttrName(baseShape[0])
    cmds.connectAttr(baseShape[0] + attrName, deformer + '.pose[' + str(index) + '].poseBaseMesh', f=True)
    # Connect pose offset
    attrName = geomAttrName(offsetShape[0])
    cmds.connectAttr(offsetShape[0] + attrName, deformer + '.pose[' + str(index) + '].poseOffsetMesh', f=True)

    # Return result
    return index


def addPose(tangentBlend, baseGeo='', offsetGeo='', poseName=''):
    """
    @param tangentBlend:
    @param baseGeo:
    @param offsetGeo:
    @param poseName:
    """
    # Define suffix tags
    tangentBlend_baseTag = '_poseBase'
    tangentBlend_offsetTag = '_poseOffset'

    # Get connected geometry
    geo = findAffectedGeometry(tangentBlend)

    # Check pose geometry
    if not baseGeo: baseGeo = duplicateGeo(geo, geo + tangentBlend_baseTag)
    if not offsetGeo: baseGeo = duplicateGeo(geo, geo + tangentBlend_offsetTag)

    # Connect to deformer
    poseIndex = connectPose(baseGeo, offsetGeo, tangentBlend)

    # Alias pose name and set keyable
    if poseName:
        cmds.aliasAttr(poseName, tangentBlend + '.pose[' + str(poseIndex) + '].poseWeight')
        cmds.setAttr(tangentBlend + '.pose[' + str(poseIndex) + '].poseWeight', cb=True)
        cmds.setAttr(tangentBlend + '.pose[' + str(poseIndex) + '].poseWeight', k=True)

    return [baseGeo, offsetGeo]
