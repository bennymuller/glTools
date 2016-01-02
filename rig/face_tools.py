import maya.cmds as cmds
import glTools.tools.createAlongCurve
import glTools.tools.distanceDriver
import glTools.utils.attach
import glTools.utils.curve
import glTools.utils.mathUtils
import glTools.utils.meshIntersectArray
import glTools.utils.shape
import glTools.utils.stringUtils


def duplicateAsDrivenTransform(transform, name, transformType=0):
    if cmds.objExists(name):
        return name

    pos = cmds.xform(transform, q=True, ws=True, rp=True)
    if transformType == 0:
        drivenTrans = cmds.group(empty=True, name=name)
    elif transformType == 1:
        drivenTrans = cmds.spaceLocator(name=name)[0]
        cmds.setAttr('%s.visibility' % drivenTrans, 0)
    else:
        raise Exception('transformType must be set to 0 or 1')

    cmds.connectAttr('%s.translate' % transform, '%s.translate' % drivenTrans)
    cmds.connectAttr('%s.rotate' % transform, '%s.rotate' % drivenTrans)
    cmds.connectAttr('%s.scale' % transform, '%s.scale' % drivenTrans)

    channelState = glTools.utils.channelState.ChannelState()
    channelState.setFlags([2, 2, 2, 2, 2, 2, 2, 2, 2, 1], objectList=[drivenTrans])

    return drivenTrans


def mirrorPts(ctrlPts):
    """
    Mirror face control points.
    Control point mirroring is based on naming prefixes.
    @param ctrlPts: Control points to mirror.
    @type ctrlPts: list
    """
    # ==========================
    # - For Each Control Point -
    # ==========================

    mirrorPts = []
    for ctrlPt in ctrlPts:

        # ============================
        # - Get Control Point Mirror -
        # ============================

        mirrorPt = ctrlPt
        if ctrlPt.startswith('lf_'):
            mirrorPt = ctrlPt.replace('lf_', 'rt_')
        elif ctrlPt.startswith('rt_'):
            mirrorPt = ctrlPt.replace('rt_', 'lf_')
        else:
            continue
        if not cmds.objExists(mirrorPt):
            raise Exception('Control point mirror "' + mirrorPt + '" does not exist!')

        # ===================
        # - Mirror Position -
        # ===================

        pos = cmds.xform(ctrlPt, q=True, ws=True, rp=True)
        mpos = cmds.xform(mirrorPt, q=True, ws=True, rp=True)
        cmds.move(-pos[0] - mpos[0], pos[1] - mpos[1], pos[2] - mpos[2], mirrorPt, r=True)

        # ===================
        # - Mirror Rotation -
        # ===================

        rot = cmds.getAttr(ctrlPt + '.r')[0]
        cmds.setAttr(mirrorPt + '.r', rot[0], -rot[1], -rot[2])

        # =================
        # - Append Result -
        # =================

        mirrorPts.append(mirrorPt)

    # =================
    # - Return Result -
    # =================

    return mirrorPts


