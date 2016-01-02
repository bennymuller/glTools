import math
import maya.cmds as cmds
import glTools.utils.attach
import glTools.utils.base
import glTools.utils.constraint
import ctrlBuilder
import glTools.utils.curve
import glTools.utils.shape
import glTools.utils.stringUtils
import glTools.utils.surface


def spine_ribbon(ptList, spans=0, joints=6, prefix='cn_spine'):
    """
    """
    # ==========
    # - Checks -
    # ==========

    if not ptList: raise Exception('Invalid point list!')
    if not prefix: prefix = 'cn_spine'

    # ========================
    # - Build Spine Locators -
    # ========================

    pointList = [glTools.utils.base.getPosition(pt) for pt in ptList]
    locList = []
    lfLocList = []
    rtLocList = []
    for pt in range(len(pointList)):
        strInd = glTools.utils.stringUtils.alphaIndex(pt)
        loc = cmds.spaceLocator(p=(0, 0, 0), n=prefix + strInd + '_loc')[0]
        lfLoc = cmds.spaceLocator(p=(0.5, 0, 0), n=prefix + strInd + '_loc')[0]
        rtLoc = cmds.spaceLocator(p=(-0.5, 0, 0), n=prefix + strInd + '_loc')[0]
        cmds.parent([lfLoc, rtLoc], loc)
        cmds.move(pointList[pt][0], pointList[pt][1], pointList[pt][2], loc, ws=True, a=True)
        locList.append(loc)
        lfLocList.append(lfLoc)
        rtLocList.append(rtLoc)

    # ===========================
    # - Build Spine Loft Curves -
    # ===========================

    # Build Curves
    lfCurve = glTools.utils.curve.createFromLocators(lfLocList, degree=1, attach=True, prefix=prefix + 'A')
    rtCurve = glTools.utils.curve.createFromLocators(rtLocList, degree=1, attach=True, prefix=prefix + 'B')

    # Get Curve Shapes
    lfCurveShape = cmds.listRelatives(lfCurve, s=True, pa=True)[0]
    rtCurveShape = cmds.listRelatives(rtCurve, s=True, pa=True)[0]
    glTools.utils.shape.createIntermediate(lfCurveShape)
    glTools.utils.shape.createIntermediate(rtCurveShape)

    # Rebuild Curves
    if not spans: spans = len(ptList) - 1
    lfRebuildCrv = cmds.rebuildCurve(lfCurve, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1, s=spans, d=3, tol=0)
    rtRebuildCrv = cmds.rebuildCurve(rtCurve, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1, s=spans, d=3, tol=0)
    lfRebuildCrv = cmds.rename(lfRebuildCrv[1], prefix + 'A_rebuildCurve')
    rtRebuildCrv = cmds.rename(rtRebuildCrv[1], prefix + 'B_rebuildCurve')

    # =========================
    # - Generate Loft Surface -
    # =========================

    loft = cmds.loft([lfCurve, rtCurve], d=1, n=prefix + '_surface')
    loftSurface = loft[0]
    loftNode = cmds.rename(loft[1], prefix + '_loft')

    # ============================
    # - Create and Attach Joints -
    # ============================

    jointList = []
    inc = 1.0 / (joints - 1)
    for i in range(joints):
        cmds.select(cl=1)
        strInd = glTools.utils.stringUtils.alphaIndex(i)
        joint = cmds.joint(n=prefix + strInd + '_jnt')
        glTools.utils.attach.attachToSurface(loftSurface, joint, uValue=.5, vValue=inc * i, orient=True, uAxis='y',
                                             vAxis='x', uAttr='uCoord', vAttr='vCoord', alignTo='v',
                                             prefix=prefix + strInd)
        jointList.append(joint)

    # ===========
    # - Cleanup -
    # ===========

    jntGrp = cmds.group(jointList, n=prefix + '_jnt_grp')
    rigGrp = cmds.group([lfCurve, rtCurve, loftSurface], n=prefix + '_rig_grp')
    locGrp = cmds.group(locList, n=prefix + '_loc_grp')

    # =================
    # - Return Result -
    # =================

    return [jntGrp, rigGrp, locGrp]


