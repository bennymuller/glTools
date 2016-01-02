import maya.cmds as cmds
import glTools.utils.stringUtils
import glTools.utils.surface
import glTools.utils.transform


def sphereCollideTransform():
    pass


def cylinerCollideTransform():
    pass


def planeCollideTransform(targetTransform,
                          collidePlane=None,
                          collideTransform=None,
                          offsetFalloff=None,
                          distanceFalloff=None,
                          distanceAxis='XY',
                          prefix=None):
    """
    Setup a plane collide transform.
    Setup includes smooth offset falloff, distance falloff and collide weight attributes.
    Collision is based on the +Z axis of the collide plane transform.
    @param targetTransform: Target transform (or locator) that the collide transform will follow.
    @type targetTransform: str
    @param collidePlane: Collision plane transform. If None, creant new renderRect plane.
    @type collidePlane: str or None
    @param collideTransform: Collide transform that will collide with the plane. If None, creant new locator.
    @type collideTransform: str or None
    @param offsetFalloff: Calculate collision offset falloff. Offset falloff is calculated as collision local Z distance.
    @type offsetFalloff: float or None
    @param distanceFalloff: Calculate collision distance falloff. Distance falloff is calculated as collision local XY distance.
    @type distanceFalloff: float or None
    @param distanceAxis: Calculate collision distance falloff. Distance falloff is calculated as collision local XY distance.
    @type distanceAxis: float or None
    @param prefix: Naming prefix. If None, extracted from targetTransform
    @type prefix: str or None
    """
    # ==========
    # - Checks -
    # ==========

    # Check Target Transforms
    if not cmds.objExists(targetTransform):
        raise Exception('Target transform "' + targetTransform + '" does not exist!')
    if not glTools.utils.transform.isTransform(targetTransform):
        raise Exception('Object "' + targetTransform + '" is not a valid transform!')

    # Check Collide Plane
    if collidePlane:
        if not cmds.objExists(str(collidePlane)):
            raise Exception('Collide plane "' + collidePlane + '" does not exist!')
        if not glTools.utils.transform.isTransform(collidePlane):
            raise Exception('Object "' + collidePlane + '" is not a valid transform!')

    # Check Collide Transforms
    if collideTransform:
        if not cmds.objExists(str(collideTransform)):
            raise Exception('Collide transform "' + collideTransform + '" does not exist!')
        if not glTools.utils.transform.isTransform(collideTransform):
            raise Exception('Object "' + collideTransform + '" is not a valid transform!')

    # Check Distance Axis
    if distanceAxis: distanceAxis = distanceAxis.upper()

    # Check Prefix
    if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(targetTransform)

    # ===================
    # - Build Collision -
    # ===================

    # Build Collide Objects
    if not collideTransform:
        collideTransform = cmds.spaceLocator(n=prefix + '_collide_loc')[0]
    if not collidePlane:
        collidePlaneShape = cmds.createNode('renderRect')
        collidePlane = cmds.listRelatives(collidePlaneShape, p=True)[0]
        collidePlane = cmds.rename(collidePlane, prefix + '_collide_plane')

    # Add Collide Attributes
    if not cmds.attributeQuery('collideWeight', n=collidePlane, ex=True):
        cmds.addAttr(collidePlane, ln='collideWeight', min=0, max=1, dv=1, k=True)

    # Build Collide Nodes
    collideCondition = cmds.createNode('condition', n=prefix + '_collide_condition')
    collideBlend = cmds.createNode('blendColors', n=prefix + '_collideWeight_blendColors')
    worldToCollide = cmds.createNode('vectorProduct', n=prefix + '_worldToCollide_vectorProduct')
    cmds.setAttr(worldToCollide + '.operation', 4)  # Point Matrix Product
    collideToWorld = cmds.createNode('vectorProduct', n=prefix + '_collideToWorld_vectorProduct')
    cmds.setAttr(collideToWorld + '.operation', 4)  # Point Matrix Product
    worldToLocal = cmds.createNode('vectorProduct', n=prefix + '_worldToLocal_vectorProduct')
    cmds.setAttr(worldToLocal + '.operation', 4)  # Point Matrix Product

    # =========================
    # - Build Collide Network -
    # =========================

    # World To Collide
    cmds.connectAttr(collidePlane + '.worldInverseMatrix[0]', worldToCollide + '.matrix', f=True)
    if cmds.objExists(targetTransform + '.worldPosition[0]'):
        cmds.connectAttr(targetTransform + '.worldPosition[0]', worldToCollide + '.input1', f=True)
    else:
        localToWorld = cmds.createNode('vectorProduct', n=prefix + '_localToWorld_vectorProduct')
        cmds.setAttr(localToWorld + '.operation', 4)  # Point Matrix Product
        cmds.connectAttr(targetTransform + '.worldMatrix[0]', localToWorld + '.matrix', f=True)
        cmds.connectAttr(localToWorld + '.output', worldToCollide + '.input1', f=True)

    # Collide Condition
    cmds.connectAttr(worldToCollide + '.outputZ', collideCondition + '.firstTerm', f=True)
    cmds.setAttr(collideCondition + '.secondTerm', 0)
    cmds.setAttr(collideCondition + '.operation', 2)  # Greater Than
    cmds.connectAttr(worldToCollide + '.output', collideCondition + '.colorIfTrue', f=True)
    cmds.connectAttr(worldToCollide + '.outputX', collideCondition + '.colorIfFalseR', f=True)
    cmds.connectAttr(worldToCollide + '.outputY', collideCondition + '.colorIfFalseG', f=True)
    cmds.setAttr(collideCondition + '.colorIfFalseB', 0)

    # Collide Weight Blend
    cmds.connectAttr(collideCondition + '.outColor', collideBlend + '.color1', f=True)
    cmds.connectAttr(worldToCollide + '.output', collideBlend + '.color2', f=True)
    cmds.connectAttr(collidePlane + '.collideWeight', collideBlend + '.blender', f=True)

    # Collide To World
    cmds.connectAttr(collideBlend + '.output', collideToWorld + '.input1', f=True)
    cmds.connectAttr(collidePlane + '.worldMatrix[0]', collideToWorld + '.matrix', f=True)

    # World To Local
    cmds.connectAttr(collideToWorld + '.output', worldToLocal + '.input1', f=True)
    cmds.connectAttr(collideTransform + '.parentInverseMatrix[0]', worldToLocal + '.matrix', f=True)

    # Connect Output
    cmds.connectAttr(worldToLocal + '.output', collideTransform + '.translate', f=True)

    # ============================
    # - Calculate Offset Falloff -
    # ============================

    if offsetFalloff != None:

        # Add Collide Attributes
        if not cmds.attributeQuery('offsetFalloff', n=collidePlane, ex=True):
            cmds.addAttr(collidePlane, ln='offsetFalloff', min=0, dv=0.5, k=True)

        # Build Nodes
        falloffRemap = cmds.createNode('remapValue', n=prefix + '_offsetFalloff_remapValue')
        falloffMult = cmds.createNode('multDoubleLinear', n=prefix + '_offsetFalloff_multDoubleLinear')

        # Falloff Remap
        cmds.connectAttr(worldToCollide + '.outputZ', falloffRemap + '.inputValue', f=True)
        cmds.connectAttr(collidePlane + '.offsetFalloff', falloffRemap + '.inputMax', f=True)
        cmds.connectAttr(collidePlane + '.offsetFalloff', falloffRemap + '.outputMax', f=True)
        cmds.connectAttr(collidePlane + '.offsetFalloff', falloffMult + '.input1', f=True)
        cmds.setAttr(falloffMult + '.input2', -1)
        cmds.connectAttr(falloffMult + '.output', falloffRemap + '.inputMin', f=True)

        # Override Collide Condition
        cmds.connectAttr(collidePlane + '.offsetFalloff', collideCondition + '.secondTerm', f=True)
        cmds.connectAttr(falloffRemap + '.outValue', collideCondition + '.colorIfFalseB', f=True)

        # Set Offset Falloff
        cmds.setAttr(collidePlane + '.offsetFalloff', abs(offsetFalloff))

    # ==============================
    # - Calculate Distance Falloff -
    # ==============================

    if distanceFalloff != None:

        # Add Collide Attributes
        if not cmds.attributeQuery('distanceFalloff', n=collidePlane, ex=True):
            cmds.addAttr(collidePlane, ln='distanceFalloff', min=0, dv=1, k=True)

        # Distance Remap
        distRemap = cmds.createNode('remapValue', n=prefix + '_collideDist_remapValue')
        cmds.connectAttr(collidePlane + '.distanceFalloff', distRemap + '.inputMax', f=True)
        cmds.setAttr(distRemap + '.outputMin', 1)
        cmds.setAttr(distRemap + '.outputMax', 0)
        cmds.setAttr(distRemap + '.inputMin', 0)

        # Distance Falloff
        collideDist = cmds.createNode('distanceBetween', n=prefix + '_collideDist_distanceBetween')
        if len(distanceAxis) == 1:
            cmds.connectAttr(worldToCollide + '.output' + distanceAxis[0], collideDist + '.point1X', f=True)
        elif len(distanceAxis) == 2:
            cmds.connectAttr(worldToCollide + '.output' + distanceAxis[0], collideDist + '.point1X', f=True)
            cmds.connectAttr(worldToCollide + '.output' + distanceAxis[1], collideDist + '.point1Y', f=True)
        else:
            raise Exception('Invalid collision distance axis! (' + str(distanceAxis) + ')')
        cmds.connectAttr(collideDist + '.distance', distRemap + '.inputValue', f=True)

        # Distance Weight
        distMult = cmds.createNode('multDoubleLinear', n=prefix + '_distanceWeight_multDoubleLinear')
        cmds.connectAttr(collidePlane + '.collideWeight', distMult + '.input1', f=True)
        cmds.connectAttr(distRemap + '.outValue', distMult + '.input2', f=True)
        cmds.connectAttr(distMult + '.output', collideBlend + '.blender', f=True)

        # Set Distance Falloff
        cmds.setAttr(collidePlane + '.distanceFalloff', abs(distanceFalloff))

    # =================
    # - Return Result -
    # =================

    return [collidePlane, collideTransform]