def ctrlPointCurve(curve,
                   nucmdstrlPts=3,
                   guideGeo=None,
                   meshIntersect=None,
                   prefix=None):
    """
    Create a control point (locator) curve and project to guide surface.
    Control points are projected to guide using geometry constraints.
    @param curve: Curve to create control points from.
    @type curve: str
    @param nucmdstrlPts: Number of curve control points to build.
    @type nucmdstrlPts: str
    @param guideGeo: Guide surface to constrain control points to.
    @type guideGeo: str
    @param meshIntersect: MeshIntersectArray node to attach to. If None, use geometryConstraint.
    @type meshIntersect: str or None
    @param prefix: Naming prefix.
    @type prefix: str
    """
    # ==========
    # - Checks -
    # ==========

    if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(curve)

    # =========================
    # - Create Control Points -
    # =========================

    paramList = glTools.utils.curve.sampleParam(curve=curve,
                                                samples=nucmdstrlPts,
                                                useDistance=True)

    # Build Anchors
    ctrlPts = []
    for i in range(len(paramList)):
        # Create Anchor
        ind = glTools.utils.stringUtils.alphaIndex(i)
        ctrlPt = glTools.tools.createAlongCurve.createAtParam(curve,
                                                              param=paramList[i],
                                                              objType='locator',
                                                              name=prefix + '_ctrlPt' + ind + '_loc')
        ctrlPts.append(ctrlPt)

    # ===============
    # - Build Curve -
    # ===============

    degree = 3
    if nucmdstrlPts < 4: degree = 1
    ctrlCrv = glTools.utils.curve.createFromLocators(locatorList=ctrlPts,
                                                     degree=degree,
                                                     attach=True,
                                                     prefix=prefix + '_ctrlPt')
    # Rebuild Degree 1 Curve
    if degree == 1:
        glTools.utils.shape.createIntermediate(ctrlCrv)
        cmds.rebuildCurve(ctrlCrv, d=3, s=0, rt=0, rpo=1, end=1, fitRebuild=0)

    # Group Curve
    grp = cmds.group(ctrlCrv, ctrlPts, n=prefix + '_grp')

    # =========================
    # - Constrain to Geometry -
    # =========================

    geoConstraint = None
    intersectPt = []
    if guideGeo:

        # Use meshIntersectArray
        if meshIntersect:
            for ctrlPt in ctrlPts:
                # ctrlPtAttr = cmds.listConnections(ctrlPt+'.worldPosition[0]',s=False,d=True,p=True)[0]
                intersectPt.append(cmds.duplicate(ctrlPt, name='%s_intersectPt_loc' % prefix)[0])
                outputAttr = glTools.utils.meshIntersectArray.addIntersect(meshIntersect,
                                                                           intersectPt[-1] + '.worldPosition[0]')

                cmds.connectAttr(outputAttr[0], '%s.translate' % ctrlPt, f=True)

        # Use geometryConstraint
        else:
            geoConstraint = [cmds.geometryConstraint(guideGeo, ctrlPt)[0] for ctrlPt in ctrlPts]

            """ may want to add an option in the future for using follicles
            uvList = []
            for i, pt in enumerate(ctrlPts):
                pos = cmds.pointPosition(pt, world=True)
                uv = glTools.utils.mesh.closestUV(guideGeo,point=pos)
                uvList.append(uv)

                follicleList.append( glTools.utils.follicle.create( targetGeo = guideGeo,
                                                parameter    = uv,
                                                prefix       = '%s_%s_follicle' % (prefix, i) ) )

                cmds.parent(pt, follicleList[-1])
                cmds.parent(follicleList[-1], grp)
                cmds.setAttr('%s.translate' % pt, *[0,0,0])
                cmds.setAttr('%s.rotate' % pt, *[0,0,0])
            """

    # =================
    # - Return Result -
    # =================

    result = {}
    result['grp'] = grp
    result['crv'] = ctrlCrv
    result['pnt'] = ctrlPts
    result['geoConstraint'] = geoConstraint
    result['intersectPt'] = intersectPt
    return result


def midPtConstraint(midPt,
                    pt1,
                    pt2,
                    orient=False,
                    distRemap=False,
                    prefix=None):
    """
    Constrain a mid point to 2 end points using a point constraint.
    Optionally, constraint weights can be remaped based on distance between end points.
    @param midPt: Mid point to constrain.
    @type midPt: str
    @param pt1: First end point to constrain to.
    @type pt1: str
    @param pt2: Second end point to constrain to.
    @type pt2: str
    @param orient: Orient mid point.
    @type orient: bool
    @param distRemap: Remap constraint weight based on distance between end points.
    @type distRemap: bool
    @param prefix: Naming prefix.
    @type prefix: str
    """
    # ==========
    # - Checks -
    # ==========

    if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(midPt)

    # ==============================
    # - Build Mid Point Constraint -
    # ==============================

    ptConst = cmds.pointConstraint(pt1, pt2, midPt, n=prefix + '_midPt_pointConstraint')[0]

    # ===============================
    # - Build Distance Weight Remap -
    # ===============================

    if distRemap:
        # Distance Remap Output
        remap = glTools.tools.distanceDriver.distanceRemapOutput(pt1,
                                                                 pt2,
                                                                 minDist=None,
                                                                 maxDist=None,
                                                                 minValue=0.0,
                                                                 maxValue=1.0,
                                                                 restValue=0.5,
                                                                 attrObject=midPt,
                                                                 prefix=prefix)

        wtAttr = remap[0]
        wtRev = cmds.createNode('reverse', n=prefix + '_midPt_reverse')
        cmds.connectAttr(wtAttr, wtRev + '.inputX', f=True)
        wtRevAttr = wtRev + '.outputX'

        # Connect Constraint Weights
        cmds.connectAttr(wtAttr, ptConst + '.w0', f=True)
        cmds.connectAttr(wtRevAttr, ptConst + '.w1', f=True)

    # =================
    # - Return Result -
    # =================

    return ptConst


