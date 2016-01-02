import maya.mel as mel
import maya.cmds as cmds
import glTools.data.skinClusterData
import glTools.tools.copyPasteWeights
import glTools.utils.component
import glTools.utils.selection
import glTools.utils.skinCluster
import copy


def loadWorldSpaceData(geo='', search='', replace=''):
    """
    """
    # Load Data
    skinData = SkinClusterData().load()

    # Check Geometry
    if not geo:

        # Check Search/Replace
        if not search or (not search and not replace):

            # Get Geometry from Selection
            sel = cmds.ls(sl=True)
            if not sel:
                print('No target geometry specified! Unable to load skinCluster data...')
                return
            geo = sel[0]

        else:

            # Search and Replace Name of Affected Geometry
            affectedGeo = skinData._data['affectedGeometry'][0]
            if not search in affectedGeo:
                print(
                'Search string "' + search + '" not found in original affected geometry name "' + affectedGeo + '"! Unable to load skinCluster data...')
                return
            geo = affectedGeo.replace(search, replace)

    # Rebuild SkinCluster Data
    skinData.rebuildWorldSpaceData(targetGeo=geo)
    skinData.rebuild()


def loadWorldSpaceDataUI():
    """
    """
    window = 'loadSkinClusterWorldSpaceUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Load SkinCluster Data (World Space)')

    # Layout
    cl = cmds.columnLayout()

    # UI Elements
    targetGeoTFB = cmds.textFieldButtonGrp('loadSkinData_targetGeoTFB', label='Target Geometry', text='',
                                         buttonLabel='Load Selected')
    searchStrTFG = cmds.textFieldGrp('loadSkinData_searchStrTFB', label='Search', text='')
    replaceStrTFG = cmds.textFieldGrp('loadSkinData_replaceStrTFB', label='Replace', text='')
    loadB = cmds.button('loadSkinData_loadDataB', l='Load', c='glTools.tools.skinCluster.loadWorldSpaceDataFromUI()')
    cancelB = cmds.button('loadSkinData_cancelB', l='Cancel', c='cmds.deleteUI("' + window + '")')

    # UI callback commands
    cmds.textFieldButtonGrp(targetGeoTFB, e=True,
                          bc='glTools.ui.utils.loadTypeSel("' + targetGeoTFB + '",selType="transform")')


def loadWorldSpaceDataFromUI():
    """
    """
    # Check Window
    window = 'loadSkinClusterWorldSpaceUI'
    if not cmds.window(window, q=True, ex=1): return

    # Get UI data
    targetGeo = cmds.textFieldButtonGrp('loadSkinData_targetGeoTFB', q=True, text=True)
    searchStr = cmds.textFieldButtonGrp('loadSkinData_searchStrTFB', q=True, text=True)
    replaceStr = cmds.textFieldButtonGrp('loadSkinData_replaceStrTFB', q=True, text=True)

    # Load SkinCluster Data
    loadWorldSpaceData(geo=targetGeo, search=searchStr, replace=replaceStr)


def copyToMany(sourceGeo, targetGeoList):
    """
    """
    # ==========
    # - Checks -
    # ==========

    if not cmds.objExists(sourceGeo):
        raise Exception('Source geometry "' + sourceGeo + '" does not exist!')
    if not targetGeoList:
        raise Exception('Invalid target geometry list!')

    # ==========================
    # - Get Source SkinCluster -
    # ==========================

    srcSkin = glTools.utils.skinCluster.findRelatedSkinCluster(sourceGeo)
    skinData = glTools.data.skinClusterData.SkinClusterData(srcSkin)

    # =======================
    # - Transfer to Targets -
    # =======================

    for targetGeo in targetGeoList:
        # Copy Source SkinCluster
        xferData = copy.deepcopy(skinData)

        # Remap Geometry
        xferData.remapGeometry(targetGeo)
        xferData.rebuildWorldSpaceData(targetGeo)

        # Rebuild SkinCluster
        xferData.rebuild()


def skinInsideFaces(insideFaceList):
    """
    Copy skinCluster weights to inside faces from the outside faces of the same mesh.
    insideFaceList
    @param insideFaceList: List of inside faces to copy skinWeights to.
    @type insideFaceList: list
    """
    # Get Component List By Object
    objFaceList = glTools.utils.selection.componentListByObject(insideFaceList)

    # For Each
    for objFaces in objFaceList:

        # Get Source Mesh
        mesh = cmds.ls(objFaces[0], o=True)[0]

        # Get Face ID List
        faceIds = glTools.utils.component.getSingleIndexComponentList(objFaces)
        faceIds = faceIds[faceIds.keys()[0]]

        # Duplicate Original Mesh
        mesh_dup = cmds.duplicate(mesh)[0]
        mesh_dup_children = cmds.ls(cmds.listRelatives(mesh_dup, c=True), transforms=True)
        if mesh_dup_children: cmds.delete(mesh_dup_children)

        # Extract Faces from Duplicate
        faces = [mesh_dup + '.f[' + str(i) + ']' for i in faceIds]
        extract = cmds.polyChipOff(faces, dup=False, ch=False)
        separate = cmds.polySeparate(mesh_dup, ch=False)

        # Transfer Weights to Extracted Mesh
        copyToMany(mesh, [separate[0]])
        copyToMany(separate[0], [separate[1]])

        # Transfer Weights from Extracted Mesh
        srcSkin = glTools.utils.skinCluster.findRelatedSkinCluster(separate[1])
        skinData = glTools.data.skinClusterData.SkinClusterData(srcSkin)
        skinData.remapGeometry(mesh)
        skinData.rebuildWorldSpaceData(mesh)

        # Apply Transferred Weights
        vtxList = cmds.polyListComponentConversion(objFaces, fromFace=True, toVertex=True, internal=False)
        skinData.loadWeights(componentList=vtxList)

        # Clean Up
        cmds.delete(mesh_dup)


def edgeLoopWeights(edgeList):
    """
    """
    # Check Edge List
    if not edgeList: raise Exception('Invalid or empty edge list!')
    edgeList = cmds.filterExpand(edgeList, ex=True, sm=32) or []
    if not edgeList: raise Exception('Invalid edge list! List of polygon edges required...')

    # Get Mesh from Edges
    mesh = list(set(cmds.ls(edgeList, o=True) or []))
    if len(mesh) > 1:
        raise Exception('Edges from multiple mesh shapes were supplied! ' + str(mesh))
    mesh = mesh[0]

    for edge in edgeList:
        # Get Edge ID
        edgeID = glTools.utils.component.index(edge)

        # Get Vertices from Edge
        edgeVerts = cmds.polyListComponentConversion(edge, fe=True, tv=True)

        # Get Average Vertex Weights
        cmds.select(edgeVerts)
        glTools.tools.copyPasteWeights.averageWeights()

        # Select Edge Loop Vertices
        cmds.polySelect(mesh, edgeLoop=edgeID)
        loopEdges = cmds.ls(sl=1, fl=1)
        loopVerts = cmds.polyListComponentConversion(loopEdges, fe=True, tv=True)
        cmds.select(loopVerts)
        glTools.tools.copyPasteWeights.pasteWeights()

    # Return Result
    return mesh
