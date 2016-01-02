import maya.cmds as cmds
import glTools.tools.controlBuilder
import glTools.utils.attach
import glTools.utils.base
import glTools.utils.attribute
import glTools.utils.component
import glTools.utils.stringUtils


def buildProfile(radius=1, spans=8):
    """
    Create tube profile curve (circle)
    @param radius: Profile radius
    @type radius: float
    @param spans: Number of profile curve spans
    @type spans: int
    """
    crv = cmds.circle(c=[0, 0, 0], nr=[0, 0, 1], sw=360, r=radius, s=spans, d=3, ch=False)
    return crv


def buildOffsetCurve(crv):
    """
    """
    prefix = glTools.utils.stringUtils.stripSuffix(crv)
    offsetCrvShape = cmds.createNode('nurbsCurve', n=prefix + '_offsetCrvShape')
    offsetCrv = cmds.listRelatives(offsetCrvShape, p=True, pa=True)[0]
    cmds.connectAttr(crv + '.worldSpace[0]', offsetCrvShape + '.create', f=True)
    return offsetCrv


def buildSubCurveDetach(crv):
    """
    """
    # Get Prefix
    prefix = glTools.utils.stringUtils.stripSuffix(crv)

    # Prep Curve
    cmds.rebuildCurve(crv, ch=False, rpo=True, rt=0, end=1, kr=0, kcp=1, kep=1, kt=0, s=0, d=3)
    cmds.delete(crv, ch=True)

    # Detach Curve
    detach = cmds.detachCurve(crv, p=(0.001, 0.999), k=(0, 1, 0), rpo=False)
    detachCrv = detach[1]
    detachNode = detach[-1]
    cmds.delete(detach[0], detach[2])

    # Connect Detach Min/Max
    cmds.addAttr(subCrv, ln='min', min=0, max=0.999, dv=0, k=True)
    cmds.addAttr(subCrv, ln='max', min=0.001, max=1, dv=1, k=True)
    cmds.addAttr(subCrv, ln='offset', min=-1, max=1, dv=1, k=True)
    minAdd = cmds.createNode('addDoubleLinear', n=prefix + '_minAdd_addDoubleLinear')
    maxAdd = cmds.createNode('addDoubleLinear', n=prefix + '_maxAdd_addDoubleLinear')
    minMaxClamp = cmds.createNode('clamp', n=prefix + '_minMax_clamp')
    cmds.connectAttr(subCrv + '.min', minAdd + '.input1', f=True)
    cmds.connectAttr(subCrv + '.offset', minAdd + '.input2', f=True)
    cmds.connectAttr(subCrv + '.max', maxAdd + '.input1', f=True)
    cmds.connectAttr(subCrv + '.offset', maxAdd + '.input2', f=True)
    cmds.connectAttr(minAdd + '.output', minMaxClamp + '.inputR', f=True)
    cmds.connectAttr(maxAdd + '.output', minMaxClamp + '.inputB', f=True)
    cmds.setAttr(minMaxClamp + '.min', 0, 0, 0.0001)
    cmds.setAttr(minMaxClamp + '.max', 0.9999, 0, 0)
    cmds.connectAttr(minMaxClamp + '.outputR', detachNode + '.parameter[0]', f=True)
    cmds.connectAttr(minMaxClamp + '.outputB', detachNode + '.parameter[1]', f=True)

    # Return Result
    return detachCrv


def buildCurveRig(crv):
    """
    """
    # Get Prefix
    prefix = glTools.utils.stringUtils.stripSuffix(crv)

    # Build Joints
    pts = glTools.utils.base.getPointArray(crv)

    jnts = []
    cmds.select(cl=True)
    for i in range(len(pts)):
        ind = glTools.utils.stringUtils.alphaIndex(i)
        jnt = cmds.joint(p=pts[i], n=prefix + '_fk' + ind + '_jnt')
        cmds.joint()
        cmds.select(jnt)

    # Orient Joints

    # Build FK

    # Build Offset


