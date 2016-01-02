import maya.cmds as cmds
import maya.mel as mel
import os.path
import glTools.utils.namespace


def loadAbcImportPlugin():
    """
    Load AbcImport plugin
    """
    # Load AbcImport plugin
    if not cmds.pluginInfo('AbcImport', q=True, l=True):
        try:
            cmds.loadPlugin('AbcImport', quiet=True)
        except:
            raise Exception('Error loading AbcImport plugin!')


def loadAbcExportPlugin():
    """
    Load AbcExport plugin
    """
    # Load AbcExport plugin
    if not cmds.pluginInfo('AbcExport', q=True, l=True):
        try:
            cmds.loadPlugin('AbcExport', quiet=True)
        except:
            raise Exception('Error loading AbcExport plugin!')


def loadGpuCachePlugin():
    """
    Load gpuCache plugin
    """
    # Load gpuCache plugin
    if not cmds.pluginInfo('gpuCache', q=True, l=True):
        try:
            cmds.loadPlugin('gpuCache', quiet=True)
        except:
            raise Exception('Error loading gpuCache plugin!')


def loadIkaGpuCachePlugin():
    """
    Load glGpuCache plugin
    """
    # Load glGpuCache plugin
    if not cmds.pluginInfo('glGpuCache', q=True, l=True):
        try:
            cmds.loadPlugin('glGpuCache', quiet=True)
        except:
            raise Exception('Error loading glGpuCache plugin!')


def isAlembicNode(cacheNode):
    """
    Check if the specified node is a valid Alembic cache node
    @param cacheNode: Object to query
    @type cacheNode: str
    """
    # Check object exists
    if not cmds.objExists(cacheNode): return False

    # Check node type
    if cmds.objectType(cacheNode) != 'AlembicNode': return False

    # Return result
    return True


def isGpuCacheNode(gpuCacheNode):
    """
    Check if the specified node is a valid GPU cache node
    @param gpuCacheNode: Object to query
    @type gpuCacheNode: str
    """
    # Check object exists
    if not cmds.objExists(gpuCacheNode): return False

    # Check node type
    if cmds.objectType(gpuCacheNode) != 'gpuCache': return False

    # Return result
    return True


def isIkaGpuCacheNode(glGpuCacheNode):
    """
    Check if the specified node is a valid gl GPU cache node
    @param glGpuCacheNode: Object to query
    @type glGpuCacheNode: str
    """
    # Check object exists
    if not cmds.objExists(glGpuCacheNode): return False

    # Check node type
    if cmds.objectType(glGpuCacheNode) != 'glGpuCache': return False

    # Return result
    return True


def disconnectTime(cache):
    """
    Disconnect the time attribute for the given cache node
    @param cache: Cache node to disconnect time from
    @type cache: str
    """
    # Get existing connections
    timeConn = cmds.listConnections(cache + '.time', s=True, d=False, p=True)
    if not timeConn: return

    # Disconnect time plug
    cmds.disconnectAttr(timeConn[0], cache + '.time')


def connectTime(cache, timeAttr='time1.outTime'):
    """
    Connect a specified driver attribute to the time inout for a named cache node
    @param cache: Cache node to connect to
    @type cache: str
    @param timeAttr: Attribute to drive the cache nodes time value
    @type timeAttr: str
    """
    # Check time attribute
    if not cmds.objExists(timeAttr):
        raise Exception('Time attribute "' + timeAttr + '" does not exist!')

    # Disconnect time plug
    cmds.connectAttr(timeAttr, cache + '.time', f=True)


def importcmdsCache(geo, cacheFile):
    """
    Import and connect geometry cache file to the specified geometry
    @param geo: Geometry to load cache to
    @type geo: str
    @param cacheFile: Geometry cache file path to load
    @type cacheFile: str
    """
    # Check geo
    if not cmds.objExists(geo): raise Exception('Geometry "" does not exist!')

    # Check file
    if not os.path.isfile(cacheFile): raise Exception('Cache file "' + cacheFile + '" does not exist!')

    # Load cache
    mel.eval('doImportCacheFile "' + cacheFile + '" "" {"' + geo + '"} {}')


