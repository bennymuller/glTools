import maya.cmds as cmds
import glTools.utils.stringUtils
import glTools.utils.surface


def loadPlugin():
    """
    Load glCurveUtils plugin.
    """
    # Check if plugin is loaded
    if not cmds.pluginInfo('glCurveUtils', q=True, l=True):

        # Load Plugin
        try:
            cmds.loadPlugin('glCurveUtils')
        except:
            raise Exception('Unable to load glCurveUtils plugin!')

    # Return Result
    return 1


def create(surface, spansU=0, spansV=0, prefix=None):
    """
    """
    # Load Plugins
    loadPlugin()

    # ==========
    # - Checks -
    # ==========

    # Check Surface
    if not glTools.utils.surface.isSurface(surface):
        raise Exception('Object "' + surface + '" is not a valid nurbs surface!')

    # Check Prefix
    if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(surface)

    # Get Surface Details
    if not spansU: spansU = cmds.getAttr(surface + '.spansU')
    if not spansV: spansV = cmds.getAttr(surface + '.spansV')
    minU = cmds.getAttr(surface + '.minValueU')
    maxU = cmds.getAttr(surface + '.maxValueU')
    minV = cmds.getAttr(surface + '.minValueV')
    maxV = cmds.getAttr(surface + '.maxValueV')
    incU = (maxU - minU) / spansU
    incV = (maxV - minV) / spansV

    # =============
    # - Rebuild U -
    # =============

    crvU = []
    for i in range(spansU + 1):
        # Duplicate Surface Curve
        dupCurve = cmds.duplicateCurve(surface + '.u[' + str(incU * i) + ']', ch=True, rn=False, local=False)
        dupCurveNode = cmds.rename(dupCurve[1], prefix + '_spanU' + str(i) + '_duplicateCurve')
        dupCurve = cmds.rename(dupCurve[0], prefix + '_spanU' + str(i) + '_crv')
        crvU.append(dupCurve)

        # Set Curve Length
        arcLen = cmds.arclen(dupCurve)
        setLen = cmds.createNode('setCurveLength', n=prefix + '_spanU' + str(i) + '_setCurveLength')
        crvInfo = cmds.createNode('curveInfo', n=prefix + '_spanU' + str(i) + '_curveInfo')
        blendLen = cmds.createNode('blendTwoAttr', n=prefix + '_spanU' + str(i) + 'length_blendTwoAttr')
        cmds.addAttr(dupCurve, ln='targetLength', dv=arcLen, k=True)
        cmds.connectAttr(dupCurveNode + '.outputCurve', crvInfo + '.inputCurve', f=True)
        cmds.connectAttr(dupCurveNode + '.outputCurve', setLen + '.inputCurve', f=True)
        cmds.connectAttr(crvInfo + '.arcLength', blendLen + '.input[0]', f=True)
        cmds.connectAttr(dupCurve + '.targetLength', blendLen + '.input[1]', f=True)
        cmds.connectAttr(blendLen + '.output', setLen + '.length', f=True)
        cmds.connectAttr(setLen + '.outputCurve', dupCurve + '.create', f=True)

        # Add Control Attributes
        cmds.addAttr(dupCurve, ln='lockLength', min=0, max=1, dv=1, k=True)
        cmds.addAttr(dupCurve, ln='lengthBias', min=0, max=1, dv=0, k=True)
        cmds.connectAttr(dupCurve + '.lockLength', blendLen + '.attributesBlender', f=True)
        cmds.connectAttr(dupCurve + '.lengthBias', setLen + '.bias', f=True)

    # Loft New Surface
    srfU = cmds.loft(crvU, ch=True, uniform=True, close=False, autoReverse=False, degree=3)
    srfUloft = cmds.rename(srfU[1], prefix + '_rebuildU_loft')
    srfU = cmds.rename(srfU[0], prefix + '_rebuildU_srf')

    # Rebuild 0-1
    rebuildSrf = cmds.rebuildSurface(srfU, ch=True, rpo=True, rt=0, end=1, kr=0, kcp=1, su=0, du=3, sv=0, dv=3, tol=0)
    rebuildSrfNode = cmds.rename(rebuildSrf[1], prefix + '_rebuildU_rebuildSurface')

    # Add Control Attributes
    cmds.addAttr(srfU, ln='lockLength', min=0, max=1, dv=1, k=True)
    cmds.addAttr(srfU, ln='lengthBias', min=0, max=1, dv=0, k=True)
    for crv in crvU:
        cmds.connectAttr(srfU + '.lockLength', crv + '.lockLength', f=True)
        cmds.connectAttr(srfU + '.lengthBias', crv + '.lengthBias', f=True)

    # =============
    # - Rebuild V -
    # =============

    crvV = []
    for i in range(spansV + 1):
        # Duplicate Surface Curve
        dupCurve = cmds.duplicateCurve(srfU + '.v[' + str(incV * i) + ']', ch=True, rn=False, local=False)
        dupCurveNode = cmds.rename(dupCurve[1], prefix + '_spanV' + str(i) + '_duplicateCurve')
        dupCurve = cmds.rename(dupCurve[0], prefix + '_spanV' + str(i) + '_crv')
        crvV.append(dupCurve)

        # Set Curve Length
        arcLen = cmds.arclen(dupCurve)
        setLen = cmds.createNode('setCurveLength', n=prefix + '_spanV' + str(i) + '_setCurveLength')
        crvInfo = cmds.createNode('curveInfo', n=prefix + '_spanV' + str(i) + '_curveInfo')
        blendLen = cmds.createNode('blendTwoAttr', n=prefix + '_spanV' + str(i) + 'length_blendTwoAttr')
        cmds.addAttr(dupCurve, ln='targetLength', dv=arcLen, k=True)
        cmds.connectAttr(dupCurveNode + '.outputCurve', crvInfo + '.inputCurve', f=True)
        cmds.connectAttr(dupCurveNode + '.outputCurve', setLen + '.inputCurve', f=True)
        cmds.connectAttr(crvInfo + '.arcLength', blendLen + '.input[0]', f=True)
        cmds.connectAttr(dupCurve + '.targetLength', blendLen + '.input[1]', f=True)
        cmds.connectAttr(blendLen + '.output', setLen + '.length', f=True)
        cmds.connectAttr(setLen + '.outputCurve', dupCurve + '.create', f=True)

        # Add Control Attribute
        cmds.addAttr(dupCurve, ln='lockLength', min=0, max=1, dv=1, k=True)
        cmds.addAttr(dupCurve, ln='lengthBias', min=0, max=1, dv=0, k=True)
        cmds.connectAttr(dupCurve + '.lockLength', blendLen + '.attributesBlender', f=True)
        cmds.connectAttr(dupCurve + '.lengthBias', setLen + '.bias', f=True)

    # Loft New Surface
    srfV = cmds.loft(crvV, ch=True, uniform=True, close=False, autoReverse=False, degree=3)
    srfVloft = cmds.rename(srfV[1], prefix + '_rebuildV_loft')
    srfV = cmds.rename(srfV[0], prefix + '_rebuildV_srf')

    # Rebuild 0-1
    rebuildSrf = cmds.rebuildSurface(srfV, ch=True, rpo=True, rt=0, end=1, kr=0, kcp=1, su=0, du=3, sv=0, dv=3, tol=0)
    rebuildSrfNode = cmds.rename(rebuildSrf[1], prefix + '_rebuildV_rebuildSurface')

    # Add Control Attribute
    cmds.addAttr(srfV, ln='lockLength', min=0, max=1, dv=1, k=True)
    cmds.addAttr(srfV, ln='lengthBias', min=0, max=1, dv=0, k=True)
    for crv in crvV:
        cmds.connectAttr(srfV + '.lockLength', crv + '.lockLength', f=True)
        cmds.connectAttr(srfV + '.lengthBias', crv + '.lengthBias', f=True)

    # ===================
    # - Build Hierarchy -
    # ===================

    rebuildUGrp = cmds.group(em=True, n=prefix + '_rebuildU_grp')
    cmds.parent(crvU, rebuildUGrp)
    cmds.parent(srfU, rebuildUGrp)

    rebuildVGrp = cmds.group(em=True, n=prefix + '_rebuildV_grp')
    cmds.parent(crvV, rebuildVGrp)
    cmds.parent(srfV, rebuildVGrp)

    rebuildGrp = cmds.group(em=True, n=prefix + '_lockLength_grp')
    cmds.parent(rebuildUGrp, rebuildGrp)
    cmds.parent(rebuildVGrp, rebuildGrp)

    # =================
    # - Return Result -
    # =================

    return rebuildGrp