def create_basic(length=10.0, width=0.5, mainCtrls=4, subCtrls=10, surface=True, curve=False, prefix=''):
    """
    Create a basic ribbon rig with a single base control
    @param length: Ribbon length
    @type length: float
    @param width: Ribbon width
    @type width: float
    @param mainCtrls: Number of main ribbon controls
    @type mainCtrls: int
    @param subCtrls: Number of ribbon sub controls
    @type subCtrls: int
    @param surface: Output ribbon surface
    @type surface: bool
    @param curve: Output ribbon curve
    @type curve: bool
    @param prefix: Name prefix for created nodes
    @type prefix: str
    """
    # Check prefix
    if not prefix: prefix = 'ribbon'

    # -----------------
    # - Create Groups -
    # -----------------

    ctrl_grp = cmds.group(em=True, n=prefix + '_ctrl_grp')
    hist_grp = cmds.group(em=True, n=prefix + '_hist_grp')
    out_grp = cmds.group(em=True, n=prefix + '_out_grp')
    rig_grp = cmds.group([ctrl_grp, hist_grp, out_grp], n=prefix + '_grp')

    cmds.setAttr(hist_grp + '.v', 0)

    # ----------------------
    # - Create Base Ribbon -
    # ----------------------

    base_pts = []
    base_inc = length / (mainCtrls - 1)
    for i in range(mainCtrls): base_pts.append([width * .5, base_inc * i, 0.0])

    # Curve 0
    base_crv_0 = cmds.curve(d=1, p=base_pts, k=range(len(base_pts)), n=prefix + '_base0_crv')
    cmds.rebuildCurve(base_crv_0, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=1, kep=1, kt=1, s=0, d=3, tol=0)
    base_crv_0_locs = glTools.utils.curve.locatorCurve(base_crv_0, prefix=prefix + '_base0')
    glTools.utils.shape.createIntermediate(base_crv_0)
    cmds.rebuildCurve(base_crv_0, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1, s=(mainCtrls - 1), d=3, tol=0)

    # Flip CV array
    base_pts = [(-i[0], i[1], i[2]) for i in base_pts]

    # Curve 1
    base_crv_1 = cmds.curve(d=1, p=base_pts, k=range(len(base_pts)), n=prefix + '_base1_crv')
    cmds.rebuildCurve(base_crv_1, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=1, kep=1, kt=1, s=0, d=3, tol=0)
    base_crv_1_locs = glTools.utils.curve.locatorCurve(base_crv_1, prefix=prefix + '_base1')
    glTools.utils.shape.createIntermediate(base_crv_1)
    cmds.rebuildCurve(base_crv_1, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1, s=(mainCtrls - 1), d=3, tol=0)

    # Loft
    base_loft = cmds.loft([base_crv_0, base_crv_1], d=1, n=prefix + '_base_surface')
    base_surface = base_loft[0]
    base_loft = cmds.rename(base_loft[1], prefix + '_base_loft')

    # Rebuild
    base_rebuild = cmds.rebuildSurface(base_surface, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=1, kc=1, su=0, du=0, sv=0, dv=0,
                                     tol=0, fr=0, dir=2, n=prefix + '_base_rebuildSurface')

    cmds.parent([base_crv_0, base_crv_1, base_surface], hist_grp)

    # -----------------------
    # - Create Base Control -
    # -----------------------

    ctrlBuilder = glTools.tools.controlBuilder.ControlBuilder()

    cmds.select(cl=True)
    base_jnt = cmds.joint(n=prefix + '_base_jnt', radius=0.0)
    base_grp = cmds.group(base_jnt, n=prefix + '_base_grp')
    cmds.parent(base_grp, ctrl_grp)

    ctrlBuilder.controlShape(base_jnt, 'circle', rotate=(90, 0, 0), scale=0.2 * length)

    # ------------------------
    # - Create Main Controls -
    # ------------------------

    main_ctrl_list = []
    main_grp_list = []
    main_ctrl_grp = cmds.group(em=True, n=prefix + '_mainCtrl_grp')
    for i in range(mainCtrls):

        # Clear selection
        cmds.select(cl=True)

        # Create main control joint
        index = glTools.utils.stringUtils.alphaIndex(int(math.floor(i)), True)
        jnt = cmds.joint(n=prefix + '_main' + index + '_jnt', radius=0.0)
        grp = cmds.group(jnt, n=prefix + '_main' + index + '_grp')

        ctrlBuilder.controlShape(jnt, 'square', rotate=(90, 0, 0), scale=0.125 * length)

        # Position main control joint
        locs = [base_crv_0_locs[i], base_crv_1_locs[i]]
        cmds.delete(cmds.pointConstraint(locs, grp))
        cmds.parent(locs, jnt)
        cmds.makeIdentity(locs, apply=True, t=1, r=1, s=1, n=0)
        for loc in locs: cmds.setAttr(loc + '.v', 0)

        # Append list
        main_ctrl_list.append(jnt)
        main_grp_list.append(grp)

    cmds.parent(main_grp_list, main_ctrl_grp)
    cmds.parent(main_ctrl_grp, base_jnt)

    # ----------------------
    # - Build Sub Controls -
    # ----------------------

    sub_ctrl_list = []
    sub_grp_list = []
    sub_ctrl_grp = cmds.group(em=True, n=prefix + '_subCtrl_grp')

    sub_inc = length / (subCtrls - 1)

    for i in range(subCtrls):
        # Clear selection
        cmds.select(cl=True)

        # Create sub control joint
        index = glTools.utils.stringUtils.alphaIndex(i, True)
        sub_jnt = cmds.joint(n=prefix + '_sub' + index + '_jnt', radius=0.0)
        sub_grp = cmds.group(sub_jnt, n=prefix + '_sub' + index + '_grp')

        ctrlBuilder.controlShape(sub_jnt, 'box', scale=0.025 * length)

        # Position and attach sub controls
        cmds.setAttr(sub_grp + '.t', 0.0, (sub_inc * i), 0.0)
        glTools.utils.attach.attachToSurface(base_surface, sub_grp, uValue=0.0, vValue=0.0, useClosestPoint=True,
                                             orient=True, uAxis='y', vAxis='x', uAttr='uCoord', vAttr='vCoord',
                                             alignTo='v', prefix=prefix + '_sub' + index)

        # Connect scale
        cmds.connectAttr(base_jnt + '.scale', sub_grp + '.scale')

        # Append list
        sub_ctrl_list.append(sub_jnt)
        sub_grp_list.append(sub_grp)

    cmds.parent(sub_grp_list, sub_ctrl_grp)
    cmds.parent(sub_ctrl_grp, ctrl_grp)

    # ----------------
    # - Build Output -
    # ----------------

    # Build point array
    sub_inc = length / (subCtrls - 1)
    pts = [[0, (sub_inc * i), 0] for i in range(subCtrls)]

    # -----
    # Curve

    if curve:

        # Build curve
        ribbon_crv = cmds.curve(d=1, p=pts, n=prefix + '_ribbon_curve')
        cmds.rebuildCurve(ribbon_crv, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=1, kep=1, kt=1, s=0, d=3, tol=0)

        # Create curve locators
        crv_locs = glTools.utils.curve.locatorCurve(ribbon_crv, prefix=prefix)
        glTools.utils.shape.createIntermediate(ribbon_crv)

        # Rebuild ribbon curve
        cmds.rebuildCurve(ribbon_crv, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1, s=(subCtrls - 1), d=3, tol=0,
                        n=prefix + '_ribbon_rebuildCurve')

        # Parent curve locators
        for i in range(len(crv_locs)):
            cmds.parent(crv_locs[i], sub_ctrl_list[i])
            cmds.setAttr(crv_locs[i] + '.v', 0)

        cmds.parent(ribbon_crv, out_grp)

    # -----------
    # - Surface -

    if surface:

        # Offset CV array
        pts = [(width * .5, i[1], i[2]) for i in pts]

        # Sub Curve 0
        sub_crv_0 = cmds.curve(d=1, p=pts, k=range(len(pts)), n=prefix + '_sub0_crv')
        cmds.rebuildCurve(sub_crv_0, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=1, kep=1, kt=1, s=0, d=3, tol=0)
        sub_crv_0_locs = glTools.utils.curve.locatorCurve(sub_crv_0, prefix=prefix + '_sub0')
        glTools.utils.shape.createIntermediate(sub_crv_0)
        cmds.rebuildCurve(sub_crv_0, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1, s=(subCtrls - 1), d=3, tol=0,
                        n=prefix + '_sub0_rebuildCurve')

        # Flip CV array
        pts = [(-i[0], i[1], i[2]) for i in pts]

        # Curve 1
        sub_crv_1 = cmds.curve(d=1, p=pts, k=range(len(pts)), n=prefix + '_sub1_crv')
        cmds.rebuildCurve(sub_crv_1, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=1, kep=1, kt=1, s=0, d=3, tol=0)
        sub_crv_1_locs = glTools.utils.curve.locatorCurve(sub_crv_1, prefix=prefix + '_sub1')
        glTools.utils.shape.createIntermediate(sub_crv_1)
        cmds.rebuildCurve(sub_crv_1, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1, s=(subCtrls - 1), d=3, tol=0,
                        n=prefix + '_sub1_rebuildCurve')

        # Loft
        ribbon_loft = cmds.loft([sub_crv_0, sub_crv_1], d=1, n=prefix + '_ribbon_surface')
        ribbon_surface = ribbon_loft[0]
        ribbon_loft = cmds.rename(ribbon_loft[1], prefix + '_ribbon_loft')

        # Parent curve locators
        for i in range(len(pts)):
            locs = [sub_crv_0_locs[i], sub_crv_1_locs[i]]
            cmds.parent(locs, sub_ctrl_list[i])
            cmds.makeIdentity(locs, apply=True, t=1, r=1, s=1, n=0)
            for loc in locs: cmds.setAttr(loc + '.v', 0)

        cmds.parent([sub_crv_0, sub_crv_1], hist_grp)
        cmds.parent(ribbon_surface, out_grp)