def doublePlaneCollideTransform(targetTransform,
                                collidePlane1=None,
                                collidePlane2=None,
                                collideTransform=None,
                                offsetFalloff=None,
                                distanceFalloff=None,
                                distanceAxis='XY',
                                prefix=None):
    """
    Setup a plane collide transform.
    Setup includes smooth offset falloff, distance falloff and collide weight attributes.
    Collision is based on the +Z axis of the collide plane transform.
    @param targetTransform: Target transform (or locator) that the collide transform will follow.
    @type targetTransform: str
    @param collidePlane1: Collision plane 1 transform. If None, creant new renderRect plane.
    @type collidePlane1: str or None
    @param collidePlane2: Collision plane 2 transform. If None, creant new renderRect plane.
    @type collidePlane2: str or None
    @param collideTransform: Collide transform that will collide with the plane. If None, creant new locator.
    @type collideTransform: str or None
    @param offsetFalloff: Calculate collision offset falloff. Offset falloff is calculated as collision local Z distance.
    @type offsetFalloff: float or None
    @param distanceFalloff: Calculate collision distance falloff. Distance falloff is calculated as collision local XY distance.
    @type distanceFalloff: float or None
    @param prefix: Naming prefix. If None, extracted from targetTransform
    @type prefix: str or None
    """
    # ==========
    # - Checks -
    # ==========

    # Check Target Transforms
    if not cmds.objExists(targetTransform):
        raise Exception('Target transform "' + targetTransform + '" does not exist!')
    if not glTools.utils.transform.isTransform(targetTransform):
        raise Exception('Object "' + targetTransform + '" is not a valid transform!')

    # Check Collide Transforms
    if collideTransform and not cmds.objExists(str(collideTransform)):
        raise Exception('Collide transform "' + collideTransform + '" does not exist!')
    if not glTools.utils.transform.isTransform(collideTransform):
        raise Exception('Object "' + collideTransform + '" is not a valid transform!')

    # Check Collide Plane
    if collidePlane and not cmds.objExists(str(collidePlane)):
        raise Exception('Collide plane "' + collidePlane + '" does not exist!')
    if not glTools.utils.transform.isTransform(collidePlane):
        raise Exception('Object "' + collidePlane + '" is not a valid transform!')

    # Check Distance Axis
    if distanceAxis: distanceAxis = distanceAxis.upper()

    # Check Prefix
    if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(targetTransform)

    # ===================
    # - Build Collision -
    # ===================

    # Build Collide Objects
    if not collideTransform:
        collideTransform = cmds.spaceLocator(n=prefix + '_collide_loc')[0]
    if not collidePlane:
        collidePlaneShape = cmds.createNode('renderRect')
        collidePlane = cmds.listRelatives(collidePlaneShape, p=True)[0]
        collidePlane = cmds.rename(collidePlane, prefix + '_collide_plane')

    # Add Collide Attributes
    if not cmds.attributeQuery('collideWeight', n=collidePlane, ex=True):
        cmds.addAttr(collidePlane, ln='collideWeight', min=0, max=1, dv=1, k=True)

    # Build Collide Nodes
    collideCondition = cmds.createNode('condition', n=prefix + '_collide_condition')
    collideBlend = cmds.createNode('blendColors', n=prefix + '_collideWeight_blendColors')
    worldToCollide = cmds.createNode('vectorProduct', n=prefix + '_worldToCollide_vectorProduct')
    cmds.setAttr(worldToCollide + '.operation', 4)  # Point Matrix Product
    collideToWorld = cmds.createNode('vectorProduct', n=prefix + '_collideToWorld_vectorProduct')
    cmds.setAttr(collideToWorld + '.operation', 4)  # Point Matrix Product
    worldToLocal = cmds.createNode('vectorProduct', n=prefix + '_worldToLocal_vectorProduct')
    cmds.setAttr(worldToLocal + '.operation', 4)  # Point Matrix Product

    # =========================
    # - Build Collide Network -
    # =========================

    # World To Collide
    cmds.connectAttr(collidePlane + '.worldInverseMatrix[0]', worldToCollide + '.matrix', f=True)
    if cmds.objExists(targetTransform + '.worldPosition[0]'):
        cmds.connectAttr(targetTransform + '.worldPosition[0]', worldToCollide + '.input1', f=True)
    else:
        localToWorld = cmds.createNode('vectorProduct', n=prefix + '_localToWorld_vectorProduct')
        cmds.setAttr(localToWorld + '.operation', 4)  # Point Matrix Product
        cmds.connectAttr(targetTransform + '.worldMatrix[0]', localToWorld + '.matrix', f=True)
        cmds.connectAttr(localToWorld + '.output', worldToCollide + '.input1', f=True)

    # Collide Condition
    cmds.connectAttr(worldToCollide + '.outputZ', collideCondition + '.firstTerm', f=True)
    cmds.setAttr(collideCondition + '.secondTerm', 0)
    cmds.setAttr(collideCondition + '.operation', 2)  # Greater Than
    cmds.connectAttr(worldToCollide + '.output', collideCondition + '.colorIfTrue', f=True)
    cmds.connectAttr(worldToCollide + '.outputX', collideCondition + '.colorIfFalseR', f=True)
    cmds.connectAttr(worldToCollide + '.outputY', collideCondition + '.colorIfFalseG', f=True)
    cmds.setAttr(collideCondition + '.colorIfFalseB', 0)

    # Collide Weight Blend
    cmds.connectAttr(collideCondition + '.outColor', collideBlend + '.color1', f=True)
    cmds.connectAttr(worldToCollide + '.output', collideBlend + '.color2', f=True)
    cmds.connectAttr(collidePlane + '.collideWeight', collideBlend + '.blender', f=True)

    # Collide To World
    cmds.connectAttr(collideBlend + '.output', collideToWorld + '.input1', f=True)
    cmds.connectAttr(collidePlane + '.worldMatrix[0]', collideToWorld + '.matrix', f=True)

    # World To Local
    cmds.connectAttr(collideToWorld + '.output', worldToLocal + '.input1', f=True)
    cmds.connectAttr(collideTransform + '.parentInverseMatrix[0]', worldToLocal + '.matrix', f=True)

    # Connect Output
    cmds.connectAttr(worldToLocal + '.output', collideTransform + '.translate', f=True)

    # ============================
    # - Calculate Offset Falloff -
    # ============================

    if offsetFalloff != None:

        # Add Collide Attributes
        if not cmds.attributeQuery('offsetFalloff', n=collidePlane, ex=True):
            cmds.addAttr(collidePlane, ln='offsetFalloff', min=0, dv=0.5, k=True)

        # Build Nodes
        falloffRemap = cmds.createNode('remapValue', n=prefix + '_offsetFalloff_remapValue')
        falloffMult = cmds.createNode('multDoubleLinear', n=prefix + '_offsetFalloff_multDoubleLinear')

        # Falloff Remap
        cmds.connectAttr(worldToCollide + '.outputZ', falloffRemap + '.inputValue', f=True)
        cmds.connectAttr(collidePlane + '.offsetFalloff', falloffRemap + '.inputMax', f=True)
        cmds.connectAttr(collidePlane + '.offsetFalloff', falloffRemap + '.outputMax', f=True)
        cmds.connectAttr(collidePlane + '.offsetFalloff', falloffMult + '.input1', f=True)
        cmds.setAttr(falloffMult + '.input2', -1)
        cmds.connectAttr(falloffMult + '.output', falloffRemap + '.inputMin', f=True)

        # Override Collide Condition
        cmds.connectAttr(collidePlane + '.offsetFalloff', collideCondition + '.secondTerm', f=True)
        cmds.connectAttr(falloffRemap + '.outValue', collideCondition + '.colorIfFalseB', f=True)

        # Set Offset Falloff
        cmds.setAttr(collidePlane + '.offsetFalloff', abs(offsetFalloff))

    # ==============================
    # - Calculate Distance Falloff -
    # ==============================

    if distanceFalloff != None:

        # Add Collide Attributes
        if not cmds.attributeQuery('distanceFalloff', n=collidePlane, ex=True):
            cmds.addAttr(collidePlane, ln='distanceFalloff', min=0, dv=1, k=True)

        # Distance Remap
        distRemap = cmds.createNode('remapValue', n=prefix + '_collideDist_remapValue')
        cmds.connectAttr(collidePlane + '.distanceFalloff', distRemap + '.inputMax', f=True)
        cmds.setAttr(distRemap + '.outputMin', 1)
        cmds.setAttr(distRemap + '.outputMax', 0)
        cmds.setAttr(distRemap + '.inputMin', 0)

        # Distance Falloff
        collideDist = cmds.createNode('distanceBetween', n=prefix + '_collideDist_distanceBetween')
        if len(distanceAxis) == 1:
            cmds.connectAttr(worldToCollide + '.output' + distanceAxis[0], collideDist + '.point1X', f=True)
        elif len(distanceAxis) == 2:
            cmds.connectAttr(worldToCollide + '.output' + distanceAxis[0], collideDist + '.point1X', f=True)
            cmds.connectAttr(worldToCollide + '.output' + distanceAxis[1], collideDist + '.point1Y', f=True)
        else:
            raise Exception('Invalid collision distance axis! (' + str(distanceAxis) + ')')
        cmds.connectAttr(collideDist + '.distance', distRemap + '.inputValue', f=True)

        # Distance Weight
        distMult = cmds.createNode('multDoubleLinear', n=prefix + '_distanceWeight_multDoubleLinear')
        cmds.connectAttr(collidePlane + '.collideWeight', distMult + '.input1', f=True)
        cmds.connectAttr(distRemap + '.outValue', distMult + '.input2', f=True)
        cmds.connectAttr(distMult + '.output', collideBlend + '.blender', f=True)

        # Set Distance Falloff
        cmds.setAttr(collidePlane + '.distanceFalloff', abs(distanceFalloff))

    # =================
    # - Return Result -
    # =================

    return


