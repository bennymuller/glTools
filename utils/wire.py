import maya.mel as mel
import maya.cmds as cmds


def isWire(wire):
    """
    Check if specified node is a wire deformer
    @param wrap: Node to check as wire deformer
    @type wrap: str
    """
    # Check Object Exists
    if not cmds.objExists(wire):
        return False
    # Check Object Type
    if not cmds.objectType(wire) == 'wire':
        return False
    # Return Result
    return True


def create(geo, wireCrv, baseCrv=None, dropoffDist=1.0, prefix=''):
    """
    Create a wire deformer using the specified geometry and curves
    @param geo: Geometry to deform
    @type geo: str
    @param wireCrv: Wire deformer curve
    @type wireCrv: str
    @param baseCrv: Wire base curve
    @type baseCrv: str
    @param dropoffDist: Wire influence dropoff distance
    @type dropoffDist: str
    @param prefix: Naming prefix
    @type prefix: str
    """
    # ==========
    # - Checks -
    # ==========

    if baseCrv and not cmds.objExists(baseCrv):
        raise Exception('Base curve "' + baseCrv + '" does not exist!')

    # ===================
    # - Create Deformer -
    # ===================

    # Create Wire
    wire = cmds.wire(geo, w=wireCrv, n=prefix + '_wire')
    wireNode = wire[0]

    # Set Dropoff Distance
    cmds.setAttr(wireNode + '.dropoffDistance[0]', dropoffDist)

    # Connect Custome Base Curve
    if baseCrv:
        oldBase = cmds.listConnections(wireNode + '.baseWire[0]', s=True, d=False)
        cmds.connectAttr(baseCrv + '.worldSpace[0]', wireNode + '.baseWire[0]', f=True)
        if oldBase: cmds.delete(oldBase)

    # =================
    # - Return Result -
    # =================

    return wire


def createMulti(geo, wireList, dropoffDist=1.0, prefix=''):
    """
    Create a wire deformer using the specified geometry and curves
    @param geo: Geometry to deform
    @type geo: str
    @param wireList: Wire deformer curve list
    @type wireList: list
    @param dropoffDist: Wire influence dropoff distance
    @type dropoffDist: str
    @param prefix: Naming prefix
    @type prefix: str
    """
    # ===================
    # - Create Deformer -
    # ===================

    # Create Wire
    wire = cmds.wire(geo, w=wireList, n=prefix + '_wire')
    wireNode = wire[0]

    # Set Dropoff Distance
    for i in range(len(wireList)):
        cmds.setAttr(wireNode + '.dropoffDistance[' + str(i) + ']', dropoffDist)

    # =================
    # - Return Result -
    # =================

    return wire


def getWireCurve(wire):
    """
    Get wire influence (driver) curves
    @param wire: Wire deformer to query
    @type wire: str
    """
    # Check Wire
    if not isWire(wire):
        raise Exception('Object "' + wire + '" is not a valid wire deformer!')

    # Get Wrap Driver
    wireCrv = cmds.listConnections(wire + '.deformedWire', s=True, d=False) or []

    # Return Result
    return wireCrv


def getWireBase(wire):
    """
    Get wire deformer influence base curves
    @param wire: Wire deformer to query
    @type wire: str
    """
    # Check Wire
    if not isWire(wire):
        raise Exception('Object "' + wire + '" is not a valid wire deformer!')

    # Get Wrap Base
    baseCrv = cmds.listConnections(wire + '.baseWire', s=True, d=False) or []

    # Return Result
    return baseCrv