def importcmdsCacheList(geoList, cachePath, cacheFileList=[]):
    """
    Import and connect geometry cache files from a specified path to the input geometry list
    @param geoList: List of geometry to load cache onto
    @type geoList: list
    @param cachePath: Directory path to load cache files from
    @type cachePath: str
    @param cacheFileList: List of cacheFiles to load. If empty, use geometry shape names. Optional.
    @type cacheFileList: list
    """
    # Check source directory path
    if not os.path.isdir(cachePath):
        raise Exception('Cache path "' + cachePath + '" does not exist!')
    if not cachePath.endswith('/'): cachePath = cachePath + '/'

    # Check cacheFile list
    if cacheFileList and not (len(cacheFileList) == len(geoList)):
        raise Exception('Cache file and geometry list mis-match!')

    # For each geometry in list
    for i in range(len(geoList)):

        # Check geo
        if not cmds.objExists(geoList[i]):
            raise Exception('Geometry "' + geoList[i] + '" does not exist!')

        # Determine cache file
        if cacheFileList:
            cacheFile = cacheFile = cachePath + cacheFileList[i] + '.cmds'
        else:
            # Get geometry shape
            shapeList = cmds.listRelatives(geoList[i], s=True, ni=True, pa=True)
            if not shapeList: raise Exception('No valid shape found for geometry!')
            geoShape = shapeList[0]
            cacheFile = cachePath + geoShape + '.cmds'

        # Check file
        if not os.path.isfile(cacheFile):
            raise Exception('Cache file "' + cacheFile + '" does not exist!')

        # Import cache
        importcmdsCache(geoList[i], cacheFile)


def exportcmdsCache(geo, cacheFile, startFrame=1, endFrame=100, useTimeline=True, filePerFrame=False, cachePerGeo=True,
                  forceExport=False):
    """
    @param geo: List of geometry to cache
    @type geo: list
    @param cacheFile: Output file name
    @type cacheFile: str
    @param startFrame: Start frame for cache output
    @type startFrame: int
    @param endFrame: End frame for cache output
    @type endFrame: int
    @param useTimeline: Get start and end from from the timeline
    @type useTimeline: bool
    @param filePerFrame: Write file per frame or single file
    @type filePerFrame: bool
    @param cachePerGeo: Write file per shape or single file
    @type cachePerGeo: bool
    @param forceExport: Force export even if it overwrites existing files
    @type forceExport: bool
    """
    # Constant value args
    version = 5  # 2010
    refresh = 1  # Refresh during caching
    usePrefix = 0  # Name as prefix
    cacheAction = 'export'  # Cache action "add", "replace", "merge", "mergeDelete" or "export"
    simRate = 1  # Sim frame rate (steps per frame - ?)

    # Frame range
    if useTimeline:
        startFrame = cmds.playbackOptions(q=True, ast=True)
        endFrame = cmds.playbackOptions(q=True, aet=True)

    # Cache file distribution
    if filePerFrame:
        cacheDist = 'OneFilePerFrame'
    else:
        cacheDist = 'OneFile'

    # Determine destination directory and file
    fileName = cacheFile.split('/')[-1]
    cacheDir = cacheFile.replace(fileName, '')
    baseName = fileName.replace('.' + fileName.split('.')[-1], '')

    # Export cache
    cmds.select(geo)
    mel.eval('doCreateGeometryCache ' + str(version) + ' {"0","' + str(startFrame) + '","' + str(
        endFrame) + '","' + cacheDist + '","' + str(refresh) + '","' + cacheDir + '","' + str(
        int(cachePerGeo)) + '","' + baseName + '","' + str(usePrefix) + '","' + cacheAction + '","' + str(
        int(forceExport)) + '","1","1","0","0","cmdsc" };')


