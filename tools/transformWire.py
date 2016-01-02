import maya.cmds as cmds
import glTools.utils.transformWire


def connectToSource(srcNS, dstNS, wireCrv, baseCrv='', addArmIk=False, connectFingers=False):
    """
    """
    # ==========
    # - Checks -
    # ==========

    if srcNS: srcNS += ':'
    if dstNS: dstNS += ':'

    # Duplicate Wire to Generate Base
    if not baseCrv: baseCrv = cmds.duplicate(wireCrv, n=wireCrv + 'Base')[0]

    # ========================
    # - Target (IK) Locators -
    # ========================

    # Create Locators (Source)
    hip_src = cmds.spaceLocator(n='hip_src')[0]
    lf_foot_src = cmds.spaceLocator(n='lf_foot_src')[0]
    rt_foot_src = cmds.spaceLocator(n='rt_foot_src')[0]
    lf_knee_src = cmds.spaceLocator(n='lf_knee_src')[0]
    rt_knee_src = cmds.spaceLocator(n='rt_knee_src')[0]
    if addArmIk:
        lf_hand_src = cmds.spaceLocator(n='lf_hand_src')[0]
        rt_hand_src = cmds.spaceLocator(n='rt_hand_src')[0]
        lf_elbow_src = cmds.spaceLocator(n='lf_elbow_src')[0]
        rt_elbow_src = cmds.spaceLocator(n='rt_elbow_src')[0]

    # Create Locators (Destination)
    hip_dst = cmds.spaceLocator(n='hip_dst')[0]
    lf_foot_dst = cmds.spaceLocator(n='lf_foot_dst')[0]
    rt_foot_dst = cmds.spaceLocator(n='rt_foot_dst')[0]
    lf_knee_dst = cmds.spaceLocator(n='lf_knee_dst')[0]
    rt_knee_dst = cmds.spaceLocator(n='rt_knee_dst')[0]
    if addArmIk:
        lf_hand_dst = cmds.spaceLocator(n='lf_hand_dst')[0]
        rt_hand_dst = cmds.spaceLocator(n='rt_hand_dst')[0]
        lf_elbow_dst = cmds.spaceLocator(n='lf_elbow_dst')[0]
        rt_elbow_dst = cmds.spaceLocator(n='rt_elbow_dst')[0]

    # Position Locators (Source)
    cmds.delete(cmds.parentConstraint(srcNS + 'Hips', hip_src))
    cmds.delete(cmds.parentConstraint(srcNS + 'LeftFoot', lf_foot_src))
    cmds.delete(cmds.parentConstraint(srcNS + 'RightFoot', rt_foot_src))
    cmds.delete(cmds.parentConstraint(srcNS + 'LeftLeg', lf_knee_src))
    cmds.delete(cmds.parentConstraint(srcNS + 'RightLeg', rt_knee_src))
    if addArmIk:
        cmds.delete(cmds.parentConstraint(srcNS + 'LeftHand', lf_hand_src))
        cmds.delete(cmds.parentConstraint(srcNS + 'RightHand', rt_hand_src))
        cmds.delete(cmds.parentConstraint(srcNS + 'LeftForeArm', lf_elbow_src))
        cmds.delete(cmds.parentConstraint(srcNS + 'RightForeArm', rt_elbow_src))

    # Position Locators (Destination)
    cmds.delete(cmds.parentConstraint(dstNS + 'Hips', hip_dst))
    cmds.delete(cmds.parentConstraint(dstNS + 'LeftFoot', lf_foot_dst))
    cmds.delete(cmds.parentConstraint(dstNS + 'RightFoot', rt_foot_dst))
    cmds.delete(cmds.parentConstraint(dstNS + 'LeftLeg', lf_knee_dst))
    cmds.delete(cmds.parentConstraint(dstNS + 'RightLeg', rt_knee_dst))
    if addArmIk:
        cmds.delete(cmds.parentConstraint(dstNS + 'LeftHand', lf_hand_dst))
        cmds.delete(cmds.parentConstraint(dstNS + 'RightHand', rt_hand_dstc))
        cmds.delete(cmds.parentConstraint(dstNS + 'LeftLeg', lf_elbow_dst))
        cmds.delete(cmds.parentConstraint(dstNS + 'RightLeg', rt_elbow_dst))

    # Parent Locators (Source)
    cmds.parent(hip_src, srcNS + 'Hips')
    cmds.parent(lf_foot_src, srcNS + 'LeftFoot')
    cmds.parent(rt_foot_src, srcNS + 'RightFoot')
    cmds.parent(lf_knee_src, srcNS + 'LeftLeg')
    cmds.parent(rt_knee_src, srcNS + 'RightLeg')
    if addArmIk:
        cmds.parent(lf_hand_loc, srcNS + 'LeftHand')
        cmds.parent(rt_hand_loc, srcNS + 'RightHand')
        cmds.parent(lf_elbow_loc, srcNS + 'LeftForeArm')
        cmds.parent(rt_elbow_loc, srcNS + 'RightForeArm')

    # =====================
    # - Connect To Source -
    # =====================

    # Hip Constraint
    hip_con = cmds.parentConstraint(hip_dst, dstNS + 'Hips')[0]

    # -------------
    # - Legs (IK) -
    # -------------

    lf_leg_ik = \
    cmds.ikHandle(startJoint=dstNS + 'LeftUpLeg', endEffector=dstNS + 'LeftFoot', solver='ikRPsolver', n='lf_leg_ik')[0]
    rt_leg_ik = \
    cmds.ikHandle(startJoint=dstNS + 'RightUpLeg', endEffector=dstNS + 'RightFoot', solver='ikRPsolver', n='rt_leg_ik')[0]

    # Limit Roll Bones
    cmds.transformLimits(dstNS + 'LeftLegRoll', ry=(0, 0), rz=(0, 0), ery=(1, 1), erz=(1, 1))
    cmds.transformLimits(dstNS + 'RightLegRoll', ry=(0, 0), rz=(0, 0), ery=(1, 1), erz=(1, 1))
    cmds.transformLimits(dstNS + 'LeftUpLegRoll', ry=(0, 0), rz=(0, 0), ery=(1, 1), erz=(1, 1))
    cmds.transformLimits(dstNS + 'RightUpLegRoll', ry=(0, 0), rz=(0, 0), ery=(1, 1), erz=(1, 1))

    # Constrain IK
    lf_leg_ik_con = cmds.parentConstraint(lf_foot_dst, lf_leg_ik)
    rt_leg_ik_con = cmds.parentConstraint(rt_foot_dst, rt_leg_ik)
    lf_leg_pv_con = cmds.poleVectorConstraint(lf_knee_dst, lf_leg_ik)
    rt_leg_pv_con = cmds.poleVectorConstraint(rt_knee_dst, rt_leg_ik)

    # Constrain Foot
    lf_foot_con = cmds.orientConstraint(lf_foot_dst, dstNS + 'LeftFoot')
    rt_foot_con = cmds.orientConstraint(rt_foot_dst, dstNS + 'RightFoot')

    # -------------
    # - Arms (IK) -
    # -------------

    if addArmIk:
        lf_arm_ik = \
        cmds.ikHandle(startJoint=dstNS + 'LeftArm', endEffector=dstNS + 'LeftHand', solver='ikRPsolver', n='lf_arm_ik')[0]
        rt_arm_ik = \
        cmds.ikHandle(startJoint=dstNS + 'RightArm', endEffector=dstNS + 'RightHand', solver='ikRPsolver', n='rt_arm_ik')[
            0]

        # Limit Roll Bones
        cmds.transformLimits(dstNS + 'LeftArmRoll', ry=(0, 0), rz=(0, 0), ery=(1, 1), erz=(1, 1))
        cmds.transformLimits(dstNS + 'RightArmRoll', ry=(0, 0), rz=(0, 0), ery=(1, 1), erz=(1, 1))
        cmds.transformLimits(dstNS + 'LeftForeArmRoll', ry=(0, 0), rz=(0, 0), ery=(1, 1), erz=(1, 1))
        cmds.transformLimits(dstNS + 'RightForeArmRoll', ry=(0, 0), rz=(0, 0), ery=(1, 1), erz=(1, 1))

        # Constrain IK
        lf_arm_ik_con = cmds.parentConstraint(lf_hand_dst, lf_arm_ik)
        rt_arm_ik_con = cmds.parentConstraint(rt_hand_dst, rt_arm_ik)
        lf_arm_pv_con = cmds.poleVectorConstraint(lf_elbow_dst, lf_leg_ik)
        rt_arm_pv_con = cmds.poleVectorConstraint(rt_elbow_dst, rt_leg_ik)

        # Constrain Hand
        lf_hand_con = cmds.orientConstraint(lf_hand_dst, dstNS + 'LeftHand')
        rt_hand_con = cmds.orientConstraint(rt_hand_dst, dstNS + 'RightHand')

    # -----------------------
    # - Upper Body Rotation -
    # -----------------------

    body_jnts = ['Spine',
                 'Spine1',
                 'Spine2',
                 'LeftShoulder',
                 'RightShoulder',
                 'Neck',
                 'Head']

    arm_jnts = ['Arm',
                'ArmRoll',
                'ForeArm',
                'ForeArmRoll',
                'Hand']

    hand_jnts = ['HandThumb1',
                 'HandThumb2',
                 'HandThumb3',
                 'InHandIndex',
                 'InHandMiddle',
                 'InHandRing',
                 'InHandPinky',
                 'HandIndex1',
                 'HandMiddle1',
                 'HandRing1',
                 'HandPinky1',
                 'HandPinky2',
                 'HandRing2',
                 'HandMiddle2',
                 'HandIndex2',
                 'HandPinky3',
                 'HandRing3',
                 'HandMiddle3',
                 'HandIndex3']

    foot_jnts = ['ToeBase']

    # Connect Body
    for jnt in body_jnts:
        cmds.connectAttr(srcNS + jnt + '.r', dstNS + jnt + '.r', f=True)

    # Connect Feet
    for side in ['Left', 'Right']:
        for jnt in foot_jnts:
            cmds.connectAttr(srcNS + side + jnt + '.r', dstNS + side + jnt + '.r', f=True)

    # Connect Arms
    if not addArmIk:
        for side in ['Left', 'Right']:
            for jnt in arm_jnts:
                cmds.connectAttr(srcNS + side + jnt + '.r', dstNS + side + jnt + '.r', f=True)

    # Connect Fingers
    if connectFingers:
        for side in ['Left', 'Right']:
            for jnt in hand_jnts:
                cmds.connectAttr(srcNS + side + jnt + '.r', dstNS + side + jnt + '.r', f=True)

    # ========================
    # - Transform Wire Setup -
    # ========================

    # Hips
    glTools.utils.transformWire.create(wireCrv=wireCrv,
                                       baseCrv=baseCrv,
                                       srcTransform=hip_src,
                                       dstTransform=hip_dst,
                                       mode='distance',
                                       aim=1.0,
                                       tilt=0.0,
                                       bank=0.0,
                                       connectPos=True,
                                       connectRot=True,
                                       orientList=[],
                                       prefix='')

    # Legs (lf_foot)
    glTools.utils.transformWire.create(wireCrv=wireCrv,
                                       baseCrv=baseCrv,
                                       srcTransform=lf_foot_src,
                                       dstTransform=lf_foot_dst,
                                       mode='distance',
                                       aim=1.0,
                                       tilt=1.0,
                                       bank=0.0,
                                       connectPos=True,
                                       connectRot=True,
                                       orientList=[],
                                       prefix='')

    # Legs (rt_foot)
    glTools.utils.transformWire.create(wireCrv=wireCrv,
                                       baseCrv=baseCrv,
                                       srcTransform=rt_foot_src,
                                       dstTransform=rt_foot_dst,
                                       mode='distance',
                                       aim=1.0,
                                       tilt=1.0,
                                       bank=0.0,
                                       connectPos=True,
                                       connectRot=True,
                                       orientList=[],
                                       prefix='')

    # Legs (lf_knee)
    glTools.utils.transformWire.create(wireCrv=wireCrv,
                                       baseCrv=baseCrv,
                                       srcTransform=lf_knee_src,
                                       dstTransform=lf_knee_dst,
                                       mode='distance',
                                       aim=1.0,
                                       tilt=1.0,
                                       bank=.0,
                                       connectPos=True,
                                       connectRot=True,
                                       orientList=[],
                                       prefix='')

    # Legs (rt_knee)
    glTools.utils.transformWire.create(wireCrv=wireCrv,
                                       baseCrv=baseCrv,
                                       srcTransform=rt_knee_src,
                                       dstTransform=rt_knee_dst,
                                       mode='distance',
                                       aim=1.0,
                                       tilt=1.0,
                                       bank=.0,
                                       connectPos=True,
                                       connectRot=True,
                                       orientList=[],
                                       prefix='')

    # Arms
    if addArmIk:
        # Arms (lf_hand)
        glTools.utils.transformWire.create(wireCrv=wireCrv,
                                           baseCrv=baseCrv,
                                           srcTransform=lf_hand_src,
                                           dstTransform=lf_hand_dst,
                                           mode='distance',
                                           aim=1.0,
                                           tilt=0.0,
                                           bank=0.0,
                                           connectPos=True,
                                           connectRot=True,
                                           orientList=[],
                                           prefix='')

        # Arms (rt_hand)
        glTools.utils.transformWire.create(wireCrv=wireCrv,
                                           baseCrv=baseCrv,
                                           srcTransform=rt_hand_src,
                                           dstTransform=rt_hand_dst,
                                           mode='distance',
                                           aim=1.0,
                                           tilt=0.0,
                                           bank=0.0,
                                           connectPos=True,
                                           connectRot=True,
                                           orientList=[],
                                           prefix='')

        # Arms (lf_elbow)
        glTools.utils.transformWire.create(wireCrv=wireCrv,
                                           baseCrv=baseCrv,
                                           srcTransform=lf_elbow_src,
                                           dstTransform=lf_elbow_dst,
                                           mode='distance',
                                           aim=1.0,
                                           tilt=0.0,
                                           bank=0.0,
                                           connectPos=True,
                                           connectRot=True,
                                           orientList=[],
                                           prefix='')

        # Arms (rt_elbow)
        glTools.utils.transformWire.create(wireCrv=wireCrv,
                                           baseCrv=baseCrv,
                                           srcTransform=rt_elbow_src,
                                           dstTransform=rt_elbow_dst,
                                           mode='distance',
                                           aim=1.0,
                                           tilt=0.0,
                                           bank=0.0,
                                           connectPos=True,
                                           connectRot=True,
                                           orientList=[],
                                           prefix='')
