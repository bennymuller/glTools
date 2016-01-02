import maya.mel as mel
import maya.cmds as cmds
import glTools.utils.mesh
import glTools.utils.blendShape
import glTools.utils.dnpublish


def createSculptBase(rigMesh, baseMesh, prefix='sculpt'):
    """
    """
    # Checks
    if not glTools.utils.mesh.isMesh(rigMesh):
        raise Exception('Invalid mesh! ("' + rigMesh + '")')
    if not glTools.utils.mesh.isMesh(baseMesh):
        raise Exception('Invalid mesh! ("' + baseMesh + '")')

    # Get mesh info
    buffer = 1.1
    meshWidth = buffer * (cmds.getAttr(rigMesh + '.boundingBoxMaxX') - cmds.getAttr(rigMesh + '.boundingBoxMinX'))
    meshHeight = buffer * (cmds.getAttr(rigMesh + '.boundingBoxMaxY') - cmds.getAttr(rigMesh + '.boundingBoxMinY'))

    # ------------------
    # - Dulpicate mesh -
    # ------------------

    # Generate rigBase mesh
    rigBase = cmds.duplicate(rigMesh)[0]
    rigBase = cmds.rename(rigBase, prefix + '_rigBase')
    cmds.parent(rigBase, w=True)
    cmds.move(meshWidth, 0, 0, rigBase, ws=True, a=True)
    # Set display type - Reference
    cmds.setAttr(rigBase + '.overrideEnabled', 1)
    cmds.setAttr(rigBase + '.overrideDisplayType', 2)

    # Generate sculpt mesh
    sculpt = cmds.duplicate(rigMesh)[0]
    sculpt = cmds.rename(sculpt, prefix + '_sculpt')
    cmds.parent(sculpt, w=True)
    cmds.move(meshWidth * 2, 0, 0, sculpt, ws=True, a=True)

    # Generate delta mesh
    delta = cmds.duplicate(baseMesh)[0]
    delta = cmds.rename(delta, prefix + '_delta')
    cmds.parent(delta, w=True)
    cmds.move(meshWidth * 1.5, meshHeight, 0, delta, ws=True, a=True)
    # Set display type - Reference
    cmds.setAttr(delta + '.overrideEnabled', 1)
    cmds.setAttr(delta + '.overrideDisplayType', 2)

    # Generate result mesh
    result = cmds.duplicate(baseMesh)[0]
    result = cmds.rename(result, prefix + '_result')
    cmds.parent(result, w=True)
    cmds.move(meshWidth * 3, 0, 0, result, ws=True, a=True)
    # Set display type - Reference
    cmds.setAttr(result + '.overrideEnabled', 1)
    cmds.setAttr(result + '.overrideDisplayType', 2)

    # --------------------------
    # - Add BlendShape Targets -
    # --------------------------

    # Create delta blendShape
    deltaBlendShape = cmds.blendShape(sculpt, rigBase, delta, n=delta + '_blendShape')[0]
    deltaTarget = cmds.listAttr(deltaBlendShape + '.w', m=True)
    cmds.setAttr(deltaBlendShape + '.' + deltaTarget[0], 1.0)
    cmds.setAttr(deltaBlendShape + '.' + deltaTarget[1], -1.0)

    # Add rig and delta mesh as targets to result mesh
    resultBlendShape = cmds.blendShape(rigMesh, delta, result, n=result + '_blendShape')[0]
    resultTarget = cmds.listAttr(resultBlendShape + '.w', m=True)
    cmds.setAttr(resultBlendShape + '.' + resultTarget[0], 1.0)
    cmds.setAttr(resultBlendShape + '.' + resultTarget[1], 1.0)

    # -----------------
    # - Return Result -
    # -----------------

    return [rigBase, sculpt, delta, result]


def updateSculptBase(rigMesh, baseMesh, prefix='sculpt'):
    """
    """
    # ----------
    # - Checks -
    # ----------

    # RigMesh
    if not glTools.utils.mesh.isMesh(rigMesh):
        raise Exception('Invalid mesh! ("' + rigMesh + '")')

    # BaseMesh
    if not glTools.utils.mesh.isMesh(baseMesh):
        raise Exception('Invalid mesh! ("' + baseMesh + '")')

    # RigBase / Sculpt / Delta
    rigBase = prefix + '_rigBase'
    sculpt = prefix + '_sculpt'
    delta = prefix + '_delta'
    if not glTools.utils.mesh.isMesh(rigBase):
        raise Exception('Invalid mesh! ("' + rigBase + '")')
    if not glTools.utils.mesh.isMesh(sculpt):
        raise Exception('Invalid mesh! ("' + sculpt + '")')
    if not glTools.utils.mesh.isMesh(delta):
        raise Exception('Invalid mesh! ("' + delta + '")')

    # ------------------------
    # - Update Sculpt Shapes -
    # ------------------------

    # Freeze Delta Mesh
    cmds.delete(delta, ch=True)

    # Update rigBase
    rigBaseBlendShape = cmds.blendShape(rigMesh, rigBase)[0]
    rigBaseTarget = cmds.listAttr(rigBaseBlendShape + '.w', m=True)
    cmds.setAttr(rigBaseBlendShape + '.' + rigBaseTarget[0], 1.0)
    cmds.delete(rigBase, ch=True)

    # Update sculpt
    sculptBlendShape = cmds.blendShape(baseMesh, sculpt)[0]
    sculptTarget = cmds.listAttr(sculptBlendShape + '.w', m=True)
    cmds.setAttr(sculptBlendShape + '.' + sculptTarget[0], 1.0)
    cmds.delete(sculpt, ch=True)
    sculptBlendShape = cmds.blendShape(rigBase, delta, sculpt)[0]
    sculptTarget = cmds.listAttr(sculptBlendShape + '.w', m=True)
    cmds.setAttr(sculptBlendShape + '.' + sculptTarget[0], 1.0)
    cmds.setAttr(sculptBlendShape + '.' + sculptTarget[1], 1.0)
    cmds.delete(sculpt, ch=True)

    # Update delta mesh
    deltaBlendShape = cmds.blendShape(baseMesh, delta)[0]
    deltaTarget = cmds.listAttr(deltaBlendShape + '.w', m=True)
    cmds.setAttr(deltaBlendShape + '.' + deltaTarget[0], 1.0)
    cmds.delete(delta, ch=True)
    deltaBlendShape = cmds.blendShape(sculpt, rigBase, delta)[0]
    deltaTarget = cmds.listAttr(deltaBlendShape + '.w', m=True)
    cmds.setAttr(deltaBlendShape + '.' + deltaTarget[0], 1.0)
    cmds.setAttr(deltaBlendShape + '.' + deltaTarget[1], -1.0)

    # -----------------
    # - Return Result -
    # -----------------

    return [rigBase, sculpt, delta]
