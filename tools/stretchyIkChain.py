import maya.cmds as cmds
import maya.mel as mel
import glTools.utils.ik
import glTools.utils.stringUtils


def build(ikHandle, scaleAxis='x', scaleAttr='', blendControl='', blendAttr='stretchScale', shrink=False, prefix=''):
    """
    Create a stretchy IK chain
    @param ikHandle: IK Handle to create stretchy setup for
    @type ikHandle: str
    @param scaleAttr: World scale attribute
    @type scaleAttr: str
    @param scaleAxis: Axis along which the ik joints will be scaled
    @type scaleAxis: str
    @param blendControl: Control object that will contain the attribute to control the stretchy IK blending. If left at default (""), blending will not be enabled.
    @type blendControl: str
    @param blendAttr: The name of the attribute on blendControl that will control the stretchy IK blending.
    @type blendAttr: str
    @param shrink: Enable joint shrinking.
    @type shrink: bool
    @param prefix: Name prefix for all builder created nodes. If left as deafult ('') prefix will be derived from ikHandle name.
    @type prefix: str
    """
    # ==========
    # - Checks -
    # ==========

    # IkHandle
    if not cmds.objExists(ikHandle): raise Exception('IK handle ' + ikHandle + ' does not exist!')

    # Blend
    blend = cmds.objExists(blendControl)
    if blend and not cmds.objExists(blendControl + '.' + blendAttr):
        cmds.addAttr(blendControl, ln=blendAttr, at='double', min=0, max=1, dv=1)
        cmds.setAttr(blendControl + '.' + blendAttr, e=True, k=True)
    blendAttr = blendControl + '.' + blendAttr

    # Prefix
    if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(ikHandle)

    # =====================
    # - Get IkHandle Info -
    # =====================

    # Get IK chain information
    ikJoints = glTools.utils.ik.getAffectedJoints(ikHandle)
    ikPos = cmds.getAttr(ikHandle + '.t')[0]

    # Calculate actual joint lengths
    lengthNode = cmds.createNode('plusMinusAverage', n=prefix + 'length_plusMinusAverage')
    for j in range(len(ikJoints) - 1):
        cmds.connectAttr(ikJoints[j + 1] + '.t' + scaleAxis, lengthNode + '.input1D[' + str(j) + ']')

    # Calculate Distance
    distNode = cmds.createNode('distanceBetween', n=prefix + '_distanceBetween')
    cmds.connectAttr(ikJoints[0] + '.parentMatrix[0]', distNode + '.inMatrix1', f=True)
    cmds.connectAttr(ikHandle + '.parentMatrix[0]', distNode + '.inMatrix2', f=True)

    # -------------!!!!!!!!!!
    # Currently setting the translate attributes instead of connecting.
    # Direct connection was causing cycle check warnings
    root_pos = cmds.getAttr(ikJoints[0] + '.t')[0]
    cmds.setAttr(distNode + '.point1', root_pos[0], root_pos[1], root_pos[2])
    cmds.setAttr(distNode + '.point2', ikPos[0], ikPos[1], ikPos[2])
    # cmds.connectAttr(ik_joint[0]+'.t',distNode+'.point1',f=True)
    # cmds.connectAttr(ikHandle+'.t',distNode+'.point2',f=True)
    # -------------

    # ===========
    # - Stretch -
    # ===========

    # Calculate Stretch Scale Factor
    stretchNode = cmds.createNode('multiplyDivide', n=prefix + '_stretch_multiplyDivide')
    cmds.setAttr(stretchNode + '.operation', 2)  # Divide
    cmds.connectAttr(distNode + '.distance', stretchNode + '.input1X', f=True)

    # Add Scale Compensation
    scaleNode = ''
    if cmds.objExists(scaleAttr):
        scaleNode = cmds.createNode('multDoubleLinear', n=prefix + '_scale_multDoubleLinear')
        cmds.connectAttr(lengthNode + '.output1D', scaleNode + '.input1', f=True)
        cmds.connectAttr(scaleAttr, scaleNode + '.input2', f=True)
        cmds.connectAttr(scaleNode + '.output', stretchNode + '.input2X', f=True)
    else:
        cmds.connectAttr(lengthNode + '.output1D', stretchNode + '.input2X', f=True)

    # Condition
    condNode = ''
    if not shrink:
        condNode = cmds.createNode('condition', n=prefix + '_shrink_condition')
        # Set condition operation
        cmds.setAttr(condNode + '.operation', 2)  # Greater than
        # Set second term as current length
        cmds.connectAttr(distNode + '.distance', condNode + '.firstTerm', f=True)
        # Set first term as original length
        if scaleNode:
            cmds.connectAttr(scaleNode + '.output', condNode + '.secondTerm', f=True)
        else:
            cmds.connectAttr(lengthNode + '.output1D', condNode + '.secondTerm', f=True)
        # Set condition results
        cmds.connectAttr(stretchNode + '.outputX', condNode + '.colorIfTrueR', f=True)
        cmds.setAttr(condNode + '.colorIfFalseR', 1)

    # =========
    # - Blend -
    # =========

    blendNode = ''
    if blend:
        blendNode = cmds.createNode('blendTwoAttr', n=prefix + '_blend_blendTwoAttr')
        cmds.connectAttr(blendAttr, blendNode + '.attributesBlender', f=True)
        # Connect Blend
        cmds.setAttr(blendNode + '.input[0]', 1.0)
        if shrink:
            cmds.connectAttr(stretchNode + '.outputX', blendNode + '.input[1]', f=True)
        else:
            cmds.connectAttr(condNode + '.outColorR', blendNode + '.input[1]', f=True)

    # =====================
    # - Connect To Joints -
    # =====================

    # Attach output to joint scale
    for i in range(len(ikJoints) - 1):
        if blend:
            cmds.connectAttr(blendNode + '.output', ikJoints[i] + '.s' + scaleAxis, f=True)
        else:
            if shrink:
                cmds.connectAttr(stretchNode + '.outputX', ikJoints[i] + '.s' + scaleAxis, f=True)
            else:
                cmds.connectAttr(condNode + '.outColorR', ikJoints[i] + '.s' + scaleAxis, f=True)

    # Set ikHandle position. Make sure IK handle evaluates correctly!
    cmds.setAttr(ikHandle + '.t', ikPos[0], ikPos[1], ikPos[2])

    # =================
    # - Return Result -
    # =================

    result = [lengthNode, distNode, stretchNode, scaleNode, condNode, blendNode]
    return result
