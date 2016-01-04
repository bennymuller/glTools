import maya.cmds as cmds
import glTools.utils.namespace


def cutPasteKey(src, dst):
    """
    @param dst:
    @param src:
    """
    keys = cmds.cutKey(src)
    if keys: cmds.pasteKey(dst)


def swapAnim(srcCtrl, dstCtrl):
    """
    @param srcCtrl:
    @param dstCtrl:
    """
    # Temp Key Node
    tmpCtrl = cmds.duplicate(srcCtrl, po=True, n=srcCtrl + 'TEMP')[0]

    # Swap Left <> Right
    cutPasteKey(srcCtrl, tmpCtrl)
    cutPasteKey(dstCtrl, srcCtrl)
    cutPasteKey(tmpCtrl, dstCtrl)

    # Delete Temp Node
    if cmds.objExists(tmpCtrl):
        try:
            cmds.delete(tmpCtrl)
        except:
            print('Error deleting temp control object "' + tmpCtrl + '"!')


def mirrorBipedAnim(rigNS):
    """
    Mirror biped body animation
    @param rigNS: Rig namespace.
    @type rigNS: str
    """
    # =============
    # - Check Rig -
    # =============

    if not cmds.namespace(ex=rigNS):
        raise Exception('Rig namespace "' + rigNS + '" not found! Unable to mirror animation...')

    # ====================
    # - Get Rig Controls -
    # ====================

    # Body
    bodyA = rigNS + ':cn_bodyA_jnt'
    bodyB = rigNS + ':cn_bodyB_jnt'

    # Spine/Neck/Head
    spineA = rigNS + ':cn_spineA_jnt'
    spineB = rigNS + ':cn_spineB_jnt'
    spineC = rigNS + ':cn_spineC_jnt'

    spineBase = rigNS + ':cn_spine_base_ctrl'
    spineMid = rigNS + ':cn_spine_mid_ctrl'
    spineTop = rigNS + ':cn_spine_top_ctrl'

    neck = rigNS + ':cn_neckA_jnt'
    head = rigNS + ':cn_headA_jnt'

    # Arms
    clav = rigNS + ':SIDE_clavicleA_jnt'
    armFkA = rigNS + ':SIDE_arm_fkA_jnt'
    armFkB = rigNS + ':SIDE_arm_fkB_jnt'
    armIk = rigNS + ':SIDE_arm_ik_ctrl'
    armPv = rigNS + ':SIDE_arm_pv_ctrl'
    hand = rigNS + ':SIDE_handA_jnt'

    # Fingers
    fingerList = ['thumbA', 'thumbB', 'thumbC',
                  'indexA', 'indexB', 'indexC', 'indexD',
                  'middleA', 'middleB', 'middleC', 'middleD',
                  'ringA', 'ringB', 'ringC', 'ringD',
                  'pinkyA', 'pinkyB', 'pinkyC', 'pinkyD']
    fingers = [rigNS + ':SIDE_' + finger + '_jnt' for finger in fingerList]

    # Legs
    legFkA = rigNS + ':SIDE_leg_fkA_jnt'
    legFkB = rigNS + ':SIDE_leg_fkB_jnt'
    legIk = rigNS + ':SIDE_leg_ik_ctrl'
    legPv = rigNS + ':SIDE_leg_pv_ctrl'

    # Feet
    footIk = rigNS + ':SIDE_foot_ik_ctrl'
    toeIk = rigNS + ':SIDE_foot_toe_ctrl'
    footFkA = rigNS + ':foot_fkA_jnt'
    footFkB = rigNS + ':foot_fkB_jnt'

    # ====================
    # - Mirror Animation -
    # ====================

    # Body
    for ctrl in [bodyA, bodyB]:
        if cmds.objExists(ctrl):
            cmds.scaleKey(ctrl, at=['tx', 'ry', 'rz'], valueScale=-1.0, valuePivot=0.0)

    # Spine/Neck/Head
    for ctrl in [spineA, spineB, spineC, spineBase, spineMid, spineTop, neck, head]:
        if cmds.objExists(ctrl):
            cmds.scaleKey(ctrl, at=['tz', 'rx', 'ry'], valueScale=-1.0, valuePivot=0.0)

    # Arms - FK (Clavicle,Arm,Hand)
    for ctrl in [clav, armFkA, armFkB, hand]:

        # Get Left/Right Nodes
        lfCtrl = ctrl.replace('SIDE', 'lf')
        rtCtrl = ctrl.replace('SIDE', 'rt')
        if cmds.objExists(lfCtrl) and cmds.objExists(rtCtrl):
            # Swap Left <> Right
            swapAnim(lfCtrl, rtCtrl)

            # Scale Keys
            cmds.scaleKey(lfCtrl, at=['tx', 'ty', 'tz'], valueScale=-1.0, valuePivot=0.0)
            cmds.scaleKey(rtCtrl, at=['tx', 'ty', 'tz'], valueScale=-1.0, valuePivot=0.0)

    # Arms - IK
    for ctrl in [armIk, armPv]:

        # Get Left/Right Nodes
        lfCtrl = ctrl.replace('SIDE', 'lf')
        rtCtrl = ctrl.replace('SIDE', 'rt')
        if cmds.objExists(lfCtrl) and cmds.objExists(rtCtrl):
            # Swap Left <> Right
            swapAnim(lfCtrl, rtCtrl)

            # Scale Keys
            cmds.scaleKey(lfCtrl, at=['tx', 'ry', 'rz'], valueScale=-1.0, valuePivot=0.0)
            cmds.scaleKey(rtCtrl, at=['tx', 'ry', 'rz'], valueScale=-1.0, valuePivot=0.0)

    # Fingers
    for ctrl in fingers:

        # Get Left/Right Nodes
        lfCtrl = ctrl.replace('SIDE', 'lf')
        rtCtrl = ctrl.replace('SIDE', 'rt')
        if cmds.objExists(lfCtrl) and cmds.objExists(rtCtrl):
            # Swap Left <> Right
            swapAnim(lfCtrl, rtCtrl)

            # Scale Keys
            cmds.scaleKey(lfCtrl, at=['tx', 'ty', 'tz'], valueScale=-1.0, valuePivot=0.0)
            cmds.scaleKey(rtCtrl, at=['tx', 'ty', 'tz'], valueScale=-1.0, valuePivot=0.0)

    # Legs - FK
    for ctrl in [legFkA, legFkB, footFkA, footFkB]:

        # Get Left/Right Nodes
        lfCtrl = ctrl.replace('SIDE', 'lf')
        rtCtrl = ctrl.replace('SIDE', 'rt')
        if cmds.objExists(lfCtrl) and cmds.objExists(rtCtrl):
            # Swap Left <> Right
            swapAnim(lfCtrl, rtCtrl)

            # Scale Keys
            cmds.scaleKey(lfCtrl, at=['tx', 'ty', 'tz'], valueScale=-1.0, valuePivot=0.0)
            cmds.scaleKey(rtCtrl, at=['tx', 'ty', 'tz'], valueScale=-1.0, valuePivot=0.0)

    # Legs - IK
    for ctrl in [legIk, legPv]:

        # Get Left/Right Nodes
        lfCtrl = ctrl.replace('SIDE', 'lf')
        rtCtrl = ctrl.replace('SIDE', 'rt')
        if cmds.objExists(lfCtrl) and cmds.objExists(rtCtrl):
            # Swap Left <> Right
            swapAnim(lfCtrl, rtCtrl)

            # Scale Keys
            cmds.scaleKey(lfCtrl, at=['tx', 'ry', 'rz'], valueScale=-1.0, valuePivot=0.0)
            cmds.scaleKey(rtCtrl, at=['tx', 'ry', 'rz'], valueScale=-1.0, valuePivot=0.0)

    # Feet - IK
    for ctrl in [footIk, toeIk]:

        # Get Left/Right Nodes
        lfCtrl = ctrl.replace('SIDE', 'lf')
        rtCtrl = ctrl.replace('SIDE', 'rt')
        if cmds.objExists(lfCtrl) and cmds.objExists(rtCtrl):
            # Swap Left <> Right
            swapAnim(lfCtrl, rtCtrl)

            # Scale Keys
            cmds.scaleKey(lfCtrl, at=['tx', 'ry', 'rz'], valueScale=-1.0, valuePivot=0.0)
            cmds.scaleKey(rtCtrl, at=['tx', 'ry', 'rz'], valueScale=-1.0, valuePivot=0.0)