def buildSubCurve(crv):
    """
    """
    # Build Sub Curve
    prefix = glTools.utils.stringUtils.stripSuffix(crv)
    subCrvShape = cmds.createNode('nurbsCurve', n=prefix + '_subCrvShape')
    subCrv = cmds.listRelatives(subCrvShape, p=True, pa=True)[0]
    subCrvNode = cmds.createNode('subCurve', n=prefix + '_subCurve')

    # Connect Sub Curve
    cmds.connectAttr(crv + '.worldSpace[0]', subCrvNode + '.inputCurve', f=True)
    cmds.connectAttr(subCrvNode + '.outputCurve', subCrvShape + '.create', f=True)

    # Connect Sub Curve Min/Max
    cmds.addAttr(subCrv, ln='min', min=0, max=0.999, dv=0, k=True)
    cmds.addAttr(subCrv, ln='max', min=0.001, max=1, dv=1, k=True)
    cmds.connectAttr(subCrv + '.min', subCrvNode + '.minValue', f=True)
    cmds.connectAttr(subCrv + '.max', subCrvNode + '.maxValue', f=True)
    cmds.setAttr(subCrvNode + '.relative', 1)

    # Return Result
    return subCrv


def resetCV(cvs):
    """
    """
    # Check CVs
    if not cvs: return None
    cvList = cmds.filterExpand(cvs, ex=True, sm=28)

    # Reset CVs
    for cv in cvList:
        crv = cmds.ls(cv, o=True)[0]
        i = glTools.utils.component.index(cv)
        cmds.setAttr(crv + '.controlPoints[' + i + '].xValue', 0)
        cmds.setAttr(crv + '.controlPoints[' + i + '].yValue', 0)
        cmds.setAttr(crv + '.controlPoints[' + i + '].zValue', 0)


def attachCurve(base, crv, cleanup=True):
    """
    """
    # Get Spans
    spans = cmds.getAttr(crv + '.spans')
    cmds.setAttr(base + '.spans', spans)

    # Match Shape
    shapeOrig = base + 'ShapeOrig'
    cmds.setAttr(shapeOrig + '.intermediateObject', 0)
    cmds.rebuildCurve(shapeOrig, ch=True, rpo=True, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=spans, d=3)
    bs = cmds.blendShape(crv, shapeOrig)[0]
    cmds.setAttr(bs + '.w[0]', 1)

    # Delete Orig
    if cleanup:
        cmds.delete(shapeOrig, ch=True)
        cmds.delete(crv)

    # Restore Intermediate Shape
    cmds.setAttr(shapeOrig + '.intermediateObject', 1)

    # Return Result
    return


def attachToCurveParam(ctrl, crv):
    """
    """
    grp = cmds.listRelatives(ctrl, p=True, pa=True)[0]
    param = cmds.getAttr(ctrl + '.param')
    glTools.utils.attach.attachToCurve(crv, grp, param, uAttr='param')
    cmds.connectAttr(ctrl + '.param', grp + '.param', f=True)


def addDropoffControls(locs, prefix):
    """
    """
    ctrlBuilder = glTools.tools.controlBuilder.ControlBuilder()
    for i in range(len(locs)):
        pre = prefix + glTools.utils.stringUtils.stripSuffix(locs[i])
        wire = cmds.listConnections(locs[i] + '.param', s=False, d=True)[0]
        param = cmds.getAttr(locs[i] + '.param')
        ind = glTools.utils.attribute.getConnectionIndex(locs[i] + '.param')
        ctrl = ctrlBuilder.create('sphere', pre + '_ctrl')
        grp = glTools.utils.base.group(ctrl)
        cmds.connectAttr(locs[i] + '.worldPosition[0]', grp + '.translate', f=True)
        cmds.addAttr(ctrl, ln='param', min=0, max=1, dv=param, k=True)
        cmds.addAttr(ctrl, ln='bulge', min=-1, dv=0, k=True)
        cmds.connectAttr(ctrl + '.param', locs[i] + '.param[' + str(ind) + ']', f=True)
        cmds.connectAttr(ctrl + '.bulge', wire + '.wireLocatorEnvelope[' + str(ind) + ']', f=True)


def buildTube(crv, profile = None, addCage = False, prefix = None):
"""
"""
# Nurbs Tube
cmds.extrude(
    ch=True,
    rn=False,
    po=0,
    et=2,
    ucp=1,
    fpt=1,
    upn=1,
    rotation=0,
    scale=1,
    rsp=1
)

# Polygon Tube
cmds.extrude(
    ch=True,
    rn=False,
    po=1,
    et=2,
    ucp=1,
    fpt=1,
    upn=1,
    rotation=0,
    scale=1,
    rsp=1
)
