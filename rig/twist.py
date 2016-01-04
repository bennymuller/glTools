import maya.cmds as cmds
import glTools.rig.utils
import glTools.utils.attribute
import glTools.utils.base
import glTools.utils.joint
import glTools.utils.stringUtils
import glTools.tools.controlBuilder


def createTwistJoints(joint,
                      numTwistJoints,
                      offsetAxis='x',
                      prefix=''):
    """
    Generate twist joints for a specified rig joint.
    This function only creates the joints, it does not setup the twist control network.
    @param joint: Master rig joint that will drive the twist
    @type joint: str
    @param numTwistJoints: Number of twist joints to create
    @type numTwistJoints: int
    @param offsetAxis: Twist joint offset axis
    @type offsetAxis: str
    @param prefix: Naming prefix for twist joints
    @type prefix: str
    """
    # ==========
    # - Checks -
    # ==========

    # Check joint
    if not cmds.objExists(joint):
        raise Exception('Joint ' + joint + ' does not exist!')

    # Check prefix
    if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(joint)

    # Offset Axis
    if not ['x', 'y', 'z'].count(offsetAxis):
        raise Exception('Invalid offset axis value! ("' + offsetAxis + '")')

    # =================
    # - Create Joints -
    # =================

    # Get joint length
    jointEnd = cmds.listRelatives(joint, c=True)[0]
    jointLen = cmds.getAttr(jointEnd + '.t' + offsetAxis)
    jointOffset = jointLen / (numTwistJoints - 1)

    # Create twist joints
    twistJoints = []
    for i in range(numTwistJoints):
        alphaInd = glTools.utils.stringUtils.alphaIndex(i, upper=True)

        # Duplicate joint
        twistJoint = cmds.duplicate(joint, po=True, n=prefix + '_twist' + alphaInd + '_jnt')[0]
        # Remove user attributes
        glTools.utils.attribute.deleteUserAttrs(twistJoint)
        # Parent to joint
        cmds.parent(twistJoint, joint)

        # Position joint
        cmds.setAttr(twistJoint + '.t' + offsetAxis, jointOffset * i)

        # Append joint list
        twistJoints.append(twistJoint)

    # =================
    # - Return Result -
    # =================

    return twistJoints


