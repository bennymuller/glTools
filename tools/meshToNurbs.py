import maya.cmds as cmds
import maya.mel as mel
import glTools.utils.mesh
import glTools.utils.stringUtils


def meshToNurbs(mesh, rebuild=False, spansU=0, spansV=0, prefix=''):
    """
    @param mesh:
    @param rebuild:
    @param spansU:
    @param spansV:
    @param prefix:
    """
    # Check prefix
    if not prefix:
        prefix = glTools.utils.stringUtils.stripSuffix(mesh)

    # Convert poly to subdiv
    subd = cmds.polyToSubdiv(mesh, ch=False, preserveVertexOrdering=True)[0]

    # Full crease corner vertices
    cornerIds = glTools.utils.mesh.getCornerVertexIds(mesh)
    cmds.select([subd + '.vtx[' + str(i) + ']' for i in cornerIds])
    mel.eval('FullCreaseSubdivSurface')

    # Convert subdiv to nurbs
    nurbsConvert = cmds.subdToNurbs(subd, ch=False)[0]
    nurbs = cmds.listRelatives(nurbs, c=True)

    # Cleanup
    cmds.parent(nurbs, w=True)
    cmds.delete(nurbsConvert)
    cmds.delete(subd)

    # Return result
    return nurbs
