import maya.mel as mel
import maya.cmds as cmds
import glTools.utils.shape
import glTools.utils.reference
import os.path


def getSG(geo):
    """
    Get shading group assigned to specified geometry.
    @param geo: Geometry to get shading group from
    @type geo: str
    """
    # Get Face Sets
    sets = cmds.listSets(extendToShape=True, type=1, object=geo) or []

    # Return Result
    return list(set(sets))


def getMaterial(geo):
    """
    Get shader material assigned to specified geometry.
    @param geo: Geometry to get material from
    @type geo: str
    """
    # Get Material
    mat = cmds.listConnections([SG + '.surfaceShader' for SG in getSG(geo)], s=True, d=False) or []

    # Return Result
    return list(set(mat))


def getRenderNodes():
    """
    List all valid render nodes in scene
    """
    # Get Node Types
    renderTypes = cmds.listNodeTypes('texture')
    renderTypes.extend(cmds.listNodeTypes('utility'))
    renderTypes.extend(cmds.listNodeTypes('imageplane'))
    renderTypes.extend(cmds.listNodeTypes('shader'))

    # Get Nodes by Type
    renderNodes = cmds.ls(long=True, type=renderTypes)
    if not renderNodes: renderNodes = []
    mrRenderNodes = cmds.lsThroughFilter('DefaultMrNodesFilter')
    if not mrRenderNodes: mrRenderNodes = []
    renderNodes.extend(mrRenderNodes)

    # Remove Duplicates
    renderNodes = list(set(renderNodes))

    # Return Result
    return renderNodes


def shadingGroupUnused(shadingGroup):
    """
    Check if the specified shading group is unused
    @param shadingGroup: Shading groupd to test used status of
    @type shadingGroup: str
    """
    # Check Object Exists
    if not cmds.objExists(shadingGroup): return False

    # Check Renderable
    if not cmds.sets(shadingGroup, q=True, renderable=True): return False

    # Ignore Default Types
    if shadingGroup == 'initialShadingGroup': return False
    if shadingGroup == 'initialParticleSE': return False

    # Connection to DAG objects
    objs = cmds.sets(shadingGroup, q=True)
    # Connection to render layers
    layers = cmds.listConnections(shadingGroup, type='renderLayer')

    # Check Membership / Layer attachment
    if not objs and not layers: return True

    # Check to make sure at least one shader is connected to the group
    attrs = ['.surfaceShader',
             '.volumeShader',
             '.displacementShader',
             '.miMaterialShader',
             '.miShadowShader',
             '.miVolumeShader',
             '.miPhotonShader',
             '.miPhotonVolumeShader',
             '.miDisplacementShader',
             '.miEnvironmentShader',
             '.miLightMapShader',
             '.miContourShader']

    # Check Shader Connections
    for attr in attrs:
        if cmds.objExists(shadingGroup + attr):
            if cmds.listConnections(shadingGroup + attr):
                return False

    # Return Result
    return False