def create(length=10.0, width=0.5, mainCtrls=4, subCtrls=10, surface=True, curve=False, prefix=''):
    """
    Create a ribbon rig with a primary base and tip controls
    @param length: Ribbon length
    @type length: float
    @param width: Ribbon width
    @type width: float
    @param mainCtrls: Number of main ribbon controls
    @type mainCtrls: int
    @param subCtrls: Number of ribbon sub controls
    @type subCtrls: int
    @param surface: Output ribbon surface
    @type surface: bool
    @param curve: Output ribbon curve
    @type curve: bool
    @param prefix: Name prefix for created nodes
    @type prefix: str
    """

    # Check prefix
    if not prefix: prefix = 'ribbon'

    # -----------------
    # - Create Groups -
    # -----------------

    ctrl_grp = cmds.group(em=True, n=prefix + '_ctrl_grp')
    hist_grp = cmds.group(em=True, n=prefix + '_hist_grp')
    out_grp = cmds.group(em=True, n=prefix + '_out_grp')
    rig_grp = cmds.group([ctrl_grp, hist_grp, out_grp], n=prefix + '_grp')

    cmds.setAttr(hist_grp + '.v', 0)

    # ----------------------
    # - Create Base Ribbon -
    # ----------------------

    # Generate point array
    base_inc = float(length) / (mainCtrls - 1)
    base_pts = [(width * .5, base_inc * i, 0.0) for i in range(mainCtrls)]

    # Curve 0
    base_crv_0 = cmds.curve(d=1, p=base_pts, k=range(len(base_pts)), n=prefix + '_base0_crv')
    cmds.rebuildCurve(base_crv_0, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=1, kep=1, kt=1, s=0, d=3, tol=0)
    base_crv_0_locs = glTools.utils.curve.locatorCurve(base_crv_0, prefix=prefix + '_base0')
    glTools.utils.shape.createIntermediate(base_crv_0)
    cmds.rebuildCurve(base_crv_0, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1, s=(mainCtrls - 1), d=3, tol=0)

    # Flip CV array
    base_pts = [(-i[0], i[1], i[2]) for i in base_pts]

    # Curve 1
    base_crv_1 = cmds.curve(d=1, p=base_pts, k=range(len(base_pts)), n=prefix + '_base1_crv')
    cmds.rebuildCurve(base_crv_1, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=1, kep=1, kt=1, s=0, d=3, tol=0)
    base_crv_1_locs = glTools.utils.curve.locatorCurve(base_crv_1, prefix=prefix + '_base1')
    glTools.utils.shape.createIntermediate(base_crv_1)
    cmds.rebuildCurve(base_crv_1, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1, s=(mainCtrls - 1), d=3, tol=0)

    # Loft
    base_loft = cmds.loft([base_crv_0, base_crv_1], d=1, n=prefix + '_base_surface')
    base_surface = base_loft[0]
    base_loft = cmds.rename(base_loft[1], prefix + '_base_loft')

    # Rebuild
    base_rebuild = cmds.rebuildSurface(base_surface, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=1, kc=1, su=0, du=0, sv=0, dv=0,
                                     tol=0, fr=0, dir=2, n=prefix + '_base_rebuildSurface')

    cmds.parent([base_crv_0, base_crv_1, base_surface], hist_grp)

    # -------------------------------
    # - Create Base and Tip Control -
    # -------------------------------

    # Base Control
    cmds.select(cl=True)
    base_jnt = cmds.joint(n=prefix + '_baseA_jnt', radius=0.0)
    base_grp = cmds.group(base_jnt, n=prefix + '_baseA_grp')
    cmds.parent(base_grp, ctrl_grp)

    ctrlBuilder.controlShape(base_jnt, 'circle', rotate=(90, 0, 0), scale=0.2 * length)

    # Tip Control
    cmds.select(cl=True)
    tip_jnt = cmds.joint(n=prefix + '_tipA_jnt', radius=0.0)
    tip_grp = cmds.group(tip_jnt, n=prefix + '_tipA_grp')
    cmds.parent(tip_grp, ctrl_grp)
    # Position Tip
    cmds.move(0, length, 0, tip_grp, ws=True, a=True)

    ctrlBuilder.controlShape(tip_jnt, 'circle', rotate=(90, 0, 0), scale=0.2 * length)

    # ------------------------
    # - Create Main Controls -
    # ------------------------

    # Check mid control
    mid = False
    if (float(mainCtrls) / 2) % 1: mid = True

    # Determine mid point
    if mid:
        split = int(math.ceil(float(mainCtrls) / 2)) - 1
    else:
        split = int(mainCtrls / 2)

    # Create controls
    for i in range(mainCtrls):

        # Clear selection
        cmds.select(cl=True)

        # Create main control joint
        index = glTools.utils.stringUtils.alphaIndex(int(math.floor(i)), True)
        jnt = cmds.joint(n=prefix + '_main' + index + '_jnt', radius=0.0)
        grp = cmds.group(jnt, n=prefix + '_main' + index + '_grp')

        ctrlBuilder.controlShape(jnt, 'square', rotate=(90, 0, 0), scale=0.125 * length)

        # Position main control joint
        locs = [base_crv_0_locs[i], base_crv_1_locs[i]]
        cmds.delete(cmds.pointConstraint(locs, grp))
        cmds.parent(locs, jnt)
        cmds.makeIdentity(locs, apply=True, t=1, r=1, s=1, n=0)
        for loc in locs: cmds.setAttr(loc + '.v', 0)

        # Constrain to base/tip control
        connBlend = glTools.utils.constraint.blendConstraint([base_jnt, tip_jnt], grp, jnt, blendAttr='bias',
                                                             maintainOffset=True, prefix='')

        # Set constraint weights
        if mid and i == split:
            cmds.setAttr(connBlend, 0.5)
        else:
            if i < split:
                cmds.setAttr(connBlend, 0.0)
            else:
                cmds.setAttr(connBlend, 1.0)

        # Parent to main control group
        cmds.parent(grp, ctrl_grp)

    # ----------------------
    # - Build Sub Controls -
    # ----------------------

    sub_ctrl_list = []
    sub_grp_list = []
    sub_ctrl_grp = cmds.group(em=True, n=prefix + '_subCtrl_grp')
    # Turn off inheritTransform
    cmds.setAttr(sub_ctrl_grp + '.inheritsTransform', 0)

    # Build point array
    sub_inc = float(length) / (subCtrls - 1)
    pts = [[0, (sub_inc * i), 0] for i in range(subCtrls)]

    for i in range(subCtrls):
        # Clear selection
        cmds.select(cl=True)

        # Create sub control joint
        index = glTools.utils.stringUtils.alphaIndex(i, True)
        sub_jnt = cmds.joint(n=prefix + '_sub' + index + '_jnt', radius=0.0)
        sub_grp = cmds.group(sub_jnt, n=prefix + '_sub' + index + '_grp')

        ctrlBuilder.controlShape(sub_jnt, 'box', scale=0.025 * length)

        # Position and attach sub controls
        cmds.setAttr(sub_grp + '.t', pts[i][0], pts[i][1], pts[i][2])
        glTools.utils.attach.attachToSurface(base_surface, sub_grp, uValue=0.0, vValue=0.0, useClosestPoint=True,
                                             orient=True, uAxis='-x', vAxis='y', uAttr='uCoord', vAttr='vCoord',
                                             alignTo='v', prefix=prefix + '_sub' + index)

        # Append list
        sub_ctrl_list.append(sub_jnt)
        sub_grp_list.append(sub_grp)

    cmds.parent(sub_grp_list, sub_ctrl_grp)
    cmds.parent(sub_ctrl_grp, ctrl_grp)

    # ----------------
    # - Build Output -
    # ----------------

    # -----
    # Curve

    if curve:

        # Build curve
        ribbon_crv = cmds.curve(d=1, p=pts, n=prefix + '_ribbon_curve')
        cmds.rebuildCurve(ribbon_crv, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=1, kep=1, kt=1, s=0, d=3, tol=0)

        # Create curve locators
        crv_locs = glTools.utils.curve.locatorCurve(ribbon_crv, prefix=prefix)
        glTools.utils.shape.createIntermediate(ribbon_crv)

        # Rebuild ribbon curve
        cmds.rebuildCurve(ribbon_crv, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1, s=(subCtrls - 1), d=3, tol=0,
                        n=prefix + '_ribbon_rebuildCurve')

        # Parent curve locators
        for i in range(len(crv_locs)):
            cmds.parent(crv_locs[i], sub_ctrl_list[i])
            cmds.setAttr(crv_locs[i] + '.v', 0)

        cmds.parent(ribbon_crv, out_grp)

    # -----------
    # - Surface -

    if surface:

        # Offset CV array
        pts = [(width * .5, i[1], i[2]) for i in pts]

        # Sub Curve 0
        sub_crv_0 = cmds.curve(d=1, p=pts, k=range(len(pts)), n=prefix + '_sub0_crv')
        cmds.rebuildCurve(sub_crv_0, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=1, kep=1, kt=1, s=0, d=3, tol=0)
        sub_crv_0_locs = glTools.utils.curve.locatorCurve(sub_crv_0, prefix=prefix + '_sub0')
        glTools.utils.shape.createIntermediate(sub_crv_0)
        cmds.rebuildCurve(sub_crv_0, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1, s=(subCtrls - 1), d=3, tol=0,
                        n=prefix + '_sub0_rebuildCurve')

        # Flip CV array
        pts = [(-i[0], i[1], i[2]) for i in pts]

        # Curve 1
        sub_crv_1 = cmds.curve(d=1, p=pts, k=range(len(pts)), n=prefix + '_sub1_crv')
        cmds.rebuildCurve(sub_crv_1, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=1, kep=1, kt=1, s=0, d=3, tol=0)
        sub_crv_1_locs = glTools.utils.curve.locatorCurve(sub_crv_1, prefix=prefix + '_sub1')
        glTools.utils.shape.createIntermediate(sub_crv_1)
        cmds.rebuildCurve(sub_crv_1, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1, s=(subCtrls - 1), d=3, tol=0,
                        n=prefix + '_sub1_rebuildCurve')

        # Loft
        ribbon_loft = cmds.loft([sub_crv_0, sub_crv_1], d=1, n=prefix + '_ribbon_surface')
        ribbon_surface = ribbon_loft[0]
        ribbon_loft = cmds.rename(ribbon_loft[1], prefix + '_ribbon_loft')

        # Parent curve locators
        for i in range(len(pts)):
            locs = [sub_crv_0_locs[i], sub_crv_1_locs[i]]
            cmds.parent(locs, sub_ctrl_list[i])
            cmds.makeIdentity(locs, apply=True, t=1, r=1, s=1, n=0)
            for loc in locs: cmds.setAttr(loc + '.v', 0)

        cmds.parent([sub_crv_0, sub_crv_1], hist_grp)
        cmds.parent(ribbon_surface, out_grp)
