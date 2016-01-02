import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import glTools.utils.surface
import glTools.utils.mathUtils
import glTools.utils.stringUtils
import glTools.tools.namingConvention


def add(surface, targetList, surfacePointsNode='', alignTo='u', rotate=True, tangentUAxis='x', tangentVAxis='y',
        prefix=''):
    """
    @param surface: Nurbs surface to constrain to
    @type surface: str
    @param targetList: List of target transforms/positions/coordinates
    @type targetList: list
    @param surfacePointsNode: Name for a new or existing surfacePoints node
    @type surfacePointsNode: str
    @param alignTo: Surface direction to align to. This option is ignored if the specified surface points node already exists
    @type alignTo: str
    @param rotate: Calculate rotation
    @type rotate: bool
    @param tangentUAxis: Transform axis to align with the surface U tangent
    @type tangentUAxis: str
    @param tangentVAxis: Transform axis to align with the surface V tangent
    @type tangentVAxis: str
    @param prefix: Name prefix for newly created nodes
    @type prefix: str
    """
    # Check surface
    if not glTools.utils.surface.isSurface(surface):
        raise Exception('Object "" is not a valid nurbs surface!!')

    # Check prefix
    if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(surface)

    # Check targetList
    if not targetList: raise Exception('Invalid target list!!')

    # Check surfacePoints node
    if not surfacePointsNode:
        surfacePointsNode = prefix + 'surfacePoints'
    if cmds.objExists(surfacePointsNode):
        if not cmds.objectType(surfacePointsNode) == 'surfacePoints':
            raise Exception('Object "' + surfacePointsNode + '" is not a valid surfacePoints node!!')
    else:
        # Create new surface points node
        surfacePointsNode = cmds.createNode('surfacePoints', n=surfacePointsNode)
        cmds.connectAttr(surface + '.worldSpace[0]', surfacePointsNode + '.inputSurface')
        # Apply settings
        cmds.setAttr(surfacePointsNode + '.calculateRotation', rotate)
        if alignTo == 'u':
            cmds.setAttr(surfacePointsNode + '.alignTo', 0)
        else:
            cmds.setAttr(surfacePointsNode + '.alignTo', 1)
        # Tangent Axis
        axisDict = {'x': 0, 'y': 1, 'z': 2, '-x': 3, '-y': 4, '-z': 5}
        cmds.setAttr(surfacePointsNode + '.tangentUAxis', axisDict[tangentUAxis])
        cmds.setAttr(surfacePointsNode + '.tangentVAxis', axisDict[tangentVAxis])

    # Find next available input index
    nextIndex = getNextAvailableIndex(surfacePointsNode)

    # Create surface constraints
    transformList = []
    for i in range(len(targetList)):

        # Get current input index
        ind = glTools.utils.stringUtils.stringIndex(i + 1, 2)

        # Initialize UV parameter variable
        uv = (0.0, 0.0)
        pos = (0.0, 0.0, 0.0)
        # Get target surface point for current target
        if type(targetList[i]) == str or type(targetList[i]) == unicode:
            if not cmds.objExists(targetList[i]): raise Exception(
                'Target list object "' + targetList[i] + '" does not exist')
            pos = cmds.pointPosition(targetList[i])
            uv = glTools.utils.surface.closestPoint(surface, pos)
        elif type(targetList[i]) == tuple or type(targetList[i]) == list:
            if len(targetList[i]) == 3:
                pos = targetList[i]
                uv = glTools.utils.surface.closestPoint(surface, pos)
            elif len(targetList[i]) == 2:
                uv = targetList[i]
                pos = cmds.pointOnSurface(surface, u=uv[0], v=uv[1], p=True)
        paramU = uv[0]
        paramV = uv[1]

        # Get surface point information
        pnt = cmds.pointOnSurface(surface, u=paramU, v=paramV, p=True)
        normal = cmds.pointOnSurface(surface, u=paramU, v=paramV, nn=True)
        tangentU = cmds.pointOnSurface(surface, u=paramU, v=paramV, ntu=True)
        tangentV = cmds.pointOnSurface(surface, u=paramU, v=paramV, ntv=True)

        # Clamp param to safe values
        minU = cmds.getAttr(surface + '.minValueU')
        maxU = cmds.getAttr(surface + '.maxValueU')
        minV = cmds.getAttr(surface + '.minValueV')
        maxV = cmds.getAttr(surface + '.maxValueV')
        if paramU < (minU + 0.001):
            paramU = minU
        elif paramU > (maxU - 0.001):
            paramU = maxU
        if paramV < (minV + 0.001):
            paramV = minV
        elif paramV > (maxV - 0.001):
            paramV = maxV

        # Create constraint transform
        transform = prefix + '_surfacePoint' + ind + '_transform'
        transform = cmds.createNode('transform', n=transform)
        transformList.append(transform)

        # Add param attributes
        cmds.addAttr(transform, ln='param', at='compound', numberOfChildren=2)
        cmds.addAttr(transform, ln='paramU', at='double', min=minU, max=maxU, dv=paramU, k=True, p='param')
        cmds.addAttr(transform, ln='paramV', at='double', min=minV, max=maxV, dv=paramV, k=True, p='param')

        # Connect to surfacePoints node
        # cmds.setAttr(surfacePointsNode+'.offset['+ind+']',offsetU,offsetV,offsetN)
        cmds.connectAttr(transform + '.param', surfacePointsNode + '.param[' + ind + ']', f=True)
        cmds.connectAttr(transform + '.parentMatrix', surfacePointsNode + '.targetMatrix[' + ind + ']', f=True)

        # Connect to transform
        cmds.connectAttr(surfacePointsNode + '.outTranslate[' + ind + ']', transform + '.translate', f=True)
        if rotate: cmds.connectAttr(surfacePointsNode + '.outRotate[' + ind + ']', transform + '.rotate', f=True)

    # Return result
    return (surfacePointsNode, transformList)


def getNextAvailableIndex(surfacePointsNode):
    """
    @param surfacePointsNode: SurfacePoints node to query
    @type surfacePointsNode: str
    """
    # Get MObject
    sel = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getSelectionListByName(surfacePointsNode, sel)
    obj = OpenMaya.MObject()
    sel.getDependNode(0, obj)

    # Get param plug
    paramPlug = OpenMaya.MFnDependencyNode(obj).findPlug('param')

    # Get valid index list
    indexList = OpenMaya.MIntArray()
    paramPlug.getExistingArrayAttributeIndices(indexList)

    # Determine next available index
    nextIndex = 0
    if indexList.length(): nextIndex = indexList[-1] + 1

    # Return next available index
    return nextIndex
