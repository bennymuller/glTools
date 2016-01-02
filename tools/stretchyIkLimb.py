import maya.cmds as cmds
import glTools.utils.ik
import glTools.utils.joint


def build(ikHandle,
          ikCtrl,
          pvCtrl,
          scaleAxis='x',
          scaleAttr='',
          prefix=''):
    """
    Create a stretchy IK limb
    @param ikHandle: IK Handle to create stretchy limb setup for
    @type ikHandle: str
    @param ikCtrl: IK Handle or limb end (wrist/ankle) control
    @type ikCtrl: str
    @param pvCtrl: Pole vector or limb mid (elbow/knee) control
    @type pvCtrl: str
    @param scaleAxis: Axis along which the ik joints will be scaled
    @type scaleAxis: str
    @param scaleAttr: World scale attribute
    @type scaleAttr: str
    @param prefix: Name prefix for all builder created nodes. If left as deafult ('') prefix will be derived from ikHandle name.
    @type prefix: str
    """

    upperScaleAttr = 'upperLimbScale'
    lowerScaleAttr = 'lowerLimbScale'
    blendAttr = 'stretchToControl'
    biasAttr = 'stretchBias'

    # ==============
    # - Get Joints -
    # ==============

    ikJoints = glTools.utils.ik.getAffectedJoints(ikHandle)

    # ========================
    # - Add Joint Attributes -
    # ========================

    for ikJoint in ikJoints[:-1]:
        jntLen = glTools.utils.joint.length(ikJoint)
        cmds.addAttr(ikJoint, ln='restLength', dv=jntLen)

    # =============================
    # - Add IK Control Attributes -
    # =============================

    # IK Control
    cmds.addAttr(ikCtrl, ln=upperScaleAttr, min=0.01, dv=1.0, k=True)
    cmds.addAttr(ikCtrl, ln=lowerScaleAttr, min=0.01, dv=1.0, k=True)
    cmds.addAttr(ikCtrl, ln=blendAttr, min=0.0, max=1.0, dv=0.0, k=True)
    cmds.addAttr(ikCtrl, ln=biasAttr, min=0.0, max=1.0, dv=0.5, k=True)

    # PV Control
    cmds.addAttr(pvCtrl, ln=blendAttr, min=0.0, max=1.0, dv=0.0, k=True)

    # ===============================
    # - Create Limb Stretch Network -
    # ===============================

    # Limb Length - Character Scale
    limbCharScale = cmds.createNode('multiplyDivide', n=prefix + '_characterScale_multiplyDivide')
    cmds.setAttr(limbCharScale + '.operation', 2)  # Divide
    cmds.connectAttr(scaleAttr, limbCharScale + '.input2X', f=True)
    cmds.connectAttr(scaleAttr, limbCharScale + '.input2Y', f=True)
    cmds.connectAttr(scaleAttr, limbCharScale + '.input2Z', f=True)

    # Rest Length
    limbRestLenNode = cmds.createNode('plusMinusAverage', n=prefix + '_limbRestLength_plusMinusAverage')
    for i in range(len(ikJoints[:-1])):
        cmds.connectAttr(ikJoints[i] + '.restLength', limbRestLenNode + '.input1D[' + str(i) + ']', f=True)

    # Limb Length
    limbDistNode = cmds.createNode('distanceBetween', n=prefix + '_limbLength_distanceBetween')
    cmds.connectAttr(ikJoints[0] + '.parentMatrix[0]', limbDistNode + '.inMatrix1', f=True)
    cmds.connectAttr(ikCtrl + '.worldMatrix[0]', limbDistNode + '.inMatrix2', f=True)
    cmds.connectAttr(limbDistNode + '.distance', limbCharScale + '.input1X', f=True)

    # Limb Length Diff
    limbDiffNode = cmds.createNode('plusMinusAverage', n=prefix + '_limbLengthDiff_plusMinusAverage')
    cmds.setAttr(limbDiffNode + '.operation', 2)  # Subtract
    cmds.connectAttr(limbCharScale + '.outputX', limbDiffNode + '.input1D[0]', f=True)
    cmds.connectAttr(limbRestLenNode + '.output1D', limbDiffNode + '.input1D[1]', f=True)

    # Bias Reverse
    limbBiasRev = cmds.createNode('reverse', n=prefix + '_limbBias_reverse')
    cmds.connectAttr(ikCtrl + '.' + biasAttr, limbBiasRev + '.inputX', f=True)

    # Upper Stretch Diff
    upperStretchDiff = cmds.createNode('multDoubleLinear', n=prefix + '_upperStretchDiff_multDoubleLinear')
    cmds.connectAttr(limbDiffNode + '.output1D', upperStretchDiff + '.input1', f=True)
    cmds.connectAttr(ikCtrl + '.' + biasAttr, upperStretchDiff + '.input2', f=True)

    # Lower Stretch Diff
    lowerStretchDiff = cmds.createNode('multDoubleLinear', n=prefix + '_lowerStretchDiff_multDoubleLinear')
    cmds.connectAttr(limbDiffNode + '.output1D', lowerStretchDiff + '.input1', f=True)
    cmds.connectAttr(limbBiasRev + '.outputX', lowerStretchDiff + '.input2', f=True)

    # Upper Stretch Length
    upperStretchLen = cmds.createNode('addDoubleLinear', n=prefix + '_upperStretchTarget_addDoubleLinear')
    cmds.connectAttr(ikJoints[0] + '.restLength', upperStretchLen + '.input1', f=True)
    cmds.connectAttr(upperStretchDiff + '.output', upperStretchLen + '.input2', f=True)

    # Lower Stretch Length
    lowerStretchLen = cmds.createNode('addDoubleLinear', n=prefix + '_lowerStretchTarget_addDoubleLinear')
    cmds.connectAttr(ikJoints[1] + '.restLength', lowerStretchLen + '.input1', f=True)
    cmds.connectAttr(lowerStretchDiff + '.output', lowerStretchLen + '.input2', f=True)

    # Upper Stretch Scale
    upperStretchScale = cmds.createNode('multiplyDivide', n=prefix + '_upperStretchScale_multiplyDivide')
    cmds.setAttr(upperStretchScale + '.operation', 2)  # Divide
    cmds.connectAttr(upperStretchLen + '.output', upperStretchScale + '.input1X', f=True)
    cmds.connectAttr(ikJoints[0] + '.restLength', upperStretchScale + '.input2X', f=True)

    # Lower Stretch Scale
    lowerStretchScale = cmds.createNode('multiplyDivide', n=prefix + '_lowerStretchScale_multiplyDivide')
    cmds.setAttr(lowerStretchScale + '.operation', 2)  # Divide
    cmds.connectAttr(lowerStretchLen + '.output', lowerStretchScale + '.input1X', f=True)
    cmds.connectAttr(ikJoints[1] + '.restLength', lowerStretchScale + '.input2X', f=True)

    # =====================================
    # - Create Stretch To Control Network -
    # =====================================

    # Shoulder to PV distance
    upperPvDist = cmds.createNode('distanceBetween', n=prefix + '_upperPV_distanceBetween')
    cmds.connectAttr(ikJoints[0] + '.parentMatrix[0]', upperPvDist + '.inMatrix1', f=True)
    cmds.connectAttr(pvCtrl + '.worldMatrix[0]', upperPvDist + '.inMatrix2', f=True)
    cmds.connectAttr(upperPvDist + '.distance', limbCharScale + '.input1Y', f=True)

    # Wrist to PV distance
    lowerPvDist = cmds.createNode('distanceBetween', n=prefix + '_lowerPV_distanceBetween')
    cmds.connectAttr(ikCtrl + '.worldMatrix[0]', lowerPvDist + '.inMatrix1', f=True)
    cmds.connectAttr(pvCtrl + '.worldMatrix[0]', lowerPvDist + '.inMatrix2', f=True)
    cmds.connectAttr(lowerPvDist + '.distance', limbCharScale + '.input1Z', f=True)

    # Upper to PV scale
    upperPvScale = cmds.createNode('multiplyDivide', n=prefix + '_upperPV_multiplyDivide')
    cmds.setAttr(upperPvScale + '.operation', 2)  # Divide
    cmds.connectAttr(limbCharScale + '.outputY', upperPvScale + '.input1X', f=True)
    cmds.connectAttr(ikJoints[0] + '.restLength', upperPvScale + '.input2X', f=True)

    # Lower to PV scale
    lowerPvScale = cmds.createNode('multiplyDivide', n=prefix + '_lowerPV_multiplyDivide')
    cmds.setAttr(lowerPvScale + '.operation', 2)  # Divide
    cmds.connectAttr(limbCharScale + '.outputZ', lowerPvScale + '.input1X', f=True)
    cmds.connectAttr(ikJoints[1] + '.restLength', lowerPvScale + '.input2X', f=True)

    # ============================
    # - Create Condition Network -
    # ============================

    # Limb Stretch - Condition
    limbStretchCondition = cmds.createNode('condition', n=prefix + '_limbStretch_condition')
    cmds.setAttr(limbStretchCondition + '.operation', 2)  # Greater Than
    # !!!!!!!!!!!!! ".secondTerm" had been set to 1.0 for some reason? Should be 0 to register any difference
    cmds.setAttr(limbStretchCondition + '.secondTerm', 0.0)
    cmds.connectAttr(limbDiffNode + '.output1D', limbStretchCondition + '.firstTerm', f=True)
    cmds.setAttr(limbStretchCondition + '.colorIfFalse', 1.0, 1.0, 1.0)
    cmds.connectAttr(upperStretchScale + '.outputX', limbStretchCondition + '.colorIfTrueR', f=True)
    cmds.connectAttr(lowerStretchScale + '.outputX', limbStretchCondition + '.colorIfTrueG', f=True)

    # Limb Stretch - Upper Blend
    upperLimbStretchBlend = cmds.createNode('blendTwoAttr', n=prefix + '_upperLimbSTretch_blendTwoAttr')
    cmds.connectAttr(ikCtrl + '.' + blendAttr, upperLimbStretchBlend + '.attributesBlender', f=True)
    cmds.setAttr(upperLimbStretchBlend + '.input[0]', 1.0)
    cmds.connectAttr(limbStretchCondition + '.outColorR', upperLimbStretchBlend + '.input[1]', f=True)

    # Limb Stretch - Lower Blend
    lowerLimbStretchBlend = cmds.createNode('blendTwoAttr', n=prefix + '_lowerLimbSTretch_blendTwoAttr')
    cmds.connectAttr(ikCtrl + '.' + blendAttr, lowerLimbStretchBlend + '.attributesBlender', f=True)
    cmds.setAttr(lowerLimbStretchBlend + '.input[0]', 1.0)
    cmds.connectAttr(limbStretchCondition + '.outColorG', lowerLimbStretchBlend + '.input[1]', f=True)

    # Limb Stretch - Upper Scale
    upperLimbStretchScale = cmds.createNode('multDoubleLinear', n=prefix + '_upperStretchScale_multDoubleLinear')
    cmds.connectAttr(upperLimbStretchBlend + '.output', upperLimbStretchScale + '.input1', f=True)
    cmds.connectAttr(ikCtrl + '.upperLimbScale', upperLimbStretchScale + '.input2', f=True)

    # Limb Stretch - Lower Scale
    lowerLimbStretchScale = cmds.createNode('multDoubleLinear', n=prefix + '_lowerStretchScale_multDoubleLinear')
    cmds.connectAttr(lowerLimbStretchBlend + '.output', lowerLimbStretchScale + '.input1', f=True)
    cmds.connectAttr(ikCtrl + '.lowerLimbScale', lowerLimbStretchScale + '.input2', f=True)

    # Stretch To Control - Upper Blend
    upStretchToCtrlBlend = cmds.createNode('blendTwoAttr', n=prefix + '_upperStretchToControl_blendTwoAttr')
    cmds.connectAttr(pvCtrl + '.' + blendAttr, upStretchToCtrlBlend + '.attributesBlender', f=True)
    cmds.connectAttr(upperLimbStretchScale + '.output', upStretchToCtrlBlend + '.input[0]', f=True)
    cmds.connectAttr(upperPvScale + '.outputX', upStretchToCtrlBlend + '.input[1]', f=True)

    # Stretch To Control - Lower Mult
    stretchToCtrlAllMult = cmds.createNode('multDoubleLinear', n=prefix + '_stretchCombineWt_multDoubleLinear')
    cmds.connectAttr(ikCtrl + '.' + blendAttr, stretchToCtrlAllMult + '.input1', f=True)
    cmds.connectAttr(pvCtrl + '.' + blendAttr, stretchToCtrlAllMult + '.input2', f=True)

    # Stretch To Control - Lower Blend
    loStretchToCtrlBlend = cmds.createNode('blendTwoAttr', n=prefix + '_lowerStretchToControl_blendTwoAttr')
    cmds.connectAttr(stretchToCtrlAllMult + '.output', loStretchToCtrlBlend + '.attributesBlender', f=True)
    cmds.connectAttr(lowerLimbStretchScale + '.output', loStretchToCtrlBlend + '.input[0]', f=True)
    cmds.connectAttr(lowerPvScale + '.outputX', loStretchToCtrlBlend + '.input[1]', f=True)

    # =======================
    # - End Effector Offset -
    # =======================

    # Get End Effector
    endEffector = cmds.listConnections(ikHandle + '.endEffector', s=True, d=False)[0]
    endEffectorCon = cmds.listConnections(endEffector + '.tx', s=True, d=False)[0]

    # Disconnect End Effector
    cmds.disconnectAttr(endEffectorCon + '.tx', endEffector + '.tx')
    cmds.disconnectAttr(endEffectorCon + '.ty', endEffector + '.ty')
    cmds.disconnectAttr(endEffectorCon + '.tz', endEffector + '.tz')

    # End Effector Offset
    endOffsetReverse = cmds.createNode('reverse', n=prefix + '_limbEndOffset_reverse')
    cmds.connectAttr(ikCtrl + '.' + blendAttr, endOffsetReverse + '.inputX', f=True)
    endOffsetMultiply = cmds.createNode('multDoubleLinear', n=prefix + 'limbEndOffset_multDoubleLinear')
    cmds.connectAttr(pvCtrl + '.' + blendAttr, endOffsetMultiply + '.input1', f=True)
    cmds.connectAttr(endOffsetReverse + '.outputX', endOffsetMultiply + '.input2', f=True)

    # End Effector Offset Length
    endEffectorScale = cmds.createNode('multDoubleLinear', n=prefix + '_limbEndScale_multDoubleLinear')
    cmds.connectAttr(ikJoints[1] + '.restLength', endEffectorScale + '.input1', f=True)
    cmds.connectAttr(lowerPvScale + '.outputX', endEffectorScale + '.input2', f=True)

    # End Effector Offset Scale
    endEffectorScaleMD = cmds.createNode('multiplyDivide', n=prefix + '_limbEndScale_multiplyDivide')
    cmds.setAttr(endEffectorScaleMD + '.operation', 2)  # Divide
    cmds.connectAttr(endEffectorScale + '.output', endEffectorScaleMD + '.input1X', f=True)
    cmds.connectAttr(loStretchToCtrlBlend + '.output', endEffectorScaleMD + '.input2X', f=True)

    # End Effector Offset Blend
    endEffectorBlend = cmds.createNode('blendTwoAttr', n=prefix + '_limbEndOffset_blendTwoAttr')
    cmds.connectAttr(endOffsetMultiply + '.output', endEffectorBlend + '.attributesBlender', f=True)
    cmds.connectAttr(ikJoints[1] + '.restLength', endEffectorBlend + '.input[0]', f=True)
    # cmds.connectAttr(endEffectorScale+'.output',endEffectorBlend+'.input[1]',f=True)
    cmds.connectAttr(endEffectorScaleMD + '.outputX', endEffectorBlend + '.input[1]', f=True)

    # =====================
    # - Connect To Joints -
    # =====================

    cmds.connectAttr(upStretchToCtrlBlend + '.output', ikJoints[0] + '.s' + scaleAxis, f=True)
    cmds.connectAttr(loStretchToCtrlBlend + '.output', ikJoints[1] + '.s' + scaleAxis, f=True)

    # ===========================
    # - Connect To End Effector -
    # ===========================

    # Check Negative Translate Values
    endEffectorNegate = ''
    if cmds.getAttr(endEffectorCon + '.t' + scaleAxis) < 0.0:

        # Negate Result
        endEffectorNegate = cmds.createNode('unitConversion', n=prefix + '_endEffectorNegate_unitConversio')
        cmds.connectAttr(endEffectorBlend + '.output', endEffectorNegate + '.input', f=True)
        cmds.setAttr(endEffectorNegate + '.conversionFactor', -1)
        cmds.connectAttr(endEffectorNegate + '.output', endEffector + '.t' + scaleAxis, f=True)

    else:

        # Direct Connection
        cmds.connectAttr(endEffectorBlend + '.output', endEffector + '.t' + scaleAxis, f=True)

    # =================
    # - Return Result -
    # =================

    result = {}

    result['ikHandle'] = ikHandle
    result['endEffector'] = endEffector
    result['ikCtrl'] = ikCtrl
    result['pvCtrl'] = pvCtrl
    result['joints'] = ikJoints
    result['charScaleNode'] = limbCharScale
    result['restLengthNode'] = limbRestLenNode
    result['limbDistNode'] = limbDistNode
    result['limbDiffNode'] = limbDiffNode
    result['limbBiasReverse'] = limbBiasRev
    result['upperStretchDiff'] = upperStretchDiff
    result['lowerStretchDiff'] = lowerStretchDiff
    result['upperStretchLen'] = upperStretchLen
    result['lowerStretchLen'] = lowerStretchLen
    result['upperStretchScale'] = upperStretchScale
    result['lowerStretchScale'] = lowerStretchScale
    result['upperPoleVectorDist'] = upperPvDist
    result['lowerPoleVectorDist'] = lowerPvDist
    result['upperPoleVectorScale'] = upperPvScale
    result['lowerPoleVectorScale'] = lowerPvScale
    result['limbStretchCondition'] = limbStretchCondition
    result['upperLimbStretchBlend'] = upperLimbStretchBlend
    result['lowerLimbStretchBlend'] = lowerLimbStretchBlend
    result['upperLimbStretchScale'] = upperLimbStretchScale
    result['lowerLimbStretchScale'] = lowerLimbStretchScale
    result['upperStretchToCtrlBlend'] = upStretchToCtrlBlend
    result['lowerStretchToCtrlBlend'] = loStretchToCtrlBlend
    result['stretchToCtrlMult'] = stretchToCtrlAllMult
    result['endOffsetReverse'] = endOffsetReverse
    result['endEffectorScale'] = endEffectorScale
    result['endEffectorScaleMult'] = endEffectorScaleMD
    result['endEffectorBlend'] = endEffectorBlend
    result['endEffectorNegate'] = endEffectorNegate

    return result
