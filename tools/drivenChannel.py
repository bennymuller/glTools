import maya.cmds as cmds
import glTools.utils.stringUtils


def setup(targetChannel,
          sourceChannelList,
          method='add',
          addSourceAttrs=False,
          multOutput=False,
          prefix=''):
    """
    @param targetChannel: Target channel to drive with soecified inputs
    @type targetChannel: str
    @param sourceChannelList: List of source channels to combine and drive the target channel
    @type sourceChannelList: list
    @param method: Source channel combine method. "add", "mult" or "average"
    @type method: str
    @param addSourceAttrs: Add source attributes if they don't already exist.
    @type addSourceAttrs: bool
    @param prefix: String name to strip the suffix from
    @type prefix: str
    """
    # ==========
    # - Checks -
    # ==========

    # Method
    if not method in ['add', 'average', 'mult']:
        raise Exception('Invalid source channel combine method "' + method + '"!')

    # Target Channel
    if not cmds.objExists(targetChannel):
        raise Exception('Target channel "' + targetChannel + '" does not exist!')
    targetNode = cmds.ls(targetChannel, o=True)[0]
    targetAttr = targetChannel.split('.')[-1]
    if not cmds.attributeQuery(targetAttr, n=targetNode, ex=True):
        raise Exception('Target attribute "' + targetAttr + '" not found on node "' + targetNode + '"!')
    targetAttrLong = cmds.attributeQuery(targetAttr, n=targetNode, longName=True)

    # Source Channel
    for sourceChannel in sourceChannelList:

        if not cmds.objExists(sourceChannel):

            # Add Missing Source
            if addSourceAttrs:
                sourceNode = sourceChannel.split('.')[0]
                sourceAttr = sourceChannel.split('.')[-1]

                # Check Source Node
                if not cmds.objExists(sourceNode):
                    raise Exception('Source channel node "' + sourceNode + '" does not exist!')

                # Add Source Attribute
                cmds.addAttr(sourceNode, ln=sourceAttr, k=True)

            else:
                raise Exception('Source channel "' + sourceChannel + '" does not exist!')

    # Prefix
    if not prefix: prefix = targetNode + '_' + targetAttr

    # ==============================
    # - Build Driven Channel Value -
    # ==============================

    # Initialize outChannel Variable (method return value)
    outChannel = None

    if method == 'mult':

        multNodeList = []

        for i in range(len(sourceChannelList) - 1):

            # Get Index
            strInd = glTools.utils.stringUtils.alphaIndex(i)

            # Create Multiply Node
            multNode = cmds.createNode('multDoubleLinear', n=prefix + '_mult' + strInd + '_multDoubleLinear')

            # Define Multiply Inputs
            multIn1 = sourceChannelList[i]
            if i: multIn1 = multNodeList[-1]
            multIn2 = sourceChannelList[i + 1]

            # Connect Multiply Inputs
            cmds.connectAttr(multIn1, multNode + '.input1', f=True)
            cmds.connectAttr(multIn2, multNode + '.input2', f=True)

            # Append List
            multNodeList.append(multNode)

        # Define Output Channel
        outChannel = multNodeList[-1] + '.output'

    else:

        # Create Combine Node
        combineNode = cmds.createNode('plusMinusAverage', n=prefix + '_' + method + '_plusMinusAverage')

        # Set Combine Mode
        if method == 'add':
            cmds.setAttr(combineNode + '.operation', 1)  # Sum
        elif method == 'average':
            cmds.setAttr(combineNode + '.operation', 3)  # Averge

        # Connect Source Channels to Combine Node
        for i in range(len(sourceChannelList)):
            cmds.connectAttr(sourceChannelList[i], combineNode + '.input1D[' + str(i) + ']', f=True)

        # Connect to Target Channel
        cmds.connectAttr(combineNode + '.output1D', targetChannel, f=True)
        outChannel = combineNode + '.output1D'

    # ===================
    # - Multiply Output -
    # ===================

    if multOutput:
        # Create Output Multiplier Node
        multOutNode = cmds.createNode('multDoubleLinear', n=prefix + '_multOutput_multDoubleLinear')

        # Add Output Multiplier Attribute
        cmds.addAttr(targetNode, ln=targetAttrLong + '_mult')

        # Connect Output Multiplier
        cmds.connectAttr(outChannel, multOutNode + '.input1', f=True)
        cmds.connectAttr(targetNode + '.' + targetAttrLong + '_mult', multOutNode + '.input2', f=True)

        outChannel = multOutNode + '.output'

    # ============================
    # - Connect Output to Target -
    # ============================

    cmds.connectAttr(outChannel, targetChannel, f=True)

    # =================
    # - Return Result -
    # =================

    return outChannel
