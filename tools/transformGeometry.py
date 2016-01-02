import maya.cmds as cmds
import glTools.utils.shape
import glTools.utils.stringUtils


def create(geo, transform, prefix=None):
    """
    @param geo: Geometry to transform.
    @type geo: str
    @param transform: Transform node that drives geometry transformation.
    @type transform: str
    @param prefix: Naming prefix. If None, prefix will be derived from geo name.
    @type prefix: str
    """
    # ==========
    # - Checks -
    # ==========

    if not cmds.objExists(geo):
        raise Exception('Geometry "' + geo + '" does not exist! Unable to transform geometry...')
    if not cmds.objExists(transform):
        raise Exception('Transform "' + transform + '" does not exist! Unable to transform geometry...')
    if not prefix:
        prefix = glTools.utils.stringUtils.stripSuffix(geo)

    # ======================
    # - Transform Geometry -
    # ======================

    # Find Geometry Shapes to Transform
    geoShapes = cmds.ls(cmds.listRelatives(geo, s=True, ni=True) or [], type=['mesh', 'nurbsCurve', 'nurbsSurface']) or []
    if not geoShapes:
        raise Exception('Object "' + geo + '" has no geometry shape! Unable to transform geometry...')

    # Transform Geometry Shapes
    transformGeoList = []
    for i in range(len(geoShapes)):

        # Create Transform Geometry Node
        ind = glTools.utils.stringUtils.alphaIndex(i)
        transformGeo = cmds.createNode('transformGeometry', n=prefix + '_' + ind + '_transformGeometry')
        cmds.connectAttr(transform + '.worldMatrix[0]', transformGeo + '.transform', f=True)

        # Check Shape Input
        shapeType = cmds.objectType(geoShapes[i])
        shapeInputSrc = glTools.utils.shape.shapeInputSrc(geoShapes[i])
        shapeInputAttr = glTools.utils.shape.shapeInputAttr(geoShapes[i])
        shapeOutputAttr = glTools.utils.shape.shapeOutputAttr(geoShapes[i])

        # Connect Transform Geometry Node
        if shapeInputSrc:

            # -- Existing Input Source
            cmds.connectAttr(shapeInputSrc, transformGeo + '.inputGeometry', f=True)
            cmds.connectAttr(transformGeo + '.outputGeometry', geoShapes[i] + '.' + shapeInputAttr, f=True)

        else:

            # -- No Input Source
            geoShapeOrig = cmds.rename(geoShapes[i], geoShapes[i] + 'Orig')
            geoShape = cmds.createNode(shapeType, n=geoShapes[i], p=geo)
            shapeOutputAttr = glTools.utils.shape.shapeOutputAttr(geoShapes[i])
            cmds.connectAttr(geoShapeOrig + '.' + shapeOutputAttr, transformGeo + '.inputGeometry', f=True)
            cmds.connectAttr(transformGeo + '.outputGeometry', geoShape + '.' + shapeInputAttr, f=True)
            cmds.setAttr(geoShapeOrig + '.intermediateObject', True)

            # Apply Overrides
            overrideAttrs = ['template',
                             'overrideEnabled',
                             'overrideDisplayType',
                             'overrideLevelOfDetail',
                             'overrideVisibility',
                             'overrideColor']
            for overrideAttr in overrideAttrs:
                cmds.setAttr(geoShape + '.' + overrideAttr, cmds.getAttr(geoShapeOrig + '.' + overrideAttr))

        # Append Output List
        transformGeoList.append(transformGeo)

    # =================
    # - Return Result -
    # =================

    return transformGeoList
