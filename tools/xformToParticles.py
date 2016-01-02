import maya.cmds as cmds


def xformToParticles(xformList=[]):
    """
    Create particles from the specified list of transforms
    @param xformList: List of transforms to create particles from
    @type xformList: list
    """
    if not xformList: xformList = cmds.ls(sl=True, type='transform')
    ptList = [cmds.xform(i, q=True, ws=True, rp=True) for i in xformList]
    particle = cmds.particle(p=ptList)
    return particle


def xformToNParticles(xformList=[]):
    """
    Create nParticles from the specified list of transforms
    @param xformList: List of transforms to create nParticles from
    @type xformList: list
    """
    if not xformList: xformList = cmds.ls(sl=True, type='transform')
    ptList = [cmds.xform(i, q=True, ws=True, rp=True) for i in xformList]
    particle = cmds.nParticle(p=ptList)
    return particle


def xformToPoly(xformList=[], scale=0.1):
    """
    Create poly planes from the specified list of transforms
    @param xformList: List of transforms to create poly planes from
    @type xformList: list
    @param scale: Poly plane scale
    @type scale: float
    """
    if not xformList: xformList = cmds.ls(sl=True, type='transform')
    ptList = [cmds.xform(i, q=True, ws=True, rp=True) for i in xformList]
    polyList = []
    for pt in ptList:
        poly = cmds.polyPlane(w=scale, h=scale, sx=1, sy=1, ch=0)[0]
        cmds.move(pt[0], pt[1], pt[2], poly, ws=True)
        polyList.append(poly)
    return polyList