def listUnusedShadingNodes(verbose=False):
    """
    List all Unused Shading Nodes
    @param verbose: Print progress messages
    @type verbose: bool
    """
    # List Unused Shading Nodes
    unused = []

    # ==============
    # - Check Sets -
    # ==============

    # Check Unused Sets
    for curr_set in cmds.ls(sets=True):

        # Skip Default Sets
        if curr_set.count('default'):
            continue

        # Check Set is Used
        if shadingGroupUnused(curr_set):
            if verbose: print('Unused shading group: ' + curr_set)
            unused.append(curr_set)

    # ===================
    # - Check Materials -
    # ===================

    # Delete all unconnected materials.
    materials = cmds.ls(long=True, mat=True)

    for currShader in materials:

        # Skip Default Materials
        if currShader.count('default'): continue

        # Skip Defaults
        if currShader == 'lambert1': continue
        if currShader == 'particleCloud1': continue

        shouldDelete = False

        # conn is an array of plug/connection pairs
        conn = cmds.listConnections(currShader, shapes=True, connections=True, source=False)

        # Check Shader Connections
        for j in range(0, len(conn), 2):

            # Check connection to unused shading engine
            se = cmds.listConnections(conn[j], type='shadingEngine')
            if not se:
                se = []
            else:
                if unused.count(se[0]):
                    shouldDelete = True
                    break

            # Check Message Connection
            if conn[j] != (currShader + '.message'):
                shouldDelete = False
                break

            # Third Party Prevent Deletions
            thirdPartyPreventDeletions = cmds.callbacks(currShader, conn[j + 1], conn[j], executeCallbacks=True,
                                                      hook="preventMaterialDeletionFrocmdsleanUpSceneCommand")
            if not thirdPartyPreventDeletions: thirdPartyPreventDeletions = []
            thirdPartyPreventsDeletion = False
            for deletionPrevented in thirdPartyPreventDeletions:
                if (deletionPrevented):
                    thirdPartyPreventsDeletion = True
                    break

            # Check if Used
            if se:
                shouldDelete = False
                break
            elif thirdPartyPreventsDeletion:
                shouldDelete = False
                break
            else:
                shouldDelete = True

        if shouldDelete:
            if verbose: print('Unused shader: ' + currShader)
            unused.append(currShader)

    # =======================
    # - Check Shading Utils -
    # =======================

    # Get All Render Nodes
    allRenderNodes = getRenderNodes()

    for node in allRenderNodes:

        # Skip Default Nodes
        if node.count('default'): continue

        # Skip Defaults
        if node == 'lambert1': continue
        if node == 'particleCloud1': continue

        # Deleting one node can delete other connected nodes.
        if not cmds.objExists(node): continue

        # Check heightField
        if cmds.nodeType(node) == 'heightField':
            conn = cmds.listConnections(node, connections=True, source=True, shapes=True)
            if conn: continue

        # It's a texture, postprocess or utility node. Now determine if the readable connections are done.
        shouldDelete = True

        # Decide whether or not the node is unused
        conn = cmds.listConnections(node, c=True, s=False, shapes=True) or []
        for j in range(0, len(conn), 2):

            # Check Messgae Connection
            if conn[j].count('.message'):
                connType = cmds.nodeType(conn[j + 1])
                connList = ['shadingEngine',
                            'imagePlane',
                            'arrayMapper',
                            'directionalLight',
                            'spotLight',
                            'pointLight',
                            'areaLight',
                            'transform']

                if connList.count(connType):
                    shouldDelete = False

                if cmds.objectType(conn[j + 1], isa='camera') == connType:
                    shouldDelete = False

                # Check Classification
                if shouldDelete and mel.eval('isClassified "' + conn[j + 1] + '" "shader/surface"'):
                    shouldDelete = False
                if shouldDelete and mel.eval('isClassified "' + conn[j + 1] + '" "shader/volume"'):
                    shouldDelete = False
                if shouldDelete and mel.eval('isClassified "' + conn[j + 1] + '" "shader/displacement"'):
                    shouldDelete = False

                # Give plugins a chance to label the node as 'shouldnt be deleted'
                thirdPartyPreventDeletions = cmds.callbacks(node, conn[j + 1], conn[j], executeCallbacks=True,
                                                          hook='preventMaterialDeletionFrocmdsleanUpSceneCommand')
                if not thirdPartyPreventDeletions: thirdPartyPreventDeletions = []
                # thirdPartyPreventDeletions = cmds.callbacks( -executeCallbacks -hook "preventMaterialDeletionFrocmdsleanUpSceneCommand" $node $conn[$j+1] $conn[$j]`;

                for deletionPrevented in thirdPartyPreventDeletions:
                    if deletionPrevented:
                        shouldDelete = False
                        break

                if not shouldDelete: break

            else:
                shouldDelete = False
                break

        if shouldDelete:
            if verbose: print('Unused render node: ' + node)
            unused.append(node)

    # =================
    # - Return Result -
    # =================

    return unused


