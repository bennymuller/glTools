import maya.cmds as cmds


def create(switchObject,
           switchAttr,
           switchName='',
           visTargetList=[],
           visEnumList=[],
           visIndexList=[],
           prefix=''):
    """
    Create a enumerated visibility switch based on the input arguments
    @param switchObject: Object to add switch attribute to
    @type switchObject: str
    @param switchAttr: Switch attribute name
    @type switchAttr: str
    @param switchName: Switch attribute nice name for UI.
    @type switchName: str
    @param visTargetList: List of objects lists that will have visibility toggled by the switch attr. ([ [], [], ...])
    @type visTargetList:
    @param visEnumList: List of switch enum lables
    @type visEnumList: list
    @param visIndexList: List of custom indices.
                            The index (value) of the visibility enum attr will be used to look up an index from this list.
                            If empty, visibility enum attr index (value) will be used directly.
    @param prefix: Naming prefix for new nodes
    @type prefix: str
    """
    # ==========
    # - Checks -
    # ==========

    # Check switchObject
    if not cmds.objExists(switchObject):
        raise Exception('Switch object "' + switchObject + '" does not exist!')

    # Compare target and enum list
    if not visTargetList or not visEnumList:
        raise Exception('Visibility target or enum list has zero elements!')
    if len(visTargetList) != len(visEnumList):
        raise Exception('Visibility target and enum list length mis-match!')
    # Check Visibility Index List
    if visIndexList:
        if len(visTargetList) != len(visIndexList):
            raise Exception('Visibility target and index list length mis-match!')

    # =================================
    # - Create Visibility Switch Attr -
    # =================================

    # Check Visibility Switch Attr
    if not cmds.objExists(switchObject + '.' + switchAttr):

        # Build Enum Value
        visEnum = ''
        for i in visEnumList: visEnum += i + ':'
        # Add switch attr
        cmds.addAttr(switchObject, ln=switchAttr, nn=switchName, at='enum', en=visEnum)
        cmds.setAttr(switchObject + '.' + switchAttr, e=True, cb=True)

    # Create Custom Visibility Index (choice)
    vis_choice = ''
    if visIndexList:
        vis_choice = cmds.createNode('choice', n=prefix + '_vis_choice')
        cmds.addAttr(vis_choice, ln='visIndex', at='long', dv=-1, m=True)
        cmds.connectAttr(switchObject + '.' + switchAttr, vis_choice + '.selector', f=True)
        for i in range(len(visIndexList)):
            cmds.setAttr(vis_choice + '.visIndex[' + str(i) + ']', visIndexList[i])
            cmds.connectAttr(vis_choice + '.visIndex[' + str(i) + ']', vis_choice + '.input[' + str(i) + ']', f=True)

    # ======================
    # - Connect Visibility -
    # ======================

    for i in range(len(visEnumList)):

        # Check visTargetList
        if not visTargetList[i]: continue

        # Create Condition Node
        conditionNode = cmds.createNode('condition', n=prefix + '_' + visEnumList[i] + 'Vis_condition')
        cmds.setAttr(conditionNode + '.firstTerm', i)
        cmds.setAttr(conditionNode + '.colorIfTrue', 1, 0, 1)
        cmds.setAttr(conditionNode + '.colorIfFalse', 0, 1, 0)

        # Connect Condition Node
        conditionInput = switchObject + '.' + switchAttr
        if visIndexList: conditionInput = vis_choice + '.output'
        cmds.connectAttr(conditionInput, conditionNode + '.secondTerm', f=True)

        # Connect Each Item in List - Vis ON
        for obj in visTargetList[i]:

            # Check visibility attr
            if not cmds.objExists(obj + '.v'):
                raise Exception('Object "' + obj + '" has no visibility attribute!')
            if not cmds.getAttr(obj + '.v', se=True):
                raise Exception('Attribute "' + obj + '.v" is locked or has incoming connections!')

            # Connect attribute
            cmds.connectAttr(conditionNode + '.outColorR', obj + '.v', f=True)

    # =================
    # - Return Result -
    # =================

    return (switchObject + '.' + switchAttr)


def createEmpty(switchObject,
                switchAttr,
                switchName='',
                visEnumList=[],
                prefix=''):
    """
    Create a enumerated visibility switch based on the input arguments
    @param switchObject: Object to add switch attribute to
    @type switchObject: str
    @param switchAttr: Switch attribute name
    @type switchAttr: str
    @param switchName: Switch attribute nice name for UI.
    @type switchName: str
    @param visEnumList: List of switch enum lables
    @type visEnumList: list
    @param prefix: Naming prefix for new nodes
    @type prefix: str
    """
    # ==========
    # - Checks -
    # ==========

    # Check switchObject
    if not cmds.objExists(switchObject):
        raise Exception('Switch object "' + switchObject + '" does not exist!')

    # =================================
    # - Create Visibility Switch Attr -
    # =================================

    # Check Visibility Switch Attr
    if not cmds.objExists(switchObject + '.' + switchAttr):

        # Build Enum Value
        visEnum = ''
        for i in visEnumList: visEnum += i + ':'
        # Add switch attr
        cmds.addAttr(switchObject, ln=switchAttr, nn=switchName, at='enum', en=visEnum)
        cmds.setAttr(switchObject + '.' + switchAttr, e=True, cb=True)

    # =================
    # - Return Result -
    # =================

    return (switchObject + '.' + switchAttr)
