import maya.cmds as cmds
import glTools.utils.stringUtils


def poseDrivenAttr(poseTransform,
                   poseReference,
                   poseAxis,
                   targetAttr,
                   upAxis=None,
                   remapValue=False,
                   arclen=False,
                   prefix=None):
    """
    Create a pose driven attribute.
    @param poseTransform: The transform that the pose is based on
    @type poseTransform: str
    @param poseReference: The reference transform that the pose axis is compared against
    @type poseReference: str
    @param poseAxis: The axis of the pose transform that will define the pose
    @type poseAxis: str
    @param targetAttr: The attribute that will be driven by the pose
    @type targetAttr: str
    @param upAxis: The axis of the pose transform that will define the pose twist (upVector)...optional.
    @type upAxis: str
    @param remapValue: Remap the resulting pose value via a remapValue node
    @type remapValue: bool
    @param arclen: Use vector arc length instead of dot product. Arc length method provides a more linear result.
    @type arclen: bool
    @param prefix: The name prefix for all created nodes
    @type prefix: str
    """
    # ==========
    # - Checks -
    # ==========

    axisList = ['x', 'y', 'z']  # ,'+x','+y','+z','-x','-y','-z']
    axisVector = {'x': [1, 0, 0],
                  'y': [0, 1, 0],
                  'z': [0, 0, 1]}  # ,
    # '+x':[1,0,0],
    # '+y':[0,1,0],
    # '+z':[0,0,1],
    # '-x':[-1,0,0],
    # '-y':[0,-1,0],
    # '-z':[0,0,-1] }

    # Check pose transform
    if not cmds.objExists(poseTransform):
        raise Exception('PoseTransform "' + poseTransform + '" does not exist!')

    # Check target attribute
    if not cmds.objExists(targetAttr):
        raise Exception('Target attribute "' + targetAttr + '" does not exist!')

    # Check reference axis
    poseAxis = poseAxis.lower()
    if not poseAxis in axisList:
        raise Exception('Invalid pose axis! Valid pose axis values are "x" "y" and "z"!!')

    # Check up axis
    if upAxis:
        upAxis = upAxis.lower()
        if not upAxis in axisList:
            raise Exception('Invalid up axis! Valid up axis values are "x" "y" and "z"!!')
        if upAxis == poseAxis:
            raise Exception('Pose axis and Up axis must be unique!!')

    # Check arclen
    if arclen:
        if not cmds.pluginInfo('glToolsTools', q=True, l=True):
            try:
                cmds.loadPlugin('glToolsTools')
            except:
                raise Exception('Error loading plugin glToolsTools!!')

    # Check prefix
    if not prefix:
        prefix = glTools.utils.stringUtils.stripSuffix(poseTransform)

    # ==================================
    # - Create PoseReference Transform -
    # ==================================

    if not poseReference:
        poseReference = cmds.duplicate(poseTransform, parentOnly=True, n=prefix + '_poseReference')[0]

    # Add poseTransform message attribute
    cmds.addAttr(poseReference, ln='poseTransform', at='message')
    cmds.connectAttr(poseTransform + '.message', poseReference + '.poseTransform', f=True)

    # ====================================
    # - Create vector comparison network -
    # ====================================

    poseVector = axisVector[poseAxis]
    poseResultAttr = ''

    if arclen:

        # Pose vector arc distance
        pose_arcDist = cmds.createNode('arcDistance', n=prefix + '_pose_arcDistance')
        cmds.connectAttr(poseTransform + '.worldMatrix[0]', pose_arcDist + '.matrix1', f=True)
        cmds.connectAttr(poseReference + '.worldMatrix[0]', pose_arcDist + '.matrix2', f=True)
        cmds.setAttr(pose_arcDist + '.vector1', poseVector[0], poseVector[1], poseVector[2])
        cmds.setAttr(pose_arcDist + '.vector2', poseVector[0], poseVector[1], poseVector[2])

        # Set Pose Result
        poseResultAttr = pose_arcDist + '.arcDistance'

    else:

        # - Pose Transform Vector
        poseVecDotProduct = cmds.createNode('vectorProduct', n=prefix + '_poseVector_vectorProduct')
        cmds.setAttr(poseVecDotProduct + '.operation', 3)  # Vector Matric Product
        cmds.setAttr(poseVecDotProduct + '.input1', poseVector[0], poseVector[1], poseVector[2])
        cmds.setAttr(poseVecDotProduct + '.normalizeOutput', 1)
        cmds.connectAttr(poseTransform + '.worldMatrix[0]', poseVecDotProduct + '.matrix', f=True)

        # - Pose Reference Vector
        referenceVecDotProduct = cmds.createNode('vectorProduct', n=prefix + '_referenceVector_vectorProduct')
        cmds.setAttr(referenceVecDotProduct + '.operation', 3)  # Vector Matric Product
        cmds.setAttr(referenceVecDotProduct + '.input1', poseVector[0], poseVector[1], poseVector[2])
        cmds.setAttr(referenceVecDotProduct + '.normalizeOutput', 1)
        cmds.connectAttr(poseReference + '.worldMatrix[0]', referenceVecDotProduct + '.matrix', f=True)

        # - Pose Vector Comparison
        poseVecCompare_dotProduct = cmds.createNode('vectorProduct', n=prefix + '_vectorCompare_vectorProduct')
        cmds.setAttr(poseVecCompare_dotProduct + '.operation', 1)  # Dot Product
        cmds.setAttr(poseVecCompare_dotProduct + '.normalizeOutput', 1)
        cmds.connectAttr(poseVecDotProduct + '.output', poseVecCompare_dotProduct + '.input1', f=True)
        cmds.connectAttr(referenceVecDotProduct + '.output', poseVecCompare_dotProduct + '.input2', f=True)

        # Set Pose Result
        poseResultAttr = poseVecCompare_dotProduct + '.output'

    # ===============================
    # - Check Pose Twist (UpVector) -
    # ===============================

    if upAxis:

        upVector = axisVector[upAxis]

        # Multiply Result
        poseResult_mdl = cmds.createNode('multDoubleLinear', n=prefix + '_poseResult_multDoubleLinear')

        if arclen:

            # Up vector arc distance
            upVec_arcDist = cmds.createNode('arcDistance', n=prefix + '_upVec_arcDistance')
            cmds.connectAttr(poseTransform + '.worldMatrix[0]', upVec_arcDist + '.matrix1', f=True)
            cmds.connectAttr(poseReference + '.worldMatrix[0]', upVec_arcDist + '.matrix2', f=True)
            cmds.setAttr(upVec_arcDist + '.vector1', upVector[0], upVector[1], upVector[2])
            cmds.setAttr(upVec_arcDist + '.vector2', upVector[0], upVector[1], upVector[2])

            # Invert values
            cmds.connectAttr(upVec_arcDist + '.arcDistance', pose_arcDist_reverse + '.inputY', f=True)

            # Multiply Result
            cmds.connectAttr(poseResultAttr, poseResult_mdl + '.input1', f=True)
            cmds.connectAttr(pose_arcDist_reverse + '.outputY', poseResult_mdl + '.input2', f=True)

        else:

            # - Transform Up Vector
            poseUpVec_vectorProduct = cmds.createNode('vectorProduct', n=prefix + '_upVecPose_vectorProduct')
            cmds.setAttr(poseUpVec_vectorProduct + '.operation', 3)  # Vector Matric Product
            cmds.setAttr(poseUpVec_vectorProduct + '.input1', upVector[0], upVector[1], upVector[2])
            cmds.setAttr(poseUpVec_vectorProduct + '.normalizeOutput', 1)
            cmds.connectAttr(poseTransform + '.worldMatrix[0]', poseUpVec_vectorProduct + '.matrix', f=True)

            # - Reference Up Vector
            refUpVec_vectorProduct = cmds.createNode('vectorProduct', n=prefix + '_upVecReference_vectorProduct')
            cmds.setAttr(refUpVec_vectorProduct + '.operation', 3)  # Vector Matric Product
            cmds.setAttr(refUpVec_vectorProduct + '.input1', upVector[0], upVector[1], upVector[2])
            cmds.setAttr(refUpVec_vectorProduct + '.normalizeOutput', 1)
            cmds.connectAttr(poseReference + '.worldMatrix[0]', refUpVec_vectorProduct + '.matrix', f=True)

            # - Up Vector Comparison
            upVecCompare_dotProduct = cmds.createNode('vectorProduct', n=prefix + '_upVecCompare_vectorProduct')
            cmds.setAttr(upVecCompare_dotProduct + '.operation', 1)  # Dot Product
            cmds.setAttr(upVecCompare_dotProduct + '.normalizeOutput', 1)
            cmds.connectAttr(poseUpVec_vectorProduct + '.output', upVecCompare_dotProduct + '.input1')
            cmds.connectAttr(refUpVec_vectorProduct + '.output', upVecCompare_dotProduct + '.input2')

            # Multiply Result
            cmds.connectAttr(poseResultAttr, poseResult_mdl + '.input1', f=True)
            cmds.connectAttr(upVecCompare_dotProduct + '.outputX', poseResult_mdl + '.input2', f=True)

        # Set pose compare attribute
        poseResultAttr = poseResult_mdl + '.output'

    # =======================
    # - Remap output Values -
    # =======================

    # Initialize variables
    remapValueNode = ''

    # Check remapValue node
    if remapValue:
        # Create remapValue node
        remapValueNode = cmds.createNode('remapValue', n=prefix + '_remapValue')
        cmds.connectAttr(poseResultAttr, remapValueNode + '.inputValue', f=True)
        poseResultAttr = remapValueNode + '.outValue'

    # ==========================
    # - Connect to Target Attr -
    # ==========================

    cmds.connectAttr(poseResultAttr, targetAttr, f=True)

    # =================
    # - Return Result -
    # =================

    return [poseReference, remapValueNode]


