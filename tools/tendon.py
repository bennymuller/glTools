import maya.cmds as cmds
import glTools.utils.base
import glTools.utils.curve
import glTools.utils.mathUtils


def build(startPt=[-1, 0, 0], endPt=[1, 0, 0], attachments=2, outputMesh=False, radius=0.2, prefix='tendon'):
    """
    """
    #

    # Get points
    startPt = glTools.utils.base.getMPoint(startPt)
    endPt = glTools.utils.base.getMPoint(endPt)

    # Get offset
    offsetVec = endPt - startPt
    offsetInc = 1.0 / (attachments - 1)

    # Get Point List
    ptList = []
    for i in range(attachments - 1):
        pt = startPt + (offsetVec * offsetInc)
        ptList.append(pt[0], pt[1], pt[2])

    # Build tendon curve base
    tendonCrv = glTools.utils.curve.createFromPointList(ptList, 1, prefix)
    # Generate tendon curve locators
    tendonLocList = glTools.utils.curve.locatorCurve(tendonCrv, freeze=False, prefix=prefix)
    # Rebuild tendon curve
    if attachments > 2:
        tendonRebuild = cmds.rebuildCurve(tendonCrv, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1, s=0, d=3,
                                        tol=0.01)


def crvTendon(curve, geo, precision=4, prefix='tendon'):
    """
    """
    # rebuildCurve degree 1
    baseCurve = cmds.rebuildCurve(curve, ch=0, s=1, d=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1)

    # create cv locators
    baseLocs = glTools.utils.curve.locatorCurve(baseCurve, prefix=prefix + '_baseCrv')

    # generate geo constraint curve
    geoCurve = cmds.rebuildCurve(baseCurve, ch=1, s=precsion, d=1, rpo=0, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1)
    geoCurveLocs = glTools.utils.curve.locatorCurve(geoCurve, prefix=prefix + '_geoCrv')

    # generate reference curve
    refCurve = cmds.rebuildCurve(baseCurve, ch=1, s=precsion, d=1, rpo=0, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1)
    refCurveInfo = cmds.createNode('curveInfo', n=prefix + '_ref_curveInfo')
    cmds.connectAttr(refCurve + '.worldSpace[0]', refCurveInfo + '.inputCurve', f=True)
    refCurveLocs = []
    for i in range(precsion + 1):
        refNull = cmds.group(em=True, n=prefix + '_ref' + str(i) + '_null')
        cmds.connectAttr(refCurveInfo + '.controlPoints[' + str(i) + ']', refNull + '.t')
        refCurveLocs.append(refNull)

    # Locator Constraints
    for i in range(precsion + 1):
        cmds.pointConstraint(refCurveLocs[i], geoCurveLocs[i])
        cmds.geometryConstraint(geo, geoCurveLocs[i])

    # fitBspline
    bSpline = cmds.fitBspline(geoCurve, ch=1)