def mirrorBipedAnimFromSel():
    """
    """
    # Get Current Selection
    sel = cmds.ls(sl=True, transforms=True)
    NSlist = glTools.utils.namespace.getNSList(sel, topOnly=True)

    # Mirror Animation
    for rigNS in NSlist:
        try:
            mirrorBipedAnim(rigNS)
        except Exception, e:
            print('Error mirroring animation for "' + rigNS + '"! Skipping...')


def mirrorBipedMocap(rigNS):
    """
    Mirror biped body mocap animation
    @param rigNS: Rig namespace.
    @type rigNS: str
    """
    # =============
    # - Check Rig -
    # =============

    if not cmds.namespace(ex=rigNS):
        raise Exception('Rig namespace "' + rigNS + '" not found! Unable to mirror animation...')

    # ====================
    # - Get Rig Controls -
    # ====================

    # Body
    body = rigNS + ':Hips'

    # Spine/Neck/Head
    spine = rigNS + ':Spine'
    neck = rigNS + ':Neck'
    head = rigNS + ':Head'

    # Arms
    clav = rigNS + ':SIDEShoulder'
    arm = rigNS + ':SIDEArm'
    foreArm = rigNS + ':SIDEForeArm'

    # Hand
    hand = rigNS + ':SIDEHand'
    thumb = rigNS + ':SIDEHandThumb'
    index = rigNS + ':SIDEHandIndex'
    middle = rigNS + ':SIDEHandMiddle'
    ring = rigNS + ':SIDEHandRing'
    pinky = rigNS + ':SIDEHandPinky'
    finger = [thumb, index, middle, ring, pinky]

    # Legs
    upLeg = rigNS + ':SIDEUpLeg'
    leg = rigNS + ':SIDELeg'

    # Foot
    foot = rigNS + ':SIDEFoot'
    toe = rigNS + ':SIDEToeBase'

    # Roll
    roll = 'Roll'

    # Side
    left = 'Left'
    right = 'Right'

    # ====================
    # - Mirror Animation -
    # ====================

    # Body
    for ctrl in [body]:
        if cmds.objExists(ctrl):
            cmds.scaleKey(ctrl, at=['tx', 'ry', 'rz'], valueScale=-1.0, valuePivot=0.0)

    # Spine/Neck/Head
    for item in [spine, neck, head]:
        ind = ''
        while cmds.objExists(item + str(ind)):
            ctrl = item + str(ind)
            cmds.scaleKey(ctrl, at=['rx', 'ry'], valueScale=-1.0, valuePivot=0.0)
            if not ind: ind = 0
            ind += 1

    # Shoulder
    for ctrl in [clav]:
        # Get Left/Right Nodes
        lfCtrl = ctrl.replace('SIDE', left)
        rtCtrl = ctrl.replace('SIDE', right)
        if cmds.objExists(lfCtrl) and cmds.objExists(rtCtrl):
            swapAnim(lfCtrl, rtCtrl)
            cmds.scaleKey(lfCtrl, at=['tz'], valueScale=-1.0, valuePivot=0.0)
            cmds.scaleKey(rtCtrl, at=['tz'], valueScale=-1.0, valuePivot=0.0)

    # Arms
    for ctrl in [arm, foreArm, hand]:

        # Get Left/Right Nodes
        lfCtrl = ctrl.replace('SIDE', left)
        rtCtrl = ctrl.replace('SIDE', right)
        if cmds.objExists(lfCtrl) and cmds.objExists(rtCtrl):
            swapAnim(lfCtrl, rtCtrl)
            cmds.scaleKey(lfCtrl, at=['tx', 'ty', 'tz'], valueScale=-1.0, valuePivot=0.0)
            cmds.scaleKey(rtCtrl, at=['tx', 'ty', 'tz'], valueScale=-1.0, valuePivot=0.0)

        # Get Roll Nodes
        lfCtrl = lfCtrl + roll
        rtCtrl = rtCtrl + roll
        if cmds.objExists(lfCtrl) and cmds.objExists(rtCtrl):
            swapAnim(lfCtrl, rtCtrl)
            cmds.scaleKey(lfCtrl, at=['tx', 'ty', 'tz'], valueScale=-1.0, valuePivot=0.0)
            cmds.scaleKey(rtCtrl, at=['tx', 'ty', 'tz'], valueScale=-1.0, valuePivot=0.0)

    # Fingers
    for ctrl in finger:

        # Get Left/Right Nodes
        lfCtrl = ctrl.replace('SIDE', left)
        rtCtrl = ctrl.replace('SIDE', right)

        ind = 1
        while cmds.objExists(lfCtrl + str(ind)) and cmds.objExists(rtCtrl + str(ind)):
            lfCtrlInd = lfCtrl + str(ind)
            rtCtrlInd = rtCtrl + str(ind)
            swapAnim(lfCtrlInd, rtCtrlInd)
            cmds.scaleKey(lfCtrlInd, at=['tx', 'ty', 'tz'], valueScale=-1.0, valuePivot=0.0)
            cmds.scaleKey(rtCtrlInd, at=['tx', 'ty', 'tz'], valueScale=-1.0, valuePivot=0.0)
            if not ind: ind = 0
            ind += 1

    # Legs
    for ctrl in [upLeg, leg, foot, toe]:

        # Get Left/Right Nodes
        lfCtrl = ctrl.replace('SIDE', left)
        rtCtrl = ctrl.replace('SIDE', right)
        if cmds.objExists(lfCtrl) and cmds.objExists(rtCtrl):
            swapAnim(lfCtrl, rtCtrl)
            cmds.scaleKey(lfCtrl, at=['tx', 'ty', 'tz'], valueScale=-1.0, valuePivot=0.0)
            cmds.scaleKey(rtCtrl, at=['tx', 'ty', 'tz'], valueScale=-1.0, valuePivot=0.0)

        # Get Roll Nodes
        lfCtrl = lfCtrl + roll
        rtCtrl = rtCtrl + roll
        if cmds.objExists(lfCtrl) and cmds.objExists(rtCtrl):
            swapAnim(lfCtrl, rtCtrl)
            cmds.scaleKey(lfCtrl, at=['tx', 'ty', 'tz'], valueScale=-1.0, valuePivot=0.0)
            cmds.scaleKey(rtCtrl, at=['tx', 'ty', 'tz'], valueScale=-1.0, valuePivot=0.0)


def mirrorBipedMocaFromSel():
    """
    """
    # Get Current Selection
    sel = cmds.ls(sl=True, transforms=True)
    NSlist = glTools.utils.namespace.getNSList(sel, topOnly=True)

    # Mirror Animation
    for rigNS in NSlist:
        try:
            mirrorBipedMocap(rigNS)
        except Exception, e:
            print('Error mirroring mocap animation for "' + rigNS + '"! Skipping...')
