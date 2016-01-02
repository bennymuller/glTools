import maya.mel as mel
import maya.cmds as cmds
import glTools.utils.attribute
import glTools.utils.connection


def isWrap(wrap):
    """
    Check if specified node is a wrap deformer
    @param wrap: Node to check as wrap deformer
    @type wrap: str
    """
    # Check Object Exists
    if not cmds.objExists(wrap): return False
    # Check Object Type
    if not cmds.objectType(wrap) == 'wrap': return False
    # Return Result
    return True


def create(geo, wrapGeo, worldSpace=True, prefix=''):
    """
    Create a wrap deformer using the specified geometry
    @param geo: Geometry to deform
    @type geo: str
    @param wrapGeo: Wrap deformer influence geometry
    @type wrapGeo: str
    @param prefix: Naming prefix
    @type prefix: str
    """
    # Build/Store Selection
    sel = cmds.ls(sl=1)
    cmds.select(geo, wrapGeo)

    # Create Wrap Deformer
    mel.eval('CreateWrap')
    wrap = cmds.ls(cmds.listHistory(geo), type='wrap')[0]
    wrap = cmds.rename(wrap, prefix + '_wrap')

    # World/Local Space Deformation
    if not worldSpace:
        geomMatrixInput = cmds.listConnections(wrap + '.geomMatrix', s=True, d=False, p=True)
        if geomMatrixInput: cmds.disconnectAttr(geomMatrixInput[0], wrap + '.geomMatrix')

    # Clean Base
    cleanWrapBase(wrap)

    # Restore Selection
    if sel: cmds.select(sel)

    # Return Result
    return wrap


def addInfluence(geo, wrapInf):
    """
    Add a new wrap deformer influence for the specified geometry
    @param geo: Geometry to deform
    @type geo: str
    @param wrapInf: Wrap deformer influence geometry
    @type wrapInf: str
    """
    # Build/Store Selection
    sel = cmds.ls(sl=1)
    cmds.select(geo, wrapInf)

    # Add Wrap Influence
    mel.eval('AddWrapInfluence')
    wrap = cmds.ls(cmds.listHistory(geo), type='wrap')[0]

    # Clean Base
    cleanWrapBase(wrap)

    # Restore Selection
    if sel: cmds.select(sel)

    # Return Result
    return wrap


def getWrapDriver(wrap):
    """
    Get wrap deformer influence (driver) mesh
    @param wrap: Wrap deformer to query
    @type wrap: str
    """
    # Check Wrap
    if not isWrap(wrap):
        raise Exception('Object "' + wrap + '" is not a valid wrap deformer!')

    # Get Wrap Driver
    driver = cmds.listConnections(wrap + '.driverPoints', s=True, d=False)
    if not driver: driver = []

    # Return Result
    return driver


def getWrapBase(wrap):
    """
    Get wrap deformer influence base mesh
    @param wrap: Wrap deformer to query
    @type wrap: str
    """
    # Check Wrap
    if not isWrap(wrap):
        raise Exception('Object "' + wrap + '" is not a valid wrap deformer!')

    # Get Wrap Base
    base = cmds.listConnections(wrap + '.basePoints', s=True, d=False)
    if not base: base = []

    # Return Result
    return base


def getDriverIndex(wrap, driver):
    """
    """
    # Check Wrap
    if not isWrap(wrap):
        raise Exception('Object "' + wrap + '" is not a valid wrap deformer!')

    # Check Driver
    if not driver in getWrapDriver(wrap):
        raise Exception('Object "' + driver + '" is not a valid driver for wrap deformer "' + wrap + '"!')

    # Get Driver Connections
    driverConn = glTools.utils.connection.connectionListToAttr(wrap, 'driverPoints')
    for driverShape in driverConn:
        driverShapeParent = cmds.listRelatives(driverShape, p=True)[0]
        if driverShapeParent == driver:
            return driverConn[driverShape][1]

    # Return NULL Result
    return None


def getBaseIndex(wrap, base):
    """
    """
    # Check Wrap
    if not isWrap(wrap):
        raise Exception('Object "' + wrap + '" is not a valid wrap deformer!')

    # Check Driver
    if not base in getWrapBase(wrap):
        raise Exception('Object "' + base + '" is not a valid base for wrap deformer "' + wrap + '"!')

    # Get Base Connections
    baseConn = glTools.utils.connection.connectionListToAttr(wrap, 'basePoints')
    for baseShape in baseConn:
        baseShapeParent = cmds.listRelatives(baseShape, p=True)[0]
        if baseShapeParent == base:
            return baseConn[baseShape][1]

    # Return NULL Result
    return None


def cleanWrapBase(wrap):
    """
    Clean wrap base geometry to remove unused shapes and attributes.
    @param wrap: Wrap deformer to clean base geometry for
    @type wrap: str
    """
    # Get Wrap Base Geometry
    base = getWrapBase(wrap)

    # Remove Unused Shapes
    baseShapes = cmds.listRelatives(base, s=True, pa=True)
    wrapShapes = cmds.listConnections(wrap + '.basePoints', s=True, d=False, sh=True)
    for shape in baseShapes:
        if not shape in wrapShapes:
            cmds.delete(shape)

    # Remove Unused Attributes
    for baseObj in base: glTools.utils.attribute.deleteUserAttrs(baseObj)
    for shape in wrapShapes: glTools.utils.attribute.deleteUserAttrs(shape)