def surfaceCollideTransform(targetTransform, slaveTransform, collideSurface, inside=True, prefix=''):
    """
    """
    # ==========
    # - Checks -
    # ==========

    if not cmds.objExists(targetTransform):
        raise Exception('Target transform "' + targetTransform + '" does not exist!')
    if not cmds.objExists(slaveTransform):
        raise Exception('Slave transform "' + slaveTransform + '" does not exist!')
    if not cmds.objExists(collideSurface):
        raise Exception('Collide surface "' + collideSurface + '" does not exist!')
    if not glTools.utils.surface.isSurface(collideSurface):
        raise Exception('Collide object "' + collideSurface + '" is not a valid NURBS surface!')

    if not prefix: prefix = 'collideSurface'

    # ===================
    # - Create Locators -
    # ===================

    slave_loc = cmds.spaceLocator(n=slaveTransform + '_loc')[0]
    target_loc = cmds.spaceLocator(n=targetTransform + '_loc')[0]
    target_ptCon = cmds.pointConstraint(targetTransform, target_loc)[0]

    # - Setup -
    con = cmds.createNode('condition', n=prefix + '_condition')
    vp = cmds.createNode('vectorProduct', n=prefix + '_vectorProduct')
    pma = cmds.createNode('plusMinusAverage', n=prefix + '_plusMinusAverage')
    posi = cmds.createNode('pointOnSurfaceInfo', n=prefix + '_pointOnSurfaceInfo')
    cpos = cmds.createNode('closestPointOnSurface', n=prefix + '_closestPointOnSurface')

    # Surface Connect
    cmds.connectAttr(collideSurface + '.worldSpace[0]', posi + '.inputSurface', f=True)
    cmds.connectAttr(collideSurface + '.worldSpace[0]', cpos + '.inputSurface', f=True)
    cmds.connectAttr(target_loc + '.worldPosition[0]', cpos + '.inPosition', f=True)

    # Parameter Connect
    cmds.connectAttr(cpos + '.parameterU', posi + '.parameterU', f=True)
    cmds.connectAttr(cpos + '.parameterV', posi + '.parameterV', f=True)

    # Offset Calc
    cmds.setAttr(pma + '.operation', 2)  # SUBTRACT
    cmds.connectAttr(target_loc + '.worldPosition[0]', pma + '.input3D[0]', f=True)
    cmds.connectAttr(cpos + '.position', pma + '.input3D[1]', f=True)

    # Dot Product
    cmds.setAttr(vp + '.operation', 1)  # DOT PRODUCT
    cmds.connectAttr(posi + '.normal', vp + '.input1', f=True)
    cmds.connectAttr(pma + '.output3D', vp + '.input2', f=True)

    # Condition
    if inside:
        cmds.setAttr(con + '.operation', 2)  # Greater Than
    else:
        cmds.setAttr(con + '.operation', 4)  # Less Than
    cmds.setAttr(con + '.firstTerm', 0.0)
    cmds.connectAttr(vp + '.outputX', con + '.secondTerm', f=True)
    cmds.connectAttr(target_loc + '.worldPosition[0]', con + '.colorIfTrue', f=True)
    cmds.connectAttr(cpos + '.position', con + '.colorIfFalse', f=True)

    # Output
    cmds.connectAttr(con + '.outColor', slave_loc + '.t', f=True)

    return target_loc, slave_loc