def build(sourceJoint,
          targetJoint,
          numJoints=4,
          aimAxis='x',
          upAxis='y',
          baseToTip=True,
          enableCtrl=False,
          prefix=''):
    """
    Build twist joint setup using an aicmdsonstraint to calculate rotation.
    @param numJoints:
    @param sourceJoint: Twist base joint
    @type sourceJoint: str
    @param targetJoint: Twist target or end joint
    @type targetJoint: str
    @param aimAxis: Axis along the length of the source joint
    @type aimAxis: list or tuple
    @param upAxis: Upward facing axis of the source joint
    @type upAxis: list or tuple
    @param baseToTip: Twist from the base to the tip
    @type baseToTip: bool
    @param enableCtrl: Enable the twist child joint as a control
    @type enableCtrl: bool
    @param prefix: Naming prefix for created nodes
    @type prefix: str
    """
    # ==========
    # - Checks -
    # ==========

    # Define Axis Dictionary
    axisDict = {'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1), '-x': (-1, 0, 0), '-y': (0, -1, 0), '-z': (0, 0, -1)}

    if not cmds.objExists(sourceJoint):
        raise Exception('Source joint "' + sourceJoint + '" does not exist!')
    if not cmds.objExists(targetJoint):
        raise Exception('Target joint "' + targetJoint + '" does not exist!')

    if not axisDict.has_key(aimAxis):
        raise Exception('Invalid aim axis value! ("' + aimAxis + '")')
    if not axisDict.has_key(upAxis):
        raise Exception('Invalid up axis value! ("' + upAxis + '")')

    if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(sourceJoint)

    # ======================
    # - Configure Modifier -
    # ======================

    twistCtrlScale = 0.2
    ctrlBuilder = glTools.tools.controlBuilder.ControlBuilder()

    # =======================
    # - Create Twist Joints -
    # =======================

    twistJoints = createTwistJoints(joint=sourceJoint,
                                    numTwistJoints=numJoints,
                                    offsetAxis=aimAxis[-1],
                                    prefix=prefix)

    # Check baseToTip - Reverse list order if false
    if not baseToTip: twistJoints.reverse()

    # Create Joint Groups/Attributes/Tags
    twistJointGrps = []
    twistFactor = 1.0 / (len(twistJoints) - 1)
    jntLen = glTools.utils.joint.length(sourceJoint)
    for i in range(len(twistJoints)):

        # Add Twist Control Attribute
        cmds.addAttr(twistJoints[i], ln='twist', min=-1.0, max=1.0, dv=twistFactor * i)

        # Add Twist Joint Group
        twistJointGrp = glTools.utils.joint.group(twistJoints[i], indexStr='Twist')
        twistJointGrps.append(twistJointGrp)

        # Tag Bind Joint
        glTools.rig.utils.tagBindJoint(twistJoints[i], True)

        # Create Joint Control
        if enableCtrl:
            glTools.rig.utils.tagCtrl(twistJoints[i], 'tertiary')
            ctrlBuilder.controlShape(transform=twistJoints[i], controlType='sphere', controlScale=twistCtrlScale)

        # Set Display Override
        if enableCtrl:
            glTools.utils.base.displayOverride(twistJoints[i], overrideEnable=1, overrideDisplay=0, overrideLOD=1)
        else:
            glTools.utils.base.displayOverride(twistJoints[i], overrideEnable=1, overrideDisplay=2, overrideLOD=0)

    # Create Twist Group
    twistGrp = cmds.joint(n=prefix + '_twistJoint_grp')
    glTools.utils.base.displayOverride(twistGrp, overrideEnable=1, overrideDisplay=2, overrideLOD=1)
    glTools.utils.transform.match(twistGrp, sourceJoint)
    cmds.setAttr(twistGrp + '.segmentScaleCompensate', 0)
    cmds.setAttr(twistGrp + '.drawStyle', 2)  # None
    cmds.setAttr(twistGrp + '.radius', 0)
    cmds.parent(twistGrp, sourceJoint)
    cmds.parent(twistJointGrps, twistGrp)

    # Connect Inverse Scale
    for twistJointGrp in twistJointGrps:
        cmds.connectAttr(sourceJoint + '.scale', twistJointGrp + '.inverseScale', f=True)

    # ==========================
    # - Create Twist Aim Setup -
    # ==========================

    # Create Twist Aim Joint
    twistAimJnt = cmds.duplicate(sourceJoint, po=True, n=prefix + '_twistAim_jnt')[0]
    # Remove user attributes
    glTools.utils.attribute.deleteUserAttrs(twistAimJnt)
    # Parent to source joint
    cmds.parent(twistAimJnt, sourceJoint)
    # Display Overrides
    glTools.utils.base.displayOverride(twistAimJnt, overrideEnable=1, overrideDisplay=2, overrideLOD=0)

    # Create Twist Aim Locator
    twistAimLoc = cmds.group(em=True, n=prefix + '_twistAim_loc')
    cmds.delete(cmds.pointConstraint(targetJoint, twistAimLoc, mo=False))
    cmds.delete(cmds.orientConstraint(sourceJoint, twistAimLoc, mo=False))
    cmds.parent(twistAimLoc, targetJoint)
    # Display Overrides
    glTools.utils.base.displayOverride(twistAimLoc, overrideEnable=1, overrideDisplay=2, overrideLOD=0)

    # Create Twist Aim Constraint
    twistAicmdson = cmds.aicmdsonstraint(targetJoint,
                                   twistAimJnt,
                                   aim=axisDict[aimAxis],
                                   u=axisDict[upAxis],
                                   wu=axisDict[upAxis],
                                   wuo=twistAimLoc,
                                   wut='objectrotation')[0]

    # ========================
    # - Connect Twist Joints -
    # ========================

    twistMultNode = []
    for i in range(len(twistJoints)):
        alphaInd = glTools.utils.stringUtils.alphaIndex(i, upper=True)
        twistMult = cmds.createNode('multDoubleLinear', n=prefix + '_twist' + alphaInd + '_multDoubleLinear')
        cmds.connectAttr(twistAimJnt + '.r' + aimAxis[-1], twistMult + '.input1', f=True)
        cmds.connectAttr(twistJoints[i] + '.twist', twistMult + '.input2', f=True)
        cmds.connectAttr(twistMult + '.output', twistJointGrps[i] + '.r' + aimAxis[-1], f=True)
        twistMultNode.append(twistMult)

    # ======================
    # - Set Channel States -
    # ======================

    chStateUtil = glTools.utils.channelState.ChannelState()
    chStateUtil.setFlags([2, 2, 2, 2, 2, 2, 2, 2, 2, 1], objectList=[twistGrp])
    chStateUtil.setFlags([0, 0, 0, 0, 0, 0, 0, 0, 0, 1], objectList=twistJoints)
    chStateUtil.setFlags([2, 2, 2, 2, 2, 2, 2, 2, 2, 1], objectList=twistJointGrps)
    chStateUtil.setFlags([2, 2, 2, 1, 1, 1, 2, 2, 2, 1], objectList=[twistAimJnt])
    chStateUtil.setFlags([2, 2, 2, 2, 2, 2, 2, 2, 2, 1], objectList=[twistAimLoc])

    # =================
    # - Return Result -
    # =================

    result = {}
    result['twistGrp'] = twistGrp
    result['twistJoints'] = twistJoints
    result['twistJointGrps'] = twistJointGrps
    result['twistDriveJoint'] = twistAimJnt
    result['twistAimLocator'] = twistAimLoc
    result['twistConstraint'] = twistAicmdson
    result['twistMultNodes'] = twistMultNode
    return result


def build_shoulder(shoulder,
                   spine,
                   numJoints=4,
                   shoulderAim='x',
                   shoulderFront='y',
                   spineAim='x',
                   spineFront='y',
                   enableCtrl=False,
                   prefix=''):
    """
    Build shoudler twist using custom shoulderConstraint node
    @param numJoints:
    @param shoulder: Shoulder or upper arm joint
    @type shoulder: str
    @param spine: Spine end joint
    @type spine: str
    @param shoulderAim: Axis along the length of the shoulder joint
    @type shoulderAim: list or tuple
    @param shoulderFront: Forward facing axis of the shoulder joint
    @type shoulderFront: list or tuple
    @param spineAim: Axis along the length of the spine joint
    @type spineAim: list or tuple
    @param spineFront: Forward facing axis of the spine joint
    @type spineFront: list or tuple
    @param enableCtrl: Enable the twist child joint as a control
    @type enableCtrl: bool
    @param prefix: Naming prefix for created nodes
    @type prefix: str
    """
    # ==========
    # - Checks -
    # ==========

    # Define Axis Dictionary
    axisDict = {'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1), '-x': (-1, 0, 0), '-y': (0, -1, 0), '-z': (0, 0, -1)}

    if not cmds.objExists(shoulder):
        raise Exception('Shoulder joint "' + shoulder + '" does not exist!')
    if not cmds.objExists(spine):
        raise Exception('Spine joint "' + spine + '" does not exist!')

    if not axisDict.has_key(shoulderAim):
        raise Exception('Invalid shoulder aim axis value! ("' + shoulderAim + '")')
    if not axisDict.has_key(shoulderFront):
        raise Exception('Invalid shoulder front axis value! ("' + shoulderFront + '")')
    if not axisDict.has_key(spineAim):
        raise Exception('Invalid spine aim axis value! ("' + spineAim + '")')
    if not axisDict.has_key(spineFront):
        raise Exception('Invalid spine front axis value! ("' + spineFront + '")')

    if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(shoulder)

    # Check Plugin
    if not cmds.pluginInfo('twistConstraint', q=True, l=True):
        try:
            cmds.loadPlugin('twistConstraint')
        except:
            raise Exception('Unable to load plugin "twistConstraint"!')

    # =====================
    # - Configure Control -
    # =====================

    twistCtrlScale = 0.2
    ctrlBuilder = glTools.tools.controlBuilder.ControlBuilder()

    # =======================
    # - Create Twist Joints -
    # =======================

    twistJoints = createTwistJoints(joint=shoulder,
                                    numTwistJoints=numJoints,
                                    offsetAxis=shoulderAim[-1],
                                    prefix=prefix)

    # Reverse twist joint list
    twistJoints.reverse()

    # Create Twist Driver Joint
    cmds.select(cl=True)
    shoulderTwist = cmds.joint(n=prefix + '_twistDrive_jnt')
    shoulderTwistGrp = glTools.utils.joint.group(shoulderTwist)
    cmds.delete(cmds.parentConstraint(shoulder, shoulderTwistGrp))
    cmds.parent(shoulderTwistGrp, shoulder)
    glTools.utils.base.displayOverride(shoulderTwist, overrideEnable=1, overrideDisplay=2, overrideLOD=0)

    # Create Shoulder Twist Joints
    twistJointGrps = []
    twistFactor = 1.0 / (len(twistJoints) - 1)
    jntLen = glTools.utils.joint.length(shoulder)
    for i in range(len(twistJoints)):

        # Add twist attribute
        cmds.addAttr(twistJoints[i], ln='twist', min=-1.0, max=1.0, dv=twistFactor * i)

        # Add Twist Joint Group
        twistJointGrp = glTools.utils.joint.group(twistJoints[i], indexStr='Twist')
        twistJointGrps.append(twistJointGrp)

        # Tag Bind joint
        glTools.rig.utils.tagBindJoint(twistJoints[i], True)

        # Create Joint Control
        if enableCtrl:
            glTools.rig.utils.tagCtrl(twistJoints[i], 'tertiary')
            ctrlBuilder.controlShape(transform=twistJoints[i], controlType='sphere', controlScale=twistCtrlScale)

        # Set Display Override
        if enableCtrl:
            glTools.utils.base.displayOverride(twistJoints[i], overrideEnable=1, overrideDisplay=0, overrideLOD=1)
        else:
            glTools.utils.base.displayOverride(twistJoints[i], overrideEnable=1, overrideDisplay=2, overrideLOD=0)

    # Create Twist Group
    twistGrp = cmds.joint(n=prefix + '_twistJoint_grp')
    glTools.utils.base.displayOverride(twistGrp, overrideEnable=1, overrideLOD=1)
    glTools.utils.transform.match(twistGrp, shoulder)
    cmds.setAttr(twistGrp + '.segmentScaleCompensate', 0)
    cmds.setAttr(twistGrp + '.drawStyle', 2)  # None
    cmds.setAttr(twistGrp + '.radius', 0)
    cmds.parent(twistGrp, shoulder)
    cmds.parent(twistJointGrps, twistGrp)

    # Connect Inverse Scale
    for twistJointGrp in twistJointGrps:
        cmds.connectAttr(shoulder + '.scale', twistJointGrp + '.inverseScale', f=True)

    # ===============================
    # - Create Shoulder Twist Setup -
    # ===============================

    # Create shoulderConstraint node
    shoulderCon = cmds.createNode('shoulderConstraint', n=prefix + '_shoulderConstraint')

    # Set and connect shoulderConstraint attributes
    cmds.connectAttr(shoulder + '.worldMatrix[0]', shoulderCon + '.shoulder', f=True)
    cmds.connectAttr(spine + '.worldMatrix[0]', shoulderCon + '.spine', f=True)
    cmds.connectAttr(shoulderTwist + '.parentInverseMatrix[0]', shoulderCon + '.parentInverseMatrix', f=True)
    cmds.connectAttr(shoulderTwist + '.rotateOrder', shoulderCon + '.rotateOrder', f=True)
    cmds.connectAttr(shoulderTwist + '.jointOrient', shoulderCon + '.jointOrient', f=True)
    cmds.setAttr(shoulderCon + '.shoulderAim', *axisDict[shoulderAim])
    cmds.setAttr(shoulderCon + '.shoulderFront', *axisDict[shoulderFront])
    cmds.setAttr(shoulderCon + '.spineAim', *axisDict[spineAim])
    cmds.setAttr(shoulderCon + '.spineFront', *axisDict[spineFront])
    cmds.setAttr(shoulderCon + '.raisedAngleOffset', 0)

    # Connect to shoudler twist joint
    cmds.connectAttr(shoulderCon + '.outRotate', shoulderTwist + '.rotate', f=True)

    # Correct initial offset
    twistOffset = cmds.getAttr(shoulderTwist + '.r' + shoulderAim[-1])
    cmds.setAttr(shoulderTwist + '.jo' + shoulderAim[-1], twistOffset)

    # ========================
    # - Connect Twist Joints -
    # ========================

    twistMultNode = []
    for i in range(len(twistJoints)):
        alphaInd = glTools.utils.stringUtils.alphaIndex(i, upper=True)
        twistMult = cmds.createNode('multDoubleLinear', n=prefix + '_twist' + alphaInd + '_multDoubleLinear')
        cmds.connectAttr(shoulderTwist + '.r' + shoulderAim[-1], twistMult + '.input1', f=True)
        cmds.connectAttr(twistJoints[i] + '.twist', twistMult + '.input2', f=True)
        cmds.connectAttr(twistMult + '.output', twistJointGrps[i] + '.r' + shoulderAim[-1], f=True)
        twistMultNode.append(twistMult)

    # Reverse twist joint list
    twistJoints.reverse()

    # ======================
    # - Set Channel States -
    # ======================

    chStateUtil = glTools.utils.channelState.ChannelState()
    chStateUtil.setFlags([2, 2, 2, 2, 2, 2, 2, 2, 2, 1], objectList=[twistGrp])
    chStateUtil.setFlags([0, 0, 0, 0, 0, 0, 0, 0, 0, 1], objectList=twistJoints)
    chStateUtil.setFlags([2, 2, 2, 2, 2, 2, 2, 2, 2, 1], objectList=twistJointGrps)
    chStateUtil.setFlags([2, 2, 2, 2, 2, 2, 2, 2, 2, 1], objectList=[shoulderTwistGrp])
    chStateUtil.setFlags([2, 2, 2, 1, 1, 1, 2, 2, 2, 1], objectList=[shoulderTwist])

    # =================
    # - Return Result -
    # =================

    result = {}
    result['twistGrp'] = twistGrp
    result['twistJoints'] = twistJoints
    result['twistJointGrps'] = twistJointGrps
    result['twistDriveJoint'] = shoulderTwist
    result['twistConstraint'] = shoulderCon
    result['twistMultNodes'] = twistMultNode
    return result


def build_hip(hip,
              pelvis,
              numJoints=4,
              hipAim='x',
              hipFront='y',
              pelvisAim='x',
              pelvisFront='y',
              enableCtrl=False,
              prefix=''):
    """
    Build hip twist using custom hipConstraint node
    @param numJoints:
    @param hip: Hip or upper leg joint
    @type hip: str
    @param pelvis: Pelvis joint
    @type pelvis: str
    @param hipAim: Axis along the length of the hip/leg joint
    @type hipAim: list or tuple
    @param hipFront: Forward facing axis of the hip/leg joint
    @type hipFront: list or tuple
    @param pelvisAim: Axis along the length of the pelvis joint
    @type pelvisAim: list or tuple
    @param pelvisFront: Forward facing axis of the pelvis joint
    @type pelvisFront: list or tuple
    @param enableCtrl: Enable the twist child joint as a control
    @type enableCtrl: bool
    @param prefix: Naming prefix for created nodes
    @type prefix: str
    """
    # ==========
    # - Checks -
    # ==========

    # Define Axis Dictionary
    axisDict = {'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1), '-x': (-1, 0, 0), '-y': (0, -1, 0), '-z': (0, 0, -1)}

    if not cmds.objExists(hip):
        raise Exception('Hip joint "' + hip + '" does not exist!')
    if not cmds.objExists(pelvis):
        raise Exception('Pelvis joint "' + pelvis + '" does not exist!')

    if not axisDict.has_key(hipAim):
        raise Exception('Invalid hip aim axis value! ("' + hipAim + '")')
    if not axisDict.has_key(hipFront):
        raise Exception('Invalid hip front axis value! ("' + hipFront + '")')
    if not axisDict.has_key(pelvisAim):
        raise Exception('Invalid pelvis aim axis value! ("' + pelvisAim + '")')
    if not axisDict.has_key(pelvisFront):
        raise Exception('Invalid pelvis front axis value! ("' + pelvisFront + '")')

    if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(hip)

    # Check Plugin
    if not cmds.pluginInfo('twistConstraint', q=True, l=True):
        try:
            cmds.loadPlugin('twistConstraint')
        except:
            raise Exception('Unable to load plugin "twistConstraint"!')

    # ======================
    # - Configure Modifier -
    # ======================

    twistCtrlScale = 0.2
    ctrlBuilder = glTools.tools.controlBuilder.ControlBuilder()

    # =======================
    # - Create Twist Joints -
    # =======================

    twistJoints = createTwistJoints(joint=hip,
                                    numTwistJoints=numJoints,
                                    offsetAxis=hipAim[-1],
                                    prefix=prefix)
    # Reverse twist joint list
    twistJoints.reverse()

    # Create Twist Driver Joint
    cmds.select(cl=True)
    hipTwist = cmds.joint(n=prefix + '_twistDrive_jnt')
    hipTwistGrp = glTools.utils.joint.group(hipTwist)
    cmds.delete(cmds.parentConstraint(hip, hipTwistGrp))
    cmds.parent(hipTwistGrp, hip)
    glTools.utils.base.displayOverride(hipTwist, overrideEnable=1, overrideDisplay=2, overrideLOD=0)

    # Create Hip Twist Joints
    twistJointGrps = []
    twistFactor = 1.0 / (len(twistJoints) - 1)
    jntLen = glTools.utils.joint.length(hip)
    for i in range(len(twistJoints)):

        # Add Twist Control Attribute
        cmds.addAttr(twistJoints[i], ln='twist', min=-1.0, max=1.0, dv=twistFactor * i)

        # Add Twist Joint Group
        twistJointGrp = glTools.utils.joint.group(twistJoints[i], indexStr='Twist')
        twistJointGrps.append(twistJointGrp)

        # Tag Bind Joint
        glTools.rig.utils.tagBindJoint(twistJoints[i], True)

        # Create Joint Control
        if enableCtrl:
            glTools.rig.utils.tagCtrl(twistJoints[i], 'tertiary')
            ctrlBuilder.controlShape(transform=twistJoints[i], controlType='sphere', controlScale=twistCtrlScale)

        # Set Display Override
        if enableCtrl:
            glTools.utils.base.displayOverride(twistJoints[i], overrideEnable=1, overrideDisplay=0, overrideLOD=1)
        else:
            glTools.utils.base.displayOverride(twistJoints[i], overrideEnable=1, overrideDisplay=2, overrideLOD=0)

    # Create Twist Group
    twistGrp = cmds.joint(n=prefix + '_twistJoint_grp')
    glTools.utils.base.displayOverride(twistGrp, overrideEnable=1, overrideLOD=1)
    glTools.utils.transform.match(twistGrp, hip)
    cmds.setAttr(twistGrp + '.segmentScaleCompensate', 0)
    cmds.setAttr(twistGrp + '.drawStyle', 2)  # None
    cmds.setAttr(twistGrp + '.radius', 0)
    cmds.parent(twistGrp, hip)
    cmds.parent(twistJointGrps, twistGrp)

    # Connect Inverse Scale
    for twistJointGrp in twistJointGrps:
        cmds.connectAttr(hip + '.scale', twistJointGrp + '.inverseScale', f=True)

    # ==========================
    # - Create Hip Twist Setup -
    # ==========================

    # Create hipConstraint node
    hipCon = cmds.createNode('hipConstraint', n=prefix + '_hipConstraint')

    # Set and connect hipConstraint attributes
    cmds.connectAttr(hip + '.worldMatrix[0]', hipCon + '.hip', f=True)
    cmds.connectAttr(pelvis + '.worldMatrix[0]', hipCon + '.pelvis', f=True)
    cmds.connectAttr(hipTwist + '.parentInverseMatrix[0]', hipCon + '.parentInverseMatrix', f=True)
    cmds.connectAttr(hipTwist + '.rotateOrder', hipCon + '.rotateOrder', f=True)
    cmds.connectAttr(hipTwist + '.jointOrient', hipCon + '.jointOrient', f=True)
    cmds.setAttr(hipCon + '.hipAim', *axisDict[hipAim])
    cmds.setAttr(hipCon + '.hipFront', *axisDict[hipFront])
    cmds.setAttr(hipCon + '.pelvisAim', *axisDict[pelvisAim])
    cmds.setAttr(hipCon + '.pelvisFront', *axisDict[pelvisFront])

    # Connect to hip twist joint
    cmds.connectAttr(hipCon + '.outRotate', hipTwist + '.rotate', f=True)

    # Correct initial offset
    twistOffset = cmds.getAttr(hipTwist + '.r' + hipAim[-1])
    cmds.setAttr(hipTwist + '.jo' + hipAim[-1], twistOffset)

    # ========================
    # - Connect Twist Joints -
    # ========================

    twistMultNode = []
    for i in range(len(twistJoints)):
        alphaInd = glTools.utils.stringUtils.alphaIndex(i, upper=True)
        twistMult = cmds.createNode('multDoubleLinear', n=prefix + '_twist' + alphaInd + '_multDoubleLinear')
        cmds.connectAttr(hipTwist + '.r' + hipAim[-1], twistMult + '.input1', f=True)
        cmds.connectAttr(twistJoints[i] + '.twist', twistMult + '.input2', f=True)
        cmds.connectAttr(twistMult + '.output', twistJointGrps[i] + '.r' + hipAim[-1], f=True)
        twistMultNode.append(twistMult)

    # Reverse twist joint list
    twistJoints.reverse()

    # ======================
    # - Set Channel States -
    # ======================

    chStateUtil = glTools.utils.channelState.ChannelState()
    chStateUtil.setFlags([2, 2, 2, 2, 2, 2, 2, 2, 2, 1], objectList=[twistGrp])
    chStateUtil.setFlags([0, 0, 0, 0, 0, 0, 0, 0, 0, 1], objectList=twistJoints)
    chStateUtil.setFlags([2, 2, 2, 2, 2, 2, 2, 2, 2, 1], objectList=twistJointGrps)
    chStateUtil.setFlags([2, 2, 2, 2, 2, 2, 2, 2, 2, 1], objectList=[hipTwistGrp])
    chStateUtil.setFlags([2, 2, 2, 1, 1, 1, 2, 2, 2, 1], objectList=[hipTwist])

    # =================
    # - Return Result -
    # =================

    result = {}
    result['twistGrp'] = twistGrp
    result['twistJoints'] = twistJoints
    result['twistJointGrps'] = twistJointGrps
    result['twistDriveJoint'] = hipTwist
    result['twistConstraint'] = hipCon
    result['twistMultNodes'] = twistMultNode
    return result
