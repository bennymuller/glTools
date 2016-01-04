import maya.cmds as cmds
import glTools.utils.attribute
import pymel.core as pm
import re


def isHub(hub):
    """
    Check if node is a valid connection hub node.
    @param hub: Hub node to query.
    @type hub: str
    """
    if not cmds.objExists(hub):
        return False
    if not cmds.objExists(hub + '.connectionHub'):
        return False
    return True


def connectionHubNode(prefix):
    """
    Create empty connection hub node (transform).
    @param prefix: Naming prefix for node
    @type prefix: str
    """
    # Create Hub Node
    hub = cmds.createNode('transform', n=prefix + '_connectionHub')

    # Add Connection Hub Attribute
    cmds.addAttr(hub, ln='connectionHub', dt='string')
    cmds.setAttr(hub + '.connectionHub', prefix, type='string', l=True, k=False)

    # Return Result
    return hub


def addConnection(hub, attr, output=True, connect=True):
    """
    Add an attribute connection entry to the specified hub node.
    @param hub: Connection hub node to add attribute connection to.
    @type hub: str
    @param attr: Attribute to establish connection for.
    @type attr: str
    @param output: Set the connection type. True = output, False = input.
    @type output: bool
    @param connect: Create the connection to the hub node. If False, just create the unconnected hub entry.
    @type connect: bool
    """
    # ==========
    # - Checks -
    # ==========

    if not isHub(hub):
        raise Exception('Object "' + hub + '" is not a valid connection hub node!')

    if not glTools.utils.attribute.isAttr(attr):
        raise Exception('Object "' + attr + '" is not a valid attribute!')

    # ============================
    # - Add Connection Attribute -
    # ============================

    # Determine connection attribute name
    suffix = ''
    if output:
        suffix = 'OUT'
    else:
        suffix = 'IN'

    connectionAttr = re.sub('\.', '__', attr) + suffix

    # Add Attribute
    cmds.addAttr(hub, ln=connectionAttr, k=True)

    # =====================
    # - Connect Attribute -
    # =====================

    if connect:

        if output:
            # Connect Output
            cmds.connectAttr(attr, hub + '.' + connectionAttr, f=True)
        else:
            # Get Input Value
            inputVal = cmds.getAttr(attr)
            cmds.setAttr(hub + '.' + connectionAttr, inputVal)
            # Connect Input
            cmds.setAttr(attr, l=False)
            cmds.connectAttr(hub + '.' + connectionAttr, attr, f=True)

    # =================
    # - Return Result -
    # =================

    return hub + '.' + connectionAttr


def connect(hub):
    """
    @param hub: First hub in connection pair.
    @type hub: str
    """
    # Get Hub Attributes
    for hubAttr in pm.PyNode(hub).listAttr(ud=True):

        # Get Attribute Name Components
        inout, node, nodeAttr = hubAttr.attrName().split('__')
        try:
            if inout == 'OUT':
                # Connect OUTput
                hubAttr >> pm.PyNode(node).attr(nodeAttr)
            elif inout == 'IN':
                # Connect INput
                pm.PyNode(node).attr(nodeAttr) >> hubAttr
        except:
            pass


def connectToHub(hub1, hub2):
    """
    Connect a pair of specified connection hubs.
    @param hub1: First hub in connection pair.
    @type hub1: str
    @param hub2: Second hub in connection pair.
    @type hub2: str
    """
    # ==========
    # - Checks -
    # ==========

    if not isHub(hub1):
        raise Exception('Object "' + hub1 + '" is not a valid connection hub node!')
    if not isHub(hub2):
        raise Exception('Object "' + hub2 + '" is not a valid connection hub node!')

    # ===========
    # - Connect -
    # ===========

    # Get connection attribute lists
    hub1_attrs = cmds.listAttr(hub1, ud=True, k=True)
    hub2_attrs = cmds.listAttr(hub2, ud=True, k=True)

    # Connect HUB1 >>> HUB2
    for attr in hub1_attrs:

        # Check Output
        if attr.endswith('OUT'):

            # Get connection source/destination attributes
            srcAttr = hub1 + '.' + attr
            dstAttr = hub2 + '.' + attr.replace('OUT', 'IN')
            # Check destination attribute
            if not glTools.utils.attribute.isAttr(dstAttr):
                raise Exception('Destination attribute "' + dstAttr + '" does not exist!')

            # Connect
            print('Connecting hub attributes:')
            print('\t' + srcAttr + ' >>> ' + dstAttr)
            cmds.connectAttr(srcAttr, dstAttr, f=True)

    # Connect HUB2 >>> HUB1
    for attr in hub2_attrs:

        # Check Output
        if attr.endswith('OUT'):

            # Get connection source/destination attributes
            srcAttr = hub2 + '.' + attr
            dstAttr = hub1 + '.' + attr.replace('OUT', 'IN')
            # Check destination attribute
            if not glTools.utils.attribute.isAttr(dstAttr):
                raise Exception('Destination attribute "' + dstAttr + '" does not exist!')

            # Connect
            print('Connecting hub attributes:')
            print('\t' + srcAttr + ' >>> ' + dstAttr)
            cmds.connectAttr(srcAttr, dstAttr, f=True)

    # =================
    # - Return Result -
    # =================

    print('Successfully Connected Hubs: ["' + hub1 + '" << >> "' + hub2 + '"]')


def connectCopy(hub):
    """
    @param hub: First hub
    @type hub: str
    """
    # ==========
    # - Checks -
    # ==========

    if not isHub(hub):
        raise Exception('Object "' + hub + '" is not a valid connection hub node!')