def applyReferencedShader(geo):
    """
    Fix broken shader assignment in rigs by applying the shader assigned to a referenced intermediate shape, to the final (non-referenced - local) shape.
    Also, breaks placeholder connection to the reference node if needed.
    @param geo: Geometry to fix reference shader assignment for.
    @type geo: str
    """
    # ==========
    # - Checks -
    # ==========

    # Check Geometry
    if not cmds.objExists(geo):
        raise Exception('Geometry "' + geo + '" does not exist!!')

    # Get Shapes
    shapes = glTools.utils.shape.getShapes(geo, nonIntermediates=True, intermediates=False)
    ishapes = glTools.utils.shape.getShapes(geo, nonIntermediates=False, intermediates=True)
    if not shapes: raise Exception('Unable to determine shape node from geometry "' + geo + '"!')
    if not ishapes: raise Exception('Unable to determine intermediate shape node from geometry "' + geo + '"!')

    # Get Referenced Shape
    refShape = ''
    for i in ishapes:
        if glTools.utils.reference.isReferenced(i):
            refShape = i
            break
    if not refShape:
        print('No referenced shape found! Using first intermediate shape ("' + ishapes[0] + '").')
        refShape = ishapes[0]

    # ====================
    # - Reconnect Shader -
    # ====================

    # Get Reference Shader Assignment
    shader = cmds.listConnections(refShape + '.instObjGroups', d=True)
    if not shader:
        raise Exception('Unable to determine shader assignment from intermediate shape node "' + refShape + '"!')

    # Break Placeholder Connections
    breakReferencePlaceholderConnections(shapes[0])

    # Assigned Shader
    cmds.sets(shapes[0], fe=shader[0])

    # =================
    # - Return Result -
    # =================

    return shader[0]


def breakReferencePlaceholderConnections(shape):
    """
    Break all reference placeholder connections to the shape.instObjGroups plug.
    @param shape: Shape to break reference placeholder connections from.
    @type shape: str
    """
    # Get Shape Connections
    placeHolderConn = cmds.listConnections(shape, s=True, d=True, p=True, c=True) or []

    # For Each Connection Pair
    for i in range(0, len(placeHolderConn), 2):

        # Check Reference Connection
        placeHolderNode = cmds.ls(placeHolderConn[i + 1], o=True)[0]
        if glTools.utils.reference.isReference(placeHolderNode):

            # Disconnect PlaceHolder
            if cmds.isConnected(placeHolderConn[i], placeHolderConn[i + 1]):
                try:
                    cmds.disconnectAttr(placeHolderConn[i], placeHolderConn[i + 1])
                except:
                    print('FAILED: ' + placeHolderConn[i] + ' >X< ' + placeHolderConn[i + 1] + '!')
                else:
                    print('Disconnected: ' + placeHolderConn[i] + ' >X< ' + placeHolderConn[i + 1] + '...')
            else:
                try:
                    cmds.disconnectAttr(placeHolderConn[i + 1], placeHolderConn[i])
                except:
                    print('FAILED: ' + placeHolderConn[i + 1] + ' >X< ' + placeHolderConn[i] + '!')
                else:
                    print('Disconnected: ' + placeHolderConn[i + 1] + ' >X< ' + placeHolderConn[i] + '...')


def reconnectShader(geo):
    """
    Force shader reconnection to existing shader.
    Useful when shader connections are broken after deleting redundant groupId nodes.
    @param geo: Geometry to force reconnection to shader for.
    @type geo: str
    """
    # Check Geometry
    if not cmds.objExists(geo):
        raise Exception('Geometry "' + geo + '" does not exist!')

    # Get Shapes
    geoShapes = cmds.listRelatives(geo, s=True, ni=True, pa=True)
    geoAllShapes = cmds.listRelatives(geo, s=True, pa=True)
    if not geoAllShapes:
        raise Exception('No shapes found under geometry "' + geo + '"! Unable to determine shader connections...')

    # Break Reference Placeholder Connections
    for shape in geoAllShapes: breakReferencePlaceholderConnections(shape)

    # Get Shader Connections
    if geoShapes:
        geoShapeConn = cmds.listConnections(geoShapes) or []
        geoShaderConn = cmds.ls(geoShapeConn, type='shadingEngine')
        if geoShaderConn:
            cmds.sets(geo, fe=geoShaderConn[0])
            return geoShaderConn[0]

    # NonIntermediate Shape Shader Connections Failed - Use All Shapes
    geoShapeConn = cmds.listConnections(geoAllShapes) or []
    geoShaderConn = cmds.ls(geoShapeConn, type='shadingEngine')
    if not geoShaderConn:
        raise Exception('No shader connections found for geometry "' + geo + '"!')

    # Reconnect Shader
    cmds.sets(geo, fe=geoShaderConn[0])
    return geoShaderConn[0]


