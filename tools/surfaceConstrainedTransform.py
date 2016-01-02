import maya.cmds as cmds


def surfaceConstraint(obj, surface, point=True, orient=True, normalAxis='x', upAxis='y', upMode='', upVector=(0, 1, 0),
                      upObject='', pointMode=0, prefix=''):
    """
    @param obj: Target object that the surface constrained transform will goal to.
    @type obj: str
    @param surface: Surface to constrain to
    @type surface: str
    @param point: Constrain point (translate)
    @type point: bool
    @param orient: Constrain orient (rotate)
    @type orient: bool
    @param normalAxis: Constrained transform axis to align with surface normal
    @type normalAxis: str
    @param upAxis: Constrained transform axis to align with defined upVector
    @type upAxis: str
    @param upMode: Constraint upVector mode. Valid values are 'scene', 'object', 'objectrotation', 'vector' or 'none'.
    @type upMode: str
    @param upVector: Constraint upVector.
    @type upVector: list or tuple
    @param upObject: Constraint upVector object. Only needed for 'object' or 'objectrotation' upVector modes.
    @type upObject: str
    @param pointMode: Point (translate) constraint mode. 0 = geometryConstraint, 1 = boundaryConstraint.
    @type pointMode: int
    @param prefix: Name prefix for newly created nodes
    @type prefix: str
    """
    # Build axis dictionary
    axisDict = {'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1), '-x': (-1, 0, 0), '-y': (0, -1, 0), '-z': (0, 0, -1)}

    # ==========
    # - Checks -
    # ==========

    if not cmds.objExists(obj):
        raise Exception('Object "' + obj + '" does not exist!')

    if not cmds.objExists(surface):
        raise Exception('Surface "' + surface + '" does not exist!')

    if not axisDict.keys().count(normalAxis):
        raise Exception('Invalid normal axis specified "' + normalAxis + '"!')

    if not axisDict.keys().count(upAxis):
        raise Exception('Invalid up axis specified "' + upAxis + '"!')

    if ((upMode == 'object') or (upMode == 'objectrotation')) and not cmds.objExists(upObject):
        raise Exception('Invalid up object specified "' + upObject + '"!')

    # ===============================
    # - Create Constraint Transform -
    # ===============================

    surfConnNode = cmds.createNode('transform', n=prefix + '_surfConn_grp')

    # ================================
    # - Constraint point (translate) -
    # ================================

    if point:

        if pointMode == 0:

            # Geometry Constraint
            pntConn = cmds.pointConstraint(obj, surfConnNode, n=prefix + '_pointConstraint')
            geoConn = cmds.geometryConstraint(surface, surfConnNode, n=prefix + '_geometryConstraint')

        else:

            # =======================
            # - Boundary Constraint -
            # =======================

            # World Position (vectorProduct)
            vecProduct = cmds.createNode('vectorProduct', n=prefix + '_worldPos_vectorProduct')
            cmds.setAttr(vecProduct + '.operation', 4)  # Point Matrix Product
            cmds.connectAttr(obj + '.worldMatrix', vecProduct + '.matrix', f=True)

            # Closest Point On Surface
            cposNode = cmds.createNode('closestPointOnSurface', n=prefix + '_surfacePos_closestPointOnSurface')
            cmds.connectAttr(surface + '.worldSpace[0]', cposNode + '.inputSurface', f=True)
            cmds.connectAttr(vecProduct + '.output', cposNode + '.inPoint', f=True)

            # Point On Surface Info
            posiNode = cmds.createNode('pointOnSurfaceInfo', n=prefix + '_surfacePt_pointOnSurfaceInfo')
            cmds.connectAttr(surface + '.worldSpace[0]', cposNode + '.inputSurface', f=True)
            cmds.connectAttr(cposNode + '.parameterU', posiNode + '.parameterU', f=True)
            cmds.connectAttr(cposNode + '.parameterV', posiNode + '.parameterV', f=True)

            # Calculate Offset
            offsetNode = cmds.createNode('plusMinusAverage', n=prefix + '_surfaceOffset_plusMinusAverage')
            cmds.setAttr(offsetNode + '.operation', 2)  # Subtract
            cmds.connectAttr(vecProduct + '.output', offsetNode + '.input3D[0]', f=True)
            cmds.connectAttr(cposNode + '.position', offsetNode + '.input3D[1]', f=True)

            # Offset * Normal (dotProduct)
            dotProduct = cmds.createNode('vectorProduct', n=prefix + '_dotProduct_vectorProduct')
            cmds.setAttr(dotProduct + '.operation', 1)  # Dot Product
            cmds.connectAttr(offsetNode + '.ouput3D', dotProduct + '.input1', f=True)
            cmds.connectAttr(posiNode + '.normal', dotProduct + '.input2', f=True)

            # Boundary Condition
            condition = cmds.createNode('condition', n=prefix + '_condition')
            cmds.setAttr(condition + '.operation', 2)  # Greater Than
            cmds.connectAttr(dotProduct + '.outputX', condition + '.firstTerm', f=True)
            cmds.connectAttr(vecProduct + '.output', condition + '.colorIfTrue', f=True)
            cmds.connectAttr(cposNode + '.position', condition + '.colorIfFalse', f=True)

            # Connect to transform
            cmds.connectAttr(condition + '.outColor', surfConnNode + '.t', f=True)

    else:

        # Point Constraint
        pntConn = cmds.pointConstraint(obj, surfConnNode, n=prefix + '_pointConstraint')

    # =============================
    # - Constrain Orient (rotate) -
    # =============================

    if orient:

        # Normal Constraint
        norcmdsonn = cmds.normalConstraint(surface, surfConnNode, aim=axisDict[normalAxis], u=axisDict[upAxis], wut=upMode,
                                       wu=upVector, wuo=upObject, n=prefix + '_normalConstraint')

    else:

        # Orient Constraint
        oriConn = cmds.normalConstraint(obj, surfConnNode, n=prefix + '_orientConstraint')

    # =================
    # - Return Result -
    # =================

    return surfConnNode


def blendTarget(slaveTransform, driverAttr, attrMin=0.0, attrMax=1.0, translate=True, rotate=False, scale=False,
                prefix=''):
    """
    """
    # Checks
    if not cmds.objExists(slaveTransform):
        raise Exception('Slave transform "' + slaveTransform + '" does not exist!')
    if not cmds.objExists(driverAttr):
        raise Exception('Driver attribute "' + driverAttr + '" does not exist!')

    # Check blendTarget node
    if cmds.objExists(slaveTransform):
        pass

    # Create target locator
    targetLoc = cmds.spaceLocator(n=prefix + '_loc')[0]

    # Parent target locator
    slaveParent = cmds.listRelatives(slaveTransform, p=True, pa=True)
    if not slaveParent: raise Exception('Slave transform has no transform parent!')
    cmds.parent(targetLoc, slaveParent[0])

    # Check blendCombine nodes
    slaveTransConn = cmds.listConnections(slaveTransform + '.t', s=True, d=False)
    slaveRotateConn = cmds.listConnections(slaveTransform + '.r', s=True, d=False)
    slaveScaleConn = cmds.listConnections(slaveTransform + '.s', s=True, d=False)

#