def importGpuCache(cachePath, cacheName='', namespace=''):
    """
    Import GPU Alembic cache from file
    @param cachePath: Alembic cache file path
    @type cachePath: str
    @param cacheName: Alembic cache name. If empty, use filename.
    @type cacheName: str
    """
    # =========
    # - Check -
    # =========

    # Load Import Plugin
    loadAbcImportPlugin()

    # Check Cache Path
    if not os.path.isfile(cachePath):
        raise Exception('Cache path "' + cachePath + '" is not a valid file!')

    # Check Cache Name
    if not cacheName:
        cacheBase = os.path.basename(cachePath)
        cacheName = os.path.splitext(cacheBase)[-1]

    # Check Namespace
    if namespace:
        if cmds.namespace(ex=namespace):
            NSind = 1
            while (cmds.namespace(ex=namespace + str(NSind))):
                NSind += 1
            namespace = namespace + str(NSind)

    # ==============
    # - Load Cache -
    # ==============

    # Create Cache Node
    cacheNode = cmds.createNode('gpuCache', name=cacheName + 'Cache')
    cacheParent = cmds.listRelatives(cacheNode, p=True, pa=True)
    cacheParent = cmds.rename(cacheParent, cacheName)

    # Set Cache Path
    cmds.setAttr(cacheNode + '.cacheFileName', cachePath, type='string')

    # ===================
    # - Apply Namespace -
    # ===================

    if namespace:

        # Create Namespace (if necessary)
        if not cmds.namespace(ex=namespace): cmds.namespace(add=namespace)
        # Apply Namespace
        cacheParent = cmds.rename(cacheParent, namespace + ':' + cacheParent)
        # Update cacheNode
        cacheNode = cmds.listRelatives(cacheParent, s=True, pa=True)[0]

    # =================
    # - Return Result -
    # =================

    return cacheParent


def importAbcCache(cachePath='', cacheName='', namespace='', parent='', mode='import', debug=False):
    """
    Import Alembic cache from file
    @param cachePath: Alembic cache file path
    @type cachePath: str
    @param cacheName: Alembic cache name. If empty, use filename.
    @type cacheName: str
    @param namespace: Namespace for cache.
    @type namespace: str
    @param parent: Reparent the whole hierarchy under an existing node in the current scene.
    @type parent: str
    @param mode: Import mode. "import", "open" or "replace".
    @type mode: str
    @param debug: Turn on debug message printout.
    @type debug: bool
    """
    # ==========
    # - Checks -
    # ==========

    # Load Import Plugin
    loadAbcImportPlugin()

    # Check Cache Path
    if not os.path.isfile(cachePath):
        raise Exception('Cache path "' + cachePath + '" is not a valid file!')

    # Check Cache Name
    if not cacheName:
        cacheBase = os.path.basename(cachePath)
        cacheName = os.path.splitext(cacheBase)[-1]

    # Check Namespace
    if namespace:
        if cmds.namespace(ex=namespace):
            NSind = 1
            while (cmds.namespace(ex=namespace + str(NSind))):
                NSind += 1
            namespace = namespace + str(NSind)

    # ==============
    # - Load Cache -
    # ==============

    cacheNode = cmds.AbcImport(cachePath, mode=mode, debug=debug)
    cacheNode = cmds.rename(cacheNode, cacheName + 'Cache')

    # Get Cache Nodes
    cacheList = cmds.listConnections(cacheNode, s=False, d=True)

    # Get Cache Roots
    rootList = []
    for cacheItem in cacheList:
        root = cacheItem
        while cmds.listRelatives(root, p=True) != None:
            root = cmds.listRelatives(root, p=True, pa=True)[0]
        if not rootList.count(root):
            rootList.append(root)

    # Add to Namespace
    if namespace:
        for root in rootList:
            glTools.utils.namespace.addHierarchyToNS(root, namespace)

    # Parent
    if parent:

        # Check Parent Transform
        if not cmds.objExists(parent):
            parent = cmds.group(em=True, n=parent)

        # Parent
        cmds.parent(rootList, parent)

    # =================
    # - Return Result -
    # =================

    return cacheNode


