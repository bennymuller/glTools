import maya.cmds as cmds
import glTools.utils.base
import glTools.utils.curve
import glTools.utils.deformer
import glTools.utils.joint
import glTools.utils.skinCluster
import glTools.utils.stringUtils
import glTools.utils.surface


def buildRig(surface, uValue):
    """
    Build basic groom surface scuplting rig.
    @param surface: Surface to build joints along
    @type surface: str
    @param uValue: U isoparm to build joints along
    @type uValue: float
    """
    # ==========
    # - Checks -
    # ==========

    if not glTools.utils.surface.isSurface(surface):
        raise Exception('Object "' + surface + '" is not a valid surface!')

    # Check Domain
    if uValue > cmds.getAttr(surface + '.maxValueU'):
        raise Exception('U value "' + str(uValue) + '" is outside the parameter range!')
    if uValue < cmds.getAttr(surface + '.minValueU'):
        raise Exception('U value "' + str(uValue) + '" is outside the parameter range!')

    # Check SkinCluster
    skinCluster = glTools.utils.skinCluster.findRelatedSkinCluster(surface)
    if skinCluster:
        raise Exception('Surface "' + skinCluster + '" is already attached to an existing skinCluster!')

    # Get Surface Info
    surfFn = glTools.utils.surface.getSurfaceFn(surface)
    cvs = surfFn.nucmdsVsInU()

    # ================
    # - Build Joints -
    # ================

    # Extract IsoParm
    crv = cmds.duplicateCurve(surface + '.u[' + str(uValue) + ']', ch=False)[0]

    # Get Curve Points
    pts = glTools.utils.base.getPointArray(crv)
    cmds.delete(crv)

    # Create Joint Chain
    jnts = []
    cmds.select(cl=True)
    for i in range(len(pts)):
        # Select Prev Joint
        if i: cmds.select(jnts[-1])
        # Get Index String
        ind = glTools.utils.stringUtils.stringIndex(i)
        # Create Joint
        jnt = cmds.joint(p=pts[i], n=surface + str(i) + '_jnt')
        # Append Return List
        jnts.append(jnt)
    for i in range(len(pts)):
        # Orient Joint
        uv = glTools.utils.surface.closestPoint(surface, pos=pts[i])
        uTangent = cmds.pointOnSurface(surface, u=uv[0], v=uv[1], ntu=True)
        glTools.utils.joint.orient(jnts[i], upVec=uTangent)

    # ======================
    # - Create SkinCluster -
    # ======================

    skinCluster = cmds.skinCluster(surface, jnts, tsb=True)[0]

    # Clear Weights
    glTools.utils.skinCluster.clearWeights(surface)
    # Set Weights
    for i in range(len(pts)):
        # Generate Weights
        wts = []
        for k in range(cvs):
            for n in range(len(pts)):
                if i == n:
                    wts.append(1.0)
                else:
                    wts.append(0.0)
        # Set Influence Weights
        glTools.utils.skinCluster.setInfluenceWeights(skinCluster, jnts[i], wts, normalize=False)

    # =================
    # - Return Result -
    # =================

    return jnts


def removeRig(surface):
    """
    Remove groom surface scuplting rig.
    @param surface: Surface to remove rig from
    @type surface: str
    """
    # ==========
    # - Checks -
    # ==========

    # Check Surface
    if not glTools.utils.surface.isSurface(surface):
        raise Exception('Object "' + surface + '" is not a valid surface!')

    # Get SkinCluster
    skinCluster = glTools.utils.skinCluster.findRelatedSkinCluster(surface)
    if not glTools.utils.skinCluster.isSkinCluster(skinCluster):
        raise Exception('Surface "" is not connected to a skinCluster!')

    # Get Influence List
    influenceList = cmds.skinCluster(skinCluster, q=True, inf=True)

    # ==============
    # - Remove Rig -
    # ==============

    cmds.delete(surface, ch=True)
    cmds.delete(influenceList)

    # =================
    # - Return Result -
    # =================

    return skinCluster


def buildRigFromSelection():
    """
    Build basic groom surface scuplting rig based on the current selection.
    """
    # Get Selection
    sel = cmds.ls(sl=1)
    iso = cmds.filterExpand(sel, sm=45)
    if not iso: iso = []
    # Adjust Selection
    sel = list(set(sel) - set(iso))

    # Build Surface Rigs
    for surface in sel:

        # Check Surface
        if glTools.utils.surface.isSurface(surface):
            minU = cmds.getAttr(surface + '.minValueU')
            maxU = cmds.getAttr(surface + '.maxValueU')
            midU = minU + ((maxU - minU) * 0.5)
            buildRig(surface, uValue=midU)

    # Build Isoparm Rigs
    for crv in iso:
        surface = cmds.ls(crv, o=True)[0]
        uValue = float(crv.split('[')[-1].split(']')[0])
        buildRig(surface, uValue)


def removeRigFromSelection():
    """
    Remove the groom surface scuplting rig based on the current selection.
    """
    # Get Selection
    sel = cmds.ls(sl=1)

    # Build Surface Rigs
    for obj in sel:

        # Check Surface
        if glTools.utils.surface.isSurface(obj):
            # Remove Rig
            removeRig(obj)

        # Check Joint
        if glTools.utils.joint.isJoint(obj):

            # Get Connected SkinCluster
            skinConn = cmds.listConnections(obj, type='skinCluster')
            if not skinConn: continue
            skin = skinConn[0]

            # Get Connected Geometry
            surface = glTools.utils.deformer.getAffectedGeometry(skin).keys()[0]

            # Remove Rig
            removeRig(surface)


def groom_checksum(groomNode):
    """
    """
    # Check Groom
    if not cmds.objExists(groomNode):
        raise Exception('Groom node "' + groomNode + '" does not exist!!')

    # Get Groom Curves
    groom_crvs = cmds.ls(cmds.listRelatives(groomNode, ad=True) or [], type='nurbsCurve', ni=True)

    # Build CV Count String
    cvCounts = str([cmds.getAttr(crv + '.controlPoints', s=True) for crv in groom_crvs])

    # Generate Checksum
    m = hashlib.md5()
    m.update(cvCounts)
    hexVal = m.hexdigest()

    # Return Result
    return hexVal
