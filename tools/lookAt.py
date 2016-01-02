import maya.mel as mel
import maya.cmds as cmds
import glTools.tools.constraint
import glTools.utils.transform


def create(target,
           slaveList,
           slaveAimUp=None,
           weightList=None,
           bakeAnim=False,
           bakeStartEnd=[None, None],
           offsetAnim=None,
           offset=(0, 0, 0),
           cleanup=False):
    """
    Create a lookAt constraint setup based in the input arguments
    @param target: LookAt target transform.
    @type target: str
    @param slaveList: LookAt slave transform list.
    @type slaveList: list
    @param slaveAimUp: List of slave lookAt aim and up vectors. [(aim,up),('z',x),...]
    @type slaveAimUp: list
    @param weightList: LookAt weight list. If None, use default weight list (evenly distributed).
    @type weightList: list
    @param bakeAnim: Bake lookAt animation to controls.
    @type bakeAnim: bool
    @param bakeStartEnd: Tuple containing start and end frame value.
    @type bakeStartEnd: tuple
    @param offsetAnim: Offset baked lookAt animation.
    @type offsetAnim: float or None
    @param offset: Constraint offset.
    @type offset: tuple
    """
    # ==========
    # - Checks -
    # ==========

    # Target
    if not glTools.utils.transform.isTransform(target):
        raise Exception('LookAt target "' + target + '" is not a valid transform! Unable to create lookAt setup...')

    # Slave List
    if not slaveList:
        raise Exception('Invalid lookAt slave list! Unable to create lookAt setup...')

    # Weight List
    if not weightList:
        print('Invalid lookAt weight list! Generating default lookAt weight list...')
        weightList = range(0, 101, 100.0 / len(slaveList))[1:]
    if len(weightList) != len(slaveList):
        print('Invalid lookAt weight list! Generating default lookAt weight list...')
        weightList = range(0, 101, 100.0 / len(slaveList))[1:]

    # Slave Aim/Up Vectors
    if not slaveAimUp:
        print('Invalid lookAt slave aim/up vector values! Using default lookAt vectors (aim="z",up="y")...')
        slaveAimUp = [('z', 'y') for slave in slaveList]
    if len(slaveAimUp) != len(slaveList):
        print('Invalid lookAt slave aim/up vector values! Using default lookAt vectors (aim="z",up="y")...')
        slaveAimUp = [('z', 'y') for slave in slaveList]

    # ===========
    # - Look At -
    # ===========

    slaveReferenceList = []
    slaveLookAtList = []
    slaveLookAt_aimList = []
    slaveLookAt_orientList = []

    slaveBakeList = []

    for i in range(len(slaveList)):

        # Check Slave Object
        if not cmds.objExists(slaveList[i]):
            print('Slave object "' + slaveList[i] + '" not found! Skipping...')
            continue

        # Get Slave Short Name
        slaveSN = slaveList[i].split(':')[0]

        # Duplicate Slave to get Reference and LookAt Targets
        slaveReference = cmds.duplicate(slaveList[i], po=True, n=slaveSN + '_reference')[0]
        slaveLookAt = cmds.duplicate(slaveList[i], po=True, n=slaveSN + '_lookAt')[0]

        # Transfer Anim to Reference
        slaveKeys = cmds.copyKey(slaveList[i])
        if slaveKeys: cmds.pasteKey(slaveReference)

        # Delete Slave Rotation Anim
        cmds.cutKey(slaveList[i], at=['rx', 'ry', 'rz'])

        # Create Slave LookAt
        slaveLookAt_aim = glTools.tools.constraint.aicmdsonstraint(target=target,
                                                                 slave=slaveLookAt,
                                                                 aim=slaveAimUp[i][0],
                                                                 up=slaveAimUp[i][1],
                                                                 worldUpType='scene',
                                                                 offset=offset,
                                                                 mo=False)[0]

        # Weighted Orient Constraint
        slaveLookAt_orient = cmds.orientConstraint([slaveReference, slaveLookAt], slaveList[i], mo=False)[0]
        slaveLookAt_targets = glTools.utils.constraint.targetAliasList(slaveLookAt_orient)

        # Set Constraint Target Weights
        cmds.setAttr(slaveLookAt_orient + '.' + slaveLookAt_targets[0], 1.0 - (weightList[i] * 0.01))
        cmds.setAttr(slaveLookAt_orient + '.' + slaveLookAt_targets[1], weightList[i] * 0.01)
        cmds.setAttr(slaveLookAt_orient + '.interpType', 2)  # Shortest

        # Add Message Connections
        cmds.addAttr(slaveList[i], ln='lookAtTarget', at='message')
        cmds.addAttr(slaveList[i], ln='lookAtAnmSrc', at='message')
        cmds.connectAttr(slaveLookAt + '.message', slaveList[i] + '.lookAtTarget', f=True)
        cmds.connectAttr(slaveReference + '.message', slaveList[i] + '.lookAtAnmSrc', f=True)

        # Append Lists
        slaveReferenceList.append(slaveReference)
        slaveLookAtList.append(slaveLookAt)
        slaveLookAt_aimList.append(slaveLookAt_aim)
        slaveLookAt_orientList.append(slaveLookAt_orient)

        slaveBakeList.append(slaveList[i])

    # =============
    # - Bake Anim -
    # =============

    if bakeAnim:

        # Get Bake Range
        start = bakeStartEnd[0]
        end = bakeStartEnd[1]
        if start == None: start = cmds.playbackOptions(q=True, min=True)
        if end == None: end = cmds.playbackOptions(q=True, max=True)

        # Bake Results
        cmds.refresh(suspend=True)
        # for slave in slaveBakeList:
        cmds.bakeResults(slaveBakeList, t=(start, end), at=['rx', 'ry', 'rz'], simulation=True)
        cmds.refresh(suspend=False)

        # Post Bake Cleanup
        if cleanup:
            try:
                cmds.delete(slaveLookAt_orientList)
            except:
                pass
            try:
                cmds.delete(slaveLookAt_aimList)
            except:
                pass
            try:
                cmds.delete(slaveReferenceList)
            except:
                pass
            try:
                cmds.delete(slaveLookAtList)
            except:
                pass

    # ====================
    # - Bake Anim Offset -
    # ====================

    if offsetAnim != None:

        # For Each Slave Object
        for slave in slaveList:

            # Check Slave Object
            if not cmds.objExists(slave):
                print('Slave object "' + slave + '" not found! Skipping...')
                continue

            # Offset Rotate Channels
            for r in ['rx', 'ry', 'rz']:
                cmds.keyframe(slave + '.' + r, e=True, relative=True, timeChange=offsetAnim)

    # =================
    # - Return Result -
    # =================

    return slaveList


def isApplied(slaveList):
    """
    """
    pass


def remove(slaveList):
    """
    """
    pass