def loadAbcFromGpuCache(gpuCacheNode, debug=False):
    """
    Load Alembic cache from a specified gpuCache node.
    @param gpuCacheNode: GPU cache node to replace with alembic cache.
    @type gpuCacheNode: str
    @param debug: Print debug info to script editor
    @type debug: bool
    """
    # =========
    # - Check -
    # =========

    # Load Import Plugin
    loadAbcImportPlugin()

    # Check GPU  Cache Node
    if not isGpuCacheNode(gpuCacheNode):
        raise Exception('Object "' + gpuCacheNode + '" is not a valid GPU Cache Node!')

    # =====================
    # - Get Cache Details -
    # =====================

    cachePath = cmds.getAttr(gpuCacheNode + '.cacheFileName')

    # Get Cache Node Transform and Parent
    cacheXform = cmds.listRelatives(gpuCacheNode, p=True, pa=True)[0]
    cacheParent = cmds.listRelatives(cacheXform, p=True, pa=True)
    if not cacheParent: cacheParent = ''

    # Get Cache Namespace
    cacheNS = glTools.utils.namespace.getNS(gpuCacheNode)

    # Get Cache Name
    cacheName = gpuCacheNode
    if gpuCacheNode.count('Cache'):
        cacheName = gpuCacheNode.replace('Cache', '')

    # Delete GPU Cache
    cmds.delete(cacheXform)

    # ======================
    # - Load Alembic Cache -
    # ======================

    cacheNode = importAbcCache(cachePath, cacheName=cacheName, namespace=cacheNS, parent=cacheParent, mode='import',
                               debug=debug)
    # cacheXform = cmds.listRelatives(cacheNode,p=True,pa=True)[0]

    # Parent Cache
    #
    if cacheParent: cmds.parent(cacheXform, cacheParent)

    # =================
    # - Return Result -
    # =================

    return cacheNode


def abcTimeOffset(offsetNode, offsetAttr='alembicTimeOffset', cacheList=[]):
    """
    Setup a time offset attribute to control the incoming time value for the specified cache nodes.
    @param offsetNode: Node that will hold the time offset attribute
    @type offsetNode: str
    @param offsetAttr: Time offset attribute name.
    @type offsetAttr: str
    @param cacheList: List of cache nodes to connect to time offset.
    @type cacheList: list
    """
    # =========
    # - Check -
    # =========

    # Check Cache List
    if not cacheList: return ''

    # Check offsetNode
    if not cmds.objExists(offsetNode):
        raise Exception('Offset node "' + offsetNode + '" does not exist!')

    # Check offsetAttr
    if not offsetAttr: offsetAttr = 'alembicTimeOffset'

    # ========================
    # - Add Offset Attribute -
    # ========================

    if not cmds.objExists(offsetNode + '.' + offsetAttr):
        cmds.addAttr(offsetNode, ln=offsetAttr, at='long', dv=0, k=True)

    # =======================
    # - Connect Time Offset -
    # =======================

    for cache in cacheList:

        # Get Current Time Connection
        timeConn = cmds.listConnections(cache + '.time', s=True, d=False, p=True)
        if not timeConn: timeConn = ['time1.outTime']

        # Offset Node
        addNode = cmds.createNode('addDoubleLinear', n=cache + '_abcOffset_addDoubleLinear')

        # Connect to Offset Time
        cmds.connectAttr(timeConn[0], addNode + '.input1', f=True)
        cmds.connectAttr(offsetNode + '.' + offsetAttr, addNode + '.input2', f=True)
        cmds.connectAttr(addNode + '.output', cache + '.time', f=True)

    # =================
    # - Return Result -
    # =================

    return offsetNode + '.' + offsetAttr