def buildCurvePoints(curve,
                     numPts,
                     useDistance=False,
                     meshIntersect=None,
                     prefix=None,
                     suffix=None):
    """
    Create locators along a specified curve and project to a target mesh using a meshIntersectArray node.
    @param curve: Curve to build points from.
    @type curve: str
    @param numPts: Number of points to build along curve.
    @type numPts: int
    @param useDistance: Distribute points using world space distance as opposed to parametric distance.
    @type useDistance: bool
    @param meshIntersect: MeshIntersectArray node to project points.
    @type meshIntersect: str or None
    @param prefix: Naming prefix.
    @type prefix: str
    @param suffix: Naming suffix.
    @type suffix: str
    """
    # ==========
    # - Checks -
    # ==========

    if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(curve)
    if not suffix: suffix = 'pt'

    # ==================
    # - Build Controls -
    # ==================

    pts = glTools.tools.createAlongCurve.create(curve,
                                                'locator',
                                                objCount=numPts,
                                                parent=False,
                                                useDistance=useDistance,
                                                minPercent=0.0,
                                                maxPercent=1.0,
                                                spacing=1.0,
                                                prefix=prefix,
                                                suffix=suffix)

    # Attach Controls
    for pt in pts:

        attach = glTools.utils.attach.attachToCurve(curve,
                                                    pt,
                                                    useClosestPoint=True,
                                                    uAttr='param',
                                                    prefix=prefix)

        # Project To Mesh
        if meshIntersect:
            # Add Intersection
            pointOnCurve = attach[0]
            intersectOut = glTools.utils.meshIntersectArray.addIntersect(meshIntersect, pointOnCurve + '.position')
            cmds.connectAttr(intersectOut[0], pt + '.translate')

            # Delete Point Constraint
            cmds.delete(attach[1])

    # Return Result
    return pts


# -------------
# UNUSED / OLD
# -------------

def createCtrlPtProj(curve,
                     nucmdstrlPts=3,
                     meshIntersect=None,
                     prefix=None):
    """
    Create a control point (locator) curve and project to guide surface.
    Control points are projected to guide using a meshIntersectArray node.
    """
    # Check Prefix
    if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(curve)

    # Create Control Points
    paramList = glTools.utils.curve.sampleParam(curve=curve,
                                                samples=nucmdstrlPts,
                                                useDistance=True)

    # Build Anchors
    ctrlPtList = []
    for i in range(len(paramList)):
        # Create Anchor
        ind = glTools.utils.stringUtils.alphaIndex(i)
        ctrlPt = glTools.tools.createAlongCurve.createAtParam(curve,
                                                              param=paramList[i],
                                                              objType='locator',
                                                              name=prefix + '_ctrlPt' + ind + '_loc')
        ctrlPtList.append(ctrlPt)

    # Build Curve
    ctrlPtCurve = glTools.utils.meshIntersectArray.pointProjectCurve(meshIntersect, ctrlPtList, prefix + '_ctrlPt')

    glTools.utils.shape.createIntermediate(ctrlPtCurve)
    rebuildCrv = cmds.rebuildCurve(ctrlPtCurve,
                                 degree=3,
                                 spans=0,
                                 fitRebuild=False,
                                 rpo=True,
                                 rebuildType=0,
                                 end=1)
    rebuildCrv = cmds.rename(rebuildCrv[1], prefix + '_ctrlPtCrv_rebuildCurve')

    # Group
    grp = cmds.group(em=True, n=prefix + '_ctrlPt_grp')
    cmds.parent(ctrlPtCurve, ctrlPtList, grp)

    # Return Result
    return [grp, ctrlPtCurve, ctrlPtList]


