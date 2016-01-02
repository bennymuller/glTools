import maya.cmds as cmds
import glTools.utils.stringUtils


def poseDrivenAttr(poseTransform, poseAxis='x', remapValue=False, targetAttr, prefix=''):
    """
    Create a pose driven attribute.
    @param poseTransform: The transform that the pose is based on
    @type poseTransform: str
    @param targetAttr: The attribute that will be driven by the pose
    @type targetAttr: str
    @param poseAxis: The axis of the pose transform that will describe the pose
    @type poseAxis: str
    @param prefix: The name prefix for all created nodes
    @type prefix: str
    """
    # ----------
    # - Checks -
    # ----------

    # Check pose transform
    if not cmds.objExists(poseTransform):
        raise Exception('PoseTransform "' + poseTransform + '" does not exist!')

    # Check target attribute
    if not cmds.objExists(targetAttr):
        raise Exception('Target attribute "' + targetAttr + '" does not exist!')

    # Check reference axis
    poseAxis = poseAxis.lower()
    if not poseAxis in ['x', 'y', 'z']:
        raise Exception('Invalid pose axis! Valid pose axis values are "x" "y" and "z"!!')

    # Check prefix
    if not prefix:
        prefix = glTools.utils.stringUtils.stripSuffix(poseTransform)

    # ----------------------------------
    # - Create poseReference transform -
    # ----------------------------------

    poseReference = prefix + '_poseReference'
    poseReference = cmds.duplicate(transform, parentOnly=True, n=poseReference)

    # Add poseTransform message attribute
    cmds.addAttr(poseReference, ln='poseTransform', at='message')
    cmds.connectAttr(poseTransform + '.message', poseReference + '.poseTransform', f=True)

    # ------------------------------------
    # - Create vector comparison network -
    # ------------------------------------

    poseVector = {'x': [1, 0, 0], 'y': [0, 1, 0], 'z': [0, 0, 1]}[poseAxis]

    # - Pose Transform Vector
    poseVecDotProduct = cmds.createNode('vectorProduct', n=prefix + '_poseVector_vectorProduct')
    cmds.setAttr(poseVecDotProduct + '.operation', 3)  # Vector Matric Product
    cmds.setAttr(poseVecDotProduct + '.input', poseVector[0], poseVector[1], poseVector[2])
    cmds.setAttr(poseVecDotProduct + '.normalizeOutput', 1)
    cmds.connectAttr(poseTransform + '.worldMatrix[0]', poseVecDotProduct + '.matrix', f=True)

    # - Pose Reference Vector
    referenceVecDotProduct = cmds.createNode('vectorProduct', n=prefix + '_referenceVector_vectorProduct')
    cmds.setAttr(referenceVecDotProduct + '.operation', 3)  # Vector Matric Product
    cmds.setAttr(referenceVecDotProduct + '.input', poseVector[0], poseVector[1], poseVector[2])
    cmds.setAttr(referenceVecDotProduct + '.normalizeOutput', 1)
    cmds.connectAttr(poseReference + '.worldMatrix[0]', referenceVecDotProduct + '.matrix', f=True)

    # - Pose Vector Comparison
    vectorCompareDotProduct = cmds.createNode('vectorProduct', n=prefix + '_vectorCompare_vectorProduct')
    cmds.setAttr(vectorCompareDotProduct + '.operation', 1)  # Dot Product
    cmds.setAttr(vectorCompareDotProduct + '.normalizeOutput', 1)
    cmds.connectAttr(poseVecDotProduct + '.output', vectorCompareDotProduct + '.input1')
    cmds.connectAttr(referenceVecDotProduct + '.output', vectorCompareDotProduct + '.input2')

    # -----------------------
    # - Clamp output values -
    # -----------------------
    poseClamp = cmds.createNode('clamp', prefix + '_clamp')
    cmds.connectAttr(vectorCompareDotProduct + '.outputX', poseClamp + '.inputR', f=True)
    cmds.setAttr(poseClamp + '.minR', 0.0)
    cmds.setAttr(poseClamp + '.maxR', 1.0)

    # -----------------------
    # - Remap output Values -
    # -----------------------
    remapValueNode = ''
    if remapValue:
        remapValNode = cmds.createNode('remapValue', n=prefix + '_remapValue')
        cmds.connectAttr(poseClamp + '.outputR', remapValNode + '.inputValue', f=True)
        cmds.connectAttr(remapValNode + '.outValue', targetAttr, f=True)
    else:
        cmds.connectAttr(poseClamp + '.outputR', targetAttr, f=True)

    # -----------------
    # - Return Result -
    # -----------------

    return poseReference
