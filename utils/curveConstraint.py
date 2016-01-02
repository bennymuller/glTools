import maya.cmds as cmds
import glTools.utils.curve
import glTools.utils.stringUtils


def curveConstraint(transform, curve, parameter, useClosestPoint=True, normalizeParameter=True, tangentAxis='x',
                    upAxis='y', upVector='y', upObject='', prefix=''):
    """
    @param transform: Transform to constrain to curve
    @type transform: str
    @param curve: Target curve that drives the constraint
    @type curve: str
    @param parameter: Target curve parameter to constrain to
    @type parameter: float
    @param useClosestPoint: Use the closest curve parameter to the transform instead of the specified parameter
    @type useClosestPoint: bool
    @param tangentAxis: Transform axis to align to the curve tangent
    @type tangentAxis: str
    @param upAxis: Transform axis to align to the upVector of the constraint node
    @type upAxis: str
    @param upVector: The world or upObject vector to be used as the constraint upVector
    @type upVector: str
    @param upObject: Specifies the upVector object for the constraint
    @type upObject: str
    @param prefix: Name prefix for newly created nodes
    @type prefix: str
    """
    # Build axis dictionary
    axisDict = {'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1), '-x': (-1, 0, 0), '-y': (0, -1, 0), '-z': (0, 0, -1)}

    # Check prefix
    if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(transform)

    # Parameter
    pos = cmds.xform(transform, q=True, ws=True, rp=True)
    if useClosestPoint: parameter = glTools.utils.curve.closestPoint(curve, pos)

    # PointOnCurveInfo
    poc = prefix + '_pointOnCurveInfo'
    poc = cmds.createNode('pointOnCurveInfo', n=poc)
    cmds.connectAttr(curve + '.worldSpace[0]', poc + '.inputCurve', f=True)
    if normalizeParameter:
        cmds.setAttr(poc + '.turnOnPercentage', 1)
        minParam = cmds.getAttr(curve + '.minValue')
        maxParam = cmds.getAttr(curve + '.maxValue')
        parameter = (parameter - minParam) / (maxParam - minParam)
    cmds.setAttr(poc + '.parameter', parameter)

    # Point Constraint
    pntCon = prefix + '_pointConstraint'
    pntCon = cmds.createNode('pointConstraint', n=pntCon)
    cmds.connectAttr(poc + '.position', pntCon + '.target[0].targetTranslate', f=True)
    cmds.connectAttr(transform + '.parentInverseMatrix[0]', pntCon + '.constraintParentInverseMatrix', f=True)
    cmds.connectAttr(pntCon + '.constraintTranslate', transform + '.translate', f=True)

    # Aim Constraint
    aicmdson = prefix + '_aicmdsonstraint'
    aicmdson = cmds.createNode('aicmdsonstraint', n=aicmdson)
    cmds.connectAttr(poc + '.tangent', aicmdson + '.target[0].targetTranslate', f=True)
    aimVec = axisDict[tangentAxis]
    upVec = axisDict[upAxis]
    cmds.setAttr(aicmdson + '.aimVector', aimVec[0], aimVec[1], aimVec[2])
    cmds.setAttr(aicmdson + '.upVector', upVec[0], upVec[1], upVec[2])
    # UpVector
    wUpVec = axisDict[upVector]
    cmds.setAttr(aicmdson + '.worldUpVector', wUpVec[0], wUpVec[1], wUpVec[2])
    # UpObject
    if upObject:
        cmds.connectAttr(upObject + '.worldMatrix[0]', aicmdson + '.worldUpMatrix', f=True)
        cmds.setAttr(aicmdson + '.worldUpType', 2)  # Object Rotation Up
    # Connect
    cmds.connectAttr(transform + '.parentInverseMatrix[0]', aicmdson + '.constraintParentInverseMatrix', f=True)
    cmds.connectAttr(aicmdson + '.constraintRotate', transform + '.rotate', f=True)

    # Parent constraints
    cmds.parent(pntCon, transform)
    cmds.parent(aicmdson, transform)

    # Add parameter attribute
    if not cmds.objExists(transform + '.param'):
        if normalizeParameter:
            cmds.addAttr(transform, ln='param', at='float', dv=parameter, min=0.0, max=1.0, k=True)
        else:
            cmds.addAttr(transform, ln='param', at='float', dv=parameter, min=minParam, max=maxParam, k=True)
    cmds.connectAttr(transform + '.param', poc + '.parameter', f=True)

    # Return result
    return (poc, pntCon, aicmdson)


def curveAicmdsonstraint(transform, curve, parameter, useClosestPoint=True, aimAxis='y', tangentAxis='x', prefix=''):
    """
    @param transform: Transform to aim at point on curve
    @type transform: str
    @param curve: Target curve that drives the constraint
    @type curve: str
    @param parameter: Target curve parameter to aim at
    @type parameter: float
    @param useClosestPoint: Use the closest curve parameter to the transform instead of the specified parameter
    @type useClosestPoint: bool
    @param aimAxis: Transform axis to aim at the point on curve
    @type aimAxis: float
    @param tangentAxis: Transform axis to align to the curve tangent
    @type tangentAxis: str
    @param prefix: Name prefix for newly created nodes
    @type prefix: str
    """
    # Build axis dictionary
    axisDict = {'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1), '-x': (-1, 0, 0), '-y': (0, -1, 0), '-z': (0, 0, -1)}

    # Check prefix
    if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(transform)

    # Transform worldSpace position
    pmm = prefix + '_pointMatrixMult'
    pmm = cmds.createNode('pointMatrixMult', n=pmm)
    cmds.connectAttr(transform + '.translate', pmm + '.inPoint', f=True)
    cmds.connectAttr(transform + '.parentMatrix[0]', pmm + '.inMatrix', f=True)
    cmds.setAttr(pmm + '.vectorMultiply', 1)

    # Parameter
    pos = cmds.xform(transform, q=True, ws=True, rp=True)
    if useClosestPoint: paramater = glTools.utils.curve.closestPoint(curve, pos)

    # PointOnCurveInfo
    poc = prefix + '_pointOnCurveInfo'
    poc = cmds.createNode('pointOnCurveInfo', n=poc)
    cmds.connectAttr(curve + '.worldSpace[0]', poc + '.inputCurve', f=True)
    cmds.setAttr(poc + '.parameter', paramater)

    # Offset
    pma = prefix + '_plusMinusAverage'
    pma = cmds.createNode('plusMinusAverage', n=pma)
    cmds.connectAttr(poc + '.position', pma + '.input3D[0]', f=True)
    cmds.connectAttr(pmm + '.output', pma + '.input3D[1]', f=True)
    cmds.setAttr(pma + '.operation', 2)  # Subtract

    # Aim Constraint
    aicmdson = prefix + '_aicmdsonstraint'
    aicmdson = cmds.createNode('aicmdsonstraint', n=aicmdson)
    cmds.connectAttr(pma + '.output3D', aicmdson + '.target[0].targetTranslate', f=True)
    cmds.connectAttr(poc + '.tangent', aicmdson + '.worldUpVector', f=True)
    cmds.connectAttr(transform + '.parentInverseMatrix[0]', aicmdson + '.constraintParentInverseMatrix', f=True)
    cmds.setAttr(aicmdson + '.worldUpType', 3)  # Vector
    cmds.connectAttr(aicmdson + '.constraintRotateX', transform + '.rotateX', f=True)
    cmds.connectAttr(aicmdson + '.constraintRotateY', transform + '.rotateY', f=True)
    cmds.connectAttr(aicmdson + '.constraintRotateZ', transform + '.rotateZ', f=True)
    aimVec = axisDict[aimAxis]
    tanVec = axisDict[tangentAxis]
    cmds.setAttr(aicmdson + '.aimVector', aimVec[0], aimVec[1], aimVec[2])
    cmds.setAttr(aicmdson + '.upVector', tanVec[0], tanVec[1], tanVec[2])
    cmds.parent(aicmdson, transform)

    # Add parameter attribute
    minU = cmds.getAttr(curve + '.minValue')
    maxU = cmds.getAttr(curve + '.maxValue')
    if not cmds.objExists(transform + '.paramU'): cmds.addAttr(transform, ln='paramU', at='float', min=minU, max=maxU,
                                                           k=True)
    cmds.setAttr(transform + '.paramU', parameter)
    cmds.connectAttr(transform + '.paramU', poc + '.parameter', f=True)


def multiCurveAicmdsonstraint(transform, curve1, curve2, toggleAttr, aimAxis='y', tangentAxis='x', prefix=''):
    """
    @param transform: Transforms to aim at point on curve
    @type transform: list
    @param curve1: First curve aim target
    @type curve1: str
    @param curve2: Second curve aim target
    @type curve2: str
    @param toggleAttr: Attribute to toggle between the constraint targets
    @type toggleAttr: str
    @param aimAxis: Transform axis to aim at the point on curve
    @type aimAxis: float
    @param tangentAxis: Transform axis to align to the curve tangent
    @type tangentAxis: str
    @param prefix: Name prefix for newly created nodes
    @type prefix: str
    """
    # Build axis dictionary
    axisDict = {'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1), '-x': (-1, 0, 0), '-y': (0, -1, 0), '-z': (0, 0, -1)}

    # Check prefix
    if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(transform)

    # Transform worldSpace position
    pmm = prefix + '_pointMatrixMult'
    pmm = cmds.createNode('pointMatrixMult', n=pmm)
    cmds.connectAttr(transform + '.translate', pmm + '.inPoint', f=True)
    cmds.connectAttr(transform + '.parentMatrix[0]', pmm + '.inMatrix', f=True)
    cmds.setAttr(pmm + '.vectorMultiply', 1)

    # PointOnCurveInfo
    poc1 = prefix + '_pc01_pointOnCurveInfo'
    poc1 = cmds.createNode('pointOnCurveInfo', n=poc1)
    cmds.connectAttr(curve1 + '.worldSpace[0]', poc1 + '.inputCurve', f=True)
    poc2 = prefix + '_pc02_pointOnCurveInfo'
    poc2 = cmds.createNode('pointOnCurveInfo', n=poc2)
    cmds.connectAttr(curve2 + '.worldSpace[0]', poc2 + '.inputCurve', f=True)

    pos = cmds.xform(transform, q=True, ws=True, rp=True)
    param = glTools.utils.curve.closestPoint(curve1, pos)
    cmds.setAttr(poc1 + '.parameter', param)
    pos = cmds.pointOnCurve(curve1, pr=param, p=True)
    param = glTools.utils.curve.closestPoint(curve2, pos)
    cmds.setAttr(poc2 + '.parameter', param)

    # Offset
    pma1 = prefix + '_pc01_plusMinusAverage'
    pma1 = cmds.createNode('plusMinusAverage', n=pma1)
    cmds.connectAttr(poc1 + '.position', pma1 + '.input3D[0]', f=True)
    cmds.connectAttr(pmm + '.output', pma1 + '.input3D[1]', f=True)
    cmds.setAttr(pma1 + '.operation', 2)  # Subtract

    pma2 = prefix + '_pc02_plusMinusAverage'
    pma2 = cmds.createNode('plusMinusAverage', n=pma2)
    cmds.connectAttr(poc2 + '.position', pma2 + '.input3D[0]', f=True)
    cmds.connectAttr(pmm + '.output', pma2 + '.input3D[1]', f=True)
    cmds.setAttr(pma2 + '.operation', 2)  # Subtract

    # Blend Offset
    pos_bcn = prefix + '_ps01_blendColors'
    pos_bcn = cmds.createNode('blendColors', n=pos_bcn)
    cmds.connectAttr(pma1 + '.output3D', pos_bcn + '.color1', f=True)
    cmds.connectAttr(pma2 + '.output3D', pos_bcn + '.color2', f=True)
    cmds.connectAttr(toggleAttr, pos_bcn + '.blender', f=True)

    # Blend Tangent
    tan_bcn = prefix + '_rt01_blendColors'
    tan_bcn = cmds.createNode('blendColors', n=tan_bcn)
    cmds.connectAttr(poc1 + '.tangent', tan_bcn + '.color1', f=True)
    cmds.connectAttr(poc2 + '.tangent', tan_bcn + '.color2', f=True)
    cmds.connectAttr(toggleAttr, tan_bcn + '.blender', f=True)

    # Aim Constraint
    aicmdson = prefix + '_aicmdsonstraint'
    aicmdson = cmds.createNode('aicmdsonstraint', n=aicmdson)
    cmds.connectAttr(pos_bcn + '.output', aicmdson + '.target[0].targetTranslate', f=True)
    cmds.connectAttr(tan_bcn + '.output', aicmdson + '.worldUpVector', f=True)
    cmds.setAttr(aicmdson + '.worldUpType', 3)  # Vector
    cmds.connectAttr(transform + '.parentInverseMatrix[0]', aicmdson + '.constraintParentInverseMatrix', f=True)
    cmds.connectAttr(aicmdson + '.constraintRotateX', transform + '.rotateX', f=True)
    cmds.connectAttr(aicmdson + '.constraintRotateY', transform + '.rotateY', f=True)
    cmds.connectAttr(aicmdson + '.constraintRotateZ', transform + '.rotateZ', f=True)
    aimVec = axisDict[aimAxis]
    tanVec = axisDict[tangentAxis]
    cmds.setAttr(aicmdson + '.aimVector', aimVec[0], aimVec[1], aimVec[2])
    cmds.setAttr(aicmdson + '.upVector', tanVec[0], tanVec[1], tanVec[2])
    cmds.parent(aicmdson, transform)

    # Add parameter attribute
    minU = cmds.getAttr(curve1 + '.minValue')
    maxU = cmds.getAttr(curve1 + '.maxValue')
    if not cmds.objExists(transform + '.param1'):
        cmds.addAttr(transform, ln='param1', at='float', min=minU, max=maxU, k=True)
    cmds.setAttr(transform + '.param1', cmds.getAttr(poc1 + '.parameter'))
    cmds.connectAttr(transform + '.param1', poc1 + '.parameter', f=True)

    minU = cmds.getAttr(curve2 + '.minValue')
    maxU = cmds.getAttr(curve2 + '.maxValue')
    if not cmds.objExists(transform + '.param2'):
        cmds.addAttr(transform, ln='param2', at='float', min=minU, max=maxU, k=True)
    cmds.setAttr(transform + '.param2', cmds.getAttr(poc2 + '.parameter'))
    cmds.connectAttr(transform + '.param2', poc2 + '.parameter', f=True)

    # Return result
    return (aicmdson, poc1, poc2)