def createAnchors(curve,
                  numAnchors=2,
                  useDistance=False,
                  prefix=None):
    """
    """
    # Check Prefix
    if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(curve)

    # Build Anchors Param List
    paramList = glTools.utils.curve.sampleParam(curve=curve,
                                                samples=numAnchors,
                                                useDistance=useDistance)

    # Build Anchors
    anchorList = []
    for i in range(len(paramList)):
        # Create Anchor
        ind = glTools.utils.stringUtils.alphaIndex(i)
        anchor = glTools.tools.createAlongCurve.createAtParam(curve,
                                                              param=paramList[i],
                                                              objType='locator',
                                                              name=prefix + '_anchor' + ind + '_loc')

        # Attach Anchor
        glTools.utils.attach.attachToCurve(curve,
                                           anchor,
                                           useClosestPoint=True,
                                           uAttr='param',
                                           prefix=prefix + '_anchor' + ind)

        anchorList.append(anchor)

    # Return Result
    return anchorList


def createIntermediates(curve,
                        anchor1,
                        anchor2,
                        numIntermediates=1,
                        prefix=None):
    """
    """
    # ==========
    # - Checks -
    # ==========

    if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(curve)

    # ==========================
    # - Generate Intermediates -
    # ==========================

    # Get Anchor Params
    param1 = cmds.getAttr(anchor1 + '.param')
    param2 = cmds.getAttr(anchor2 + '.param')

    # Get Intermediate Params
    # - Add 2 to num samples to only pull inside values
    # - List slice used to trim bookend values
    intParam = glTools.utils.mathUtils.distributeValue(numIntermediate + 2,
                                                       rangeStart=param1,
                                                       rangeEnd=param2)[1:-1]

    # Build Intermediates
    intermediateList = []
    for i in range(len(intParam)):
        # Create Anchor
        intermediate = glTools.tools.createAlongCurve.createAtParam(curve,
                                                                    param=intParam[i],
                                                                    objType='locator',
                                                                    name=prefix + '_intermediate' + ind + '_loc')

        # Append Result
        intermediateList.append(intermediate)

    # Return Result
    return intermediateList


def buildLinearPoints(curve,
                      nucmdstrl,
                      useDistance=False,
                      guideSrf=None,
                      orient=False,
                      prefix=None,
                      suffix=None):
    """
    Create locators along curve and project to mesh using geometry and normal constraints.
    """
    # ==========
    # - Checks -
    # ==========

    if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(curve)
    if not suffix: suffix = 'jnt'

    # Build Controls
    ctrls = glTools.tools.createAlongCurve.create(curve,
                                                  'locator',
                                                  objCount=nucmdstrl,
                                                  parent=False,
                                                  useDistance=useDistance,
                                                  minPercent=0.0,
                                                  maxPercent=1.0,
                                                  spacing=1.0,
                                                  prefix=prefix,
                                                  suffix=suffix)

    # Attach Controls
    for ctrl in ctrls:

        cmds.select(ctrl)
        jnt = cmds.joint()

        attach = glTools.utils.attach.attachToCurve(curve,
                                                    ctrl,
                                                    useClosestPoint=True,
                                                    uAttr='param',
                                                    prefix=prefix)

        # Constrain to Guide
        if guideSrf:

            # Constrain Position
            geocmdsonst = cmds.geometryConstraint(guideSrf, ctrl)[0]

            # Constrain Orient
            if orient:
                norcmdsonst = cmds.normalConstraint(guideSrf,
                                                ctrl,
                                                aimVector=(0, 0, 1),
                                                upVector=(-1, 0, 0),
                                                worldUpType='vector')[0]

                cmds.connectAttr(attach[0] + '.tangent', norcmdsonst + '.worldUpVector', f=True)

    # Return Result
    return ctrls
