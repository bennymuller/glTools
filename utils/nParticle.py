import maya.cmds as cmds
import glTools.utils.base
import glTools.utils.shape


def softBody(geometry, prefix=''):
    """
    """
    # Check prefix
    if not prefix:
        prefix = geometry

    # Check geometry
    geometryType = cmds.objectType(geometry)
    if geometryType == 'transform':
        geometryTransform = geometry
        geometryShapes = glTools.utils.shape.getShapes(geometry, nonIntermediates=True, intermediates=False)
        if not geometryShapes: raise Exception('No valid geometry shapes found!')
        geometryShape = geometryShapes[0]
    else:
        geometryTransform = cmds.listRelatives(geometry, p=True)[0]
        geometryShape = geometry

    # Check geometry type
    geometryType = cmds.objectType(geometryShape)
    if geometryType == 'mesh':
        geometryAttribute = 'inMesh'
    elif geometryType == 'nurbsCurve':
        geometryAttribute = 'create'
    elif geometryType == 'nurbsSurface':
        geometryAttribute = 'create'
    else:
        raise Exception('Invalid geometry type (' + geometryType + ')!')

    # Get geometry points
    mPtList = glTools.utils.base.getMPointArray(geometry)
    ptList = [(i[0], i[1], i[2]) for i in mPtList]

    # Create nParticles
    nParticle = cmds.nParticle(p=ptList, n=prefix + '_nParticle')

    # Connect to geometry
    cmds.connectAttr(geometryTransform + '.worldMatrix[0]', nParticle + '.targetGeometryWorldMatrix', f=True)
    cmds.connectAttr(nParticle + '.targetGeometry', geometryShape + '.' + geometryAttribute, f=True)

    # Return result
    return nParticle