def fixReferenceShaders(refList=None, defaultShader='initialShadingGroup'):
    """
    """
    # Check Reference List
    if not refList: refList = glTools.utils.reference.listReferences()

    # Check Each Reference
    for ref in refList:

        # Initialize Reference Shape List
        shpList = []

        # Check Disconnected Shaders
        c = cmds.listConnections(ref + '.placeHolderList', s=True, d=False, p=True, c=True, sh=True)

        # Check Each Reference Connection
        for i in range(0, len(c), 2):

            # Define Connection Source and Destination
            dst = c[i]
            src = c[i + 1]

            # Check instObjGroups Connections
            if 'instObjGroups' in src:

                # Disconnect placeHolderList Connection
                cmds.disconnectAttr(src, dst)

                # Get Source Shape
                shp = cmds.ls(src, o=True)[0]
                if not shp in shpList:
                    shpList.append(shp)

        # Reconnect to Shader
        if shpList: cmds.sets(shpList, e=True, fe=defaultShader)


def basicTextureShader(texturePath, useFrameExtension=True, prefix=''):
    """
    Create a basic lambert texture shader.
    @param texturePath: File texture path for shader.
    @type texturePath: str
    @param useFrameExtension: Enable frame extension on file texture.
    @type useFrameExtension: bool
    @param prefix: Naming prefix for node names.
    @type prefix: str
    """
    # ==========
    # - Checks -
    # ==========

    # Check Texture Path
    if not os.path.isfile(texturePath):
        raise Exception('Invalid texture path "' + texturePath + '"!!')

    # Prefix
    if not prefix:
        basename = os.path.basename(texturePath)
        prefix = basename.split('.')[0]

    # =====================================
    # - Create Material and Shading Group -
    # =====================================

    # Create material
    mat = cmds.shadingNode('lambert', asShader=True, n=prefix + '_mat')
    sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=prefix + '_SG')
    cmds.connectAttr(mat + '.outColor', sg + '.surfaceShader', f=True)

    # Create File Texture
    fileNode = cmds.shadingNode('file', asTexture=True, n=prefix + '_file')

    # Assign File Path
    cmds.setAttr(fileNode + '.fileTextureName', texturePath, type='string')

    # Create File Placement
    placeNode = cmds.shadingNode('place2dTexture', asUtility=True, n=prefix + '_place2dTexture')
    cmds.connectAttr(placeNode + '.coverage', fileNode + '.coverage', f=True)
    cmds.connectAttr(placeNode + '.translateFrame', fileNode + '.translateFrame', f=True)
    cmds.connectAttr(placeNode + '.rotateFrame', fileNode + '.rotateFrame', f=True)
    cmds.connectAttr(placeNode + '.mirrorU', fileNode + '.mirrorU', f=True)
    cmds.connectAttr(placeNode + '.mirrorV', fileNode + '.mirrorV', f=True)
    cmds.connectAttr(placeNode + '.stagger', fileNode + '.stagger', f=True)
    cmds.connectAttr(placeNode + '.wrapU', fileNode + '.wrapU', f=True)
    cmds.connectAttr(placeNode + '.wrapV', fileNode + '.wrapV', f=True)
    cmds.connectAttr(placeNode + '.repeatUV', fileNode + '.repeatUV', f=True)
    cmds.connectAttr(placeNode + '.offset', fileNode + '.offset', f=True)
    cmds.connectAttr(placeNode + '.rotateUV', fileNode + '.rotateUV', f=True)
    cmds.connectAttr(placeNode + '.noiseUV', fileNode + '.noiseUV', f=True)
    cmds.connectAttr(placeNode + '.vertexUvOne', fileNode + '.vertexUvOne', f=True)
    cmds.connectAttr(placeNode + '.vertexUvTwo', fileNode + '.vertexUvTwo', f=True)
    cmds.connectAttr(placeNode + '.vertexUvThree', fileNode + '.vertexUvThree', f=True)
    cmds.connectAttr(placeNode + '.vertexCameraOne', fileNode + '.vertexCameraOne', f=True)
    cmds.connectAttr(placeNode + '.outUvFilterSize', fileNode + '.uvFilterSize', f=True)
    cmds.connectAttr(placeNode + '.outUV', fileNode + '.uv', f=True)
    cmds.setAttr(placeNode + '.rotateUV', 90)

    # Connect To Shader
    cmds.connectAttr(fileNode + '.outColor', mat + '.color', f=True)

    # Use Frame Extension
    if useFrameExtension: cmds.setAttr(fileNode + '.useFrameExtension', 1)

    # =================
    # - Return Result -
    # =================

    return [sg, mat, fileNode, placeNode]
