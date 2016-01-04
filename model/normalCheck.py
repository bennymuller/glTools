import maya.mel as mel
import maya.cmds as cmds
import cleanup


def normalCheck(meshList=[]):
    """
    Setup normal check properties for a specified list of meshes.
    @param meshList: List of meshes to setup normal check for
    @type meshList: list
    """
    # Check Mesh List
    meshList = cleanup.getMeshList(meshList)
    if not meshList: return []

    # Check Normal Shader
    normalSG = 'normalCheckSG'
    normalShader = 'normalCheckShader'
    if not cmds.objExists(normalShader):
        # Create Shader
        normalShader = cmds.shadingNode('lambert', asShader=True, n=normalShader)
        normalSG = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=normalSG)
        cmds.connectAttr(normalShader + '.outColor', normalSG + '.surfaceShader', f=True)
        cmds.setAttr(normalShader + '.color', 0, 0, 0)
        cmds.setAttr(normalShader + '.incandescence', 1, 0, 0)

    # Setup Normal Check
    for mesh in meshList:
        # Clear selection
        cmds.select(cl=True)

        # Turn on double sided
        cmds.setAttr(mesh + '.doubleSided', 1)

        # Extrude face
        numFace = cmds.polyEvaluate(mesh, f=True)
        polyExtrude = cmds.polyExtrudeFacet(mesh + '.f[0:' + str(numFace) + ']', ch=1, kft=True, pvt=(0, 0, 0),
                                          divisions=2, twist=0, taper=1, off=0, smoothingAngle=30)
        mel.eval('PolySelectTraverse 1')
        extrudeFaceList = cmds.filterExpand(ex=True, sm=34)
        cmds.setAttr(polyExtrude[0] + '.localTranslateZ', -0.001)

        # Apply shader
        cmds.sets(extrudeFaceList, fe=normalSG)

    # Set selection
    cmds.select(meshList)

    # Retrun result
    return meshList


def normalCheckRemove(meshList):
    """
    Remove normal check properties for a specified list of meshes.
    @param meshList: List of meshes to removes normal check from
    @type meshList: list
    """
    # Check Mesh List
    meshList = cleanup.getMeshList(meshList)
    if not meshList:
        return []

    # Remove Normal Check
    for mesh in meshList:

        # Clear Selection
        cmds.select(cl=True)

        # Turn Off Double Sided
        cmds.setAttr(mesh + '.doubleSided', 0)

        # Remove Extrude Face
        polyExtrude = cmds.ls(cmds.listHistory(mesh), type='polyExtrudeFace')
        if polyExtrude: cmds.delete(polyExtrude)

        # Delete History
        cmds.delete(mesh, ch=True)

        # Apply Initial Shading Group
        cmds.sets(mesh, fe='initialShadingGroup')

    # Check normalShader members
    normalSG = 'normalCheckSG'
    normalShader = 'normalCheckShader'
    if not cmds.sets(normalSG, q=True): cmds.delete(normalShader, normalSG)

    # Set Selection
    cmds.select(meshList)

    # Retrun Result
    return meshList