def addPoseData(poseNode,
                poseAttr,
                poseTransform,
                poseReference,
                poseAxis,
                upAxis='',
                remapValue=False,
                arclen=False,
                prefix=''):
    """
    Add a pose space driven attribute to a specified "poseNode".
    Pose data is stored under a multi attribute named "poseData".
    Each index of the poseData multi will be assigned an alias specified by the poseAttr argument.
    @param poseNode: The node to add the pose driven attributes to.
    @type poseNode: str
    @param poseAttr: The attribute name alias assigned to the poseData multi element created by this command.
    @type poseAttr: str
    @param poseTransform: The transform that the pose is based on
    @type poseTransform: str
    @param poseReference: The reference transform that the pose axis is compared against
    @type poseReference: str
    @param poseAxis: The axis of the pose transform that will define the pose
    @type poseAxis: str
    @param upAxis: The axis of the pose transform that will define the pose twist (upVector)...optional.
    @type upAxis: str
    @param remapValue: Remap the resulting pose value via a remapValue node
    @type remapValue: bool
    @param arclen: Use vector arc length instead of dot product. Arc length method provides a more linear result.
    @type arclen: bool
    @param prefix: The name prefix for all created nodes
    @type prefix: str
    """
    # ======================
    # - Check Rig All Node -
    # ======================

    # Check poseNode
    if not cmds.objExists(poseNode):
        raise Exception('Pose node "' + poseNode + '" does not exist!')

    # Check PoseAttr
    if cmds.attributeQuery(poseAttr, node=poseNode, exists=True):
        raise Exception('Pose attribute "' + poseNode + '.' + poseAttr + '" already exists!')

    # ==================
    # - Check PoseData -
    # ==================

    # Define PoseData Attribute
    poseDataAttr = 'poseData'

    # Add PoseData Attribute (multi)
    if not cmds.attributeQuery(poseDataAttr, node=poseNode, exists=True):
        cmds.addAttr(poseNode, ln=poseDataAttr, m=True, dv=-2)

    # ======================
    # - Add PoseData Entry -
    # ======================

    # Get next available poseData index
    poseDataIndex = cmds.getAttr(poseNode + '.' + poseDataAttr, s=True)

    # Initialize poseData at current index
    cmds.setAttr(poseNode + '.' + poseDataAttr + '[' + str(poseDataIndex) + ']', 0)

    # Alias attribute
    cmds.aliasAttr(poseAttr, poseNode + '.' + poseDataAttr + '[' + str(poseDataIndex) + ']')

    # ====================
    # - Connect PoseData -
    # ====================

    pose = glTools.tools.poseSpace.poseDrivenAttr(poseTransform=poseTransform,
                                                  poseReference=poseReference,
                                                  poseAxis=poseAxis,
                                                  targetAttr=poseNode + '.' + poseAttr,
                                                  upAxis=upAxis,
                                                  remapValue=remapValue,
                                                  arclen=arclen,
                                                  prefix=prefix)

    # =================
    # - Return Result -
    # =================

    return poseNode + '.' + poseAttr
