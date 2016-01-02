import maya.cmds as cmds


class UserInputError(Exception):
    pass


class Spaces(object):
    def __init__(self):
        """
        Initializer for Spaces class object
        """
        self.allChannels = ['t', 'tx', 'ty', 'tz', 'r', 'rx', 'ry', 'rz', 's', 'sx', 'sy', 'sz']
        self.channels = self.allChannels[0:8]
        self.transform = ['transform', 'joint']
        self.worldNode = 'spaces_wld01_loc'

        self.managerUI = 'spacesUI'
        self.uiRCL = 'spacesRCL'
        self.uiKeyCBG = 'spacesKeyCBG'
        self.uiKeyPreviousCBG = 'spacesKeyPrevCBG'
        self.uiMaintainPosCBG = 'spacesMaintainPosCBG'
        self.uiAllOMG = 'spacesAllOMG'

    def create(self, ctrl, targetList=[], abrTargetList=[], nameTag='', worldParent=''):
        """
        Create a new spaces node
        @param targetList: list of target transforms for the space node constraint
        @type targetList: list
        @param abrTargetList: list of abreviated target names. Used in UI.
        @type abrTargetList: list
        @param ctrl: Control to be parented to spaces node
        @type ctrl: str
        @param nameTag: Shortened, descriptive name for control. Used in UI.
        @type nameTag: str
        """

        if not len(abrTargetList): abrTargetList = targetList

        # Verify target list
        for target in targetList:
            if not cmds.objExists(target):
                raise UserInputError('Target object ' + target + ' does not exists!')

        # Determine SPACE node
        par = ''
        try:
            par = self.getSpacesNode(ctrl)
        except:
            # Get control transform parent
            par = cmds.listRelatives(ctrl, p=True)
            # If none exist, create one
            if par == None:
                par = cmds.group(ctrl, n=ctrl + '_buf')
            else:
                par = par[0]
        else:
            # Spaces node exists, run Spaces().add()
            # print('Spaces node already exists. Running Spaces().add() instead!')
            result = self.add(ctrl, targetList, abrTargetList, nameTag)
            return result

        # Create spaces WORLD transform
        if not cmds.objExists(self.worldNode):
            self.worldNode = cmds.createNode('transform', n=self.worldNode)
            if len(worldParent):
                if cmds.objExists(worldParent): cmds.parent(self.worldNode, worldParent)
        else:
            if len(worldParent):
                currentWorldParent = cmds.listRelatives(self.worldNode, p=1)[0]
                print('Spaces WORLD node already exists and is parented to ' + currentWorldParent + '!!')

        # Adjust TargetList Arrays
        targetList.insert(0, self.worldNode)
        targetList.insert(0, par)
        abrTargetList.insert(0, 'SuperMover')
        abrTargetList.insert(0, 'Default')

        # Create SPACES constraint transform
        spacesNode = cmds.duplicate(par, rr=1, rc=1, n=ctrl + '_spn')[0]
        cmds.delete(cmds.listRelatives(spacesNode, ad=1))

        # Unlock Constraint Offset
        for ch in self.allChannels: cmds.setAttr(spacesNode + '.' + ch, l=False, k=False)

        # Reparent hierarchy
        cmds.parent(spacesNode, par)
        cmds.parent(ctrl, spacesNode)

        # Add targetOffset attributes to link to constraint
        cmds.addAttr(spacesNode, ln='targetOffsetTranslate', sn='tot', at='double3')
        cmds.addAttr(spacesNode, ln='targetOffsetTranslateX', sn='totx', at='double', p='targetOffsetTranslate')
        cmds.addAttr(spacesNode, ln='targetOffsetTranslateY', sn='toty', at='double', p='targetOffsetTranslate')
        cmds.addAttr(spacesNode, ln='targetOffsetTranslateZ', sn='totz', at='double', p='targetOffsetTranslate')
        cmds.addAttr(spacesNode, ln='targetOffsetRotate', sn='tor', at='double3')
        cmds.addAttr(spacesNode, ln='targetOffsetRotateX', sn='torx', at='double', p='targetOffsetRotate')
        cmds.addAttr(spacesNode, ln='targetOffsetRotateY', sn='tory', at='double', p='targetOffsetRotate')
        cmds.addAttr(spacesNode, ln='targetOffsetRotateZ', sn='torz', at='double', p='targetOffsetRotate')

        # Set targetOffset attributes as keyable
        for ch in self.channels: cmds.setAttr(spacesNode + '.to' + ch, k=True)

        # Add default offset value attributes
        cmds.addAttr(spacesNode, ln='defaultOffset', at='compound', numberOfChildren=2, m=True)
        cmds.addAttr(spacesNode, ln='defaultOffsetTranslate', sn='dot', at='double3', p='defaultOffset')
        cmds.addAttr(spacesNode, ln='defaultOffsetTranslateX', sn='dotx', at='double', p='defaultOffsetTranslate')
        cmds.addAttr(spacesNode, ln='defaultOffsetTranslateY', sn='doty', at='double', p='defaultOffsetTranslate')
        cmds.addAttr(spacesNode, ln='defaultOffsetTranslateZ', sn='dotz', at='double', p='defaultOffsetTranslate')
        cmds.addAttr(spacesNode, ln='defaultOffsetRotate', sn='dor', at='double3', p='defaultOffset')
        cmds.addAttr(spacesNode, ln='defaultOffsetRotateX', sn='dorx', at='doubleAngle', p='defaultOffsetRotate')
        cmds.addAttr(spacesNode, ln='defaultOffsetRotateY', sn='dory', at='doubleAngle', p='defaultOffsetRotate')
        cmds.addAttr(spacesNode, ln='defaultOffsetRotateZ', sn='dorz', at='doubleAngle', p='defaultOffsetRotate')

        # Setup .spaces attribute
        enumString = ''
        for abr in abrTargetList: enumString += abr + ':'
        if not cmds.objExists(spacesNode + '.spaces'):
            cmds.addAttr(spacesNode, ln='spaces', at='enum', en=enumString)
            cmds.setAttr(spacesNode + '.spaces', k=1)
        else:
            cmds.addAttr(spacesNode + '.spaces', e=1, en=enumString)

        # Name Tag
        if not len(nameTag): nameTag = ctrl
        if not cmds.objExists(spacesNode + '.nameTag'):
            cmds.addAttr(spacesNode, ln='nameTag', dt='string')
        cmds.setAttr(spacesNode + '.nameTag', nameTag, type='string')

        # Create constraint
        spacesNodeConstraint = ''
        for i in range(len(targetList)):

            # Add target to constraint
            if not i:
                # First iteration - Create new constraint
                spacesNodeConstraint = cmds.parentConstraint(targetList[i], spacesNode, n=ctrl + '_pcn', w=0.0)[0]
            else:
                # Add to existing constraint
                cmds.parentConstraint(targetList[i], spacesNode, mo=True, w=0.0)

            # Unlock target offset attributes
            for ch in self.channels:
                cmds.setAttr(spacesNodeConstraint + '.target[' + str(i) + '].to' + ch, l=False, k=True)

            translateOffset = cmds.getAttr(spacesNodeConstraint + '.target[' + str(i) + '].targetOffsetTranslate')[0]
            rotateOffset = cmds.getAttr(spacesNodeConstraint + '.target[' + str(i) + '].targetOffsetRotate')[0]

            cmds.setAttr(spacesNode + '.defaultOffset', l=False)
            cmds.setAttr(spacesNode + '.defaultOffset[' + str(i) + '].dot', translateOffset[0], translateOffset[1],
                       translateOffset[2])
            cmds.setAttr(spacesNode + '.defaultOffset[' + str(i) + '].dor', rotateOffset[0], rotateOffset[1],
                       rotateOffset[2])
            cmds.setAttr(spacesNode + '.defaultOffset', l=True)

        # Connect spacesNode to Constraint
        weightAliasList = cmds.parentConstraint(spacesNodeConstraint, q=True, weightAliasList=True)
        for i in range(len(targetList)):
            # Create targetWeight attribute on spacesNode
            cmds.addAttr(spacesNode, ln=weightAliasList[i], min=0.0, max=1.0, dv=0.0)
            cmds.setAttr(spacesNode + '.' + weightAliasList[i], l=False, k=True)
            cmds.connectAttr(spacesNode + '.' + weightAliasList[i], spacesNodeConstraint + '.' + weightAliasList[i],
                           f=True)

            # Connect targetOffset attributes
            translateOffset = cmds.getAttr(spacesNode + '.defaultOffset[' + str(i) + '].dot')[0]
            rotateOffset = cmds.getAttr(spacesNode + '.defaultOffset[' + str(i) + '].dor')[0]
            cmds.setAttr(spacesNode + '.tot', translateOffset[0], translateOffset[1], translateOffset[2], l=False)
            cmds.setAttr(spacesNode + '.tor', rotateOffset[0], rotateOffset[1], rotateOffset[2], l=False)
            cmds.connectAttr(spacesNode + '.tot', spacesNodeConstraint + '.target[' + str(i) + '].tot', f=True)
            cmds.connectAttr(spacesNode + '.tor', spacesNodeConstraint + '.target[' + str(i) + '].tor', f=True)

        # Set all spaces to Default
        self.switch(ctrl, 'Default', 0)

        # Return result
        return [spacesNode, spacesNodeConstraint]

    def add(self, ctrl, targetList=[], abrTargetList=[], nameTag=''):
        """
        add to an existing spaces node
        @param targetList: list of target transforms for the space node constraint
        @type targetList: list
        @param abrTargetList: list of abreviated target names. Used in UI.
        @type abrTargetList: list
        @param ctrl: Control to be parented to spaces node
        @type ctrl: str
        @param nameTag: Shortened, descriptive name for control. Used in UI.
        @type nameTag: str
        """

        if not len(abrTargetList): abrTargetList = targetList

        # Determine SPACE node
        spacesNode = ''
        try:
            spacesNode = self.getSpacesNode(ctrl)
        except:
            # print('Spaces node does not exists. Running Spaces().create() instead!')
            result = self.create(ctrl, targetList, abrTargetList, nameTag)
            return result

        # Determine SPACE node constraint
        spacesNodeConstraint = self.getSpacesConstraint(ctrl)

        # Verify target list
        for target in targetList:
            if not cmds.objExists(target):
                raise UserInputError('Target object ' + target + ' does not exists!')

        # Add Constraint Targets
        targetListSize = len(cmds.parentConstraint(spacesNodeConstraint, q=True, tl=True))
        for i in range(len(targetList)):

            cmds.parentConstraint(targetList[i], spacesNodeConstraint, mo=True, w=0.0)

            # Unlock target offset attributes
            for ch in self.channels:
                cmds.setAttr(spacesNodeConstraint + '.target[' + str(targetListSize) + '].to' + ch, l=False, k=True)

            # Store Default Offset Values
            translateOffset = \
            cmds.getAttr(spacesNodeConstraint + '.target[' + str(targetListSize) + '].targetOffsetTranslate')[0]
            rotateOffset = cmds.getAttr(spacesNodeConstraint + '.target[' + str(targetListSize) + '].targetOffsetRotate')[
                0]

            cmds.setAttr(spacesNode + '.defaultOffset', l=False)
            cmds.setAttr(spacesNode + '.defaultOffset[' + str(targetListSize) + '].dot', translateOffset[0],
                       translateOffset[1], translateOffset[2])
            cmds.setAttr(spacesNode + '.defaultOffset[' + str(targetListSize) + '].dor', rotateOffset[0], rotateOffset[1],
                       rotateOffset[2])
            cmds.setAttr(spacesNode + '.defaultOffset', l=True)

            # Connect spacesNode offset to constraintNode offset
            cmds.connectAttr(spacesNode + '.tot', spacesNodeConstraint + '.target[' + str(targetListSize) + '].tot',
                           f=True)
            cmds.connectAttr(spacesNode + '.tor', spacesNodeConstraint + '.target[' + str(targetListSize) + '].tor',
                           f=True)

            # Increment targetListSize
            targetListSize += 1

        # Add and connect new weight attrs
        weightAliasList = cmds.parentConstraint(spacesNodeConstraint, q=True, weightAliasList=True)
        for i in range(len(weightAliasList)):
            if not cmds.objExists(spacesNode + '.' + weightAliasList[i]):
                cmds.addAttr(spacesNode, ln=weightAliasList[i], k=True, min=0.0, max=1.0, dv=0.0)
                cmds.connectAttr(spacesNode + '.' + weightAliasList[i], spacesNodeConstraint + '.' + weightAliasList[i],
                               f=True)

        # Append .spaces attribute
        enumString = cmds.addAttr(spacesNode + '.spaces', q=True, en=True) + ':'
        for abr in abrTargetList: enumString += abr + ':'
        cmds.addAttr(spacesNode + '.spaces', e=True, en=enumString)

        # Return result
        return [spacesNode, spacesNodeConstraint]

    def switch(self, ctrl, newTarget, key=0, keyPreviousFrame=0, maintainPos=1):
        """
        Switch spaces state for specified control.
        @param ctrl: Control to switch spaces for
        @type ctrl: str
        @param newTarget: Spaces target to swicth to
        @type newTarget: str
        @param key: Set key for spaces state after switch
        @type key: bool
        @param keyPreviousFrame: Set key on previous frame for spaces state before switch. Only relevant when key is also True.
        @type keyPreviousFrame: bool
        """

        # Find Space Node and Relevant Constraint
        spacesNode = self.getSpacesNode(ctrl)
        spacesNodeConstraint = self.getSpacesConstraint(ctrl)
        weightAliasList = cmds.parentConstraint(spacesNodeConstraint, q=True, weightAliasList=True)
        targetTransform = cmds.parentConstraint(spacesNodeConstraint, q=True, targetList=True)

        # Get newTarget constraint index
        validSpaces = cmds.addAttr(spacesNode + '.spaces', q=True, en=True).split(':')
        if not validSpaces.count(newTarget):
            raise UserInputError('Object ' + newTarget + ' is not a spaces target for ' + ctrl)
        newTargetIndex = validSpaces.index(newTarget)

        # Key previous frame
        if keyPreviousFrame: self.key(ctrl, [], cmds.currentTime(q=True) - 1, )

        # Calculate constraint offsets to maintain control position
        if maintainPos:
            # Create temporary constraint transform
            temp = cmds.duplicate(spacesNode, rr=True, rc=True, n='temp_spaceNode')
            cmds.delete(cmds.listRelatives(temp[0], ad=True, pa=True))

            # Unlock channels
            for ch in self.channels: cmds.setAttr(temp[0] + '.' + ch, l=False)

            # Create temporary parent constraint
            conn = cmds.parentConstraint(targetTransform[newTargetIndex], temp[0], mo=True)
            translateOffset = cmds.getAttr(conn[0] + '.target[0].targetOffsetTranslate')[0]
            rotateOffset = cmds.getAttr(conn[0] + '.target[0].targetOffsetRotate')[0]

            # Delete temporary nodes
            cmds.delete(conn)
            cmds.delete(temp)

            # Set Constraint Offsets
            cmds.setAttr(spacesNode + '.tot', translateOffset[0], translateOffset[1], translateOffset[2])
            cmds.setAttr(spacesNode + '.tor', rotateOffset[0], rotateOffset[1], rotateOffset[2])

        # Set Constraint Target Weights
        for i in range(len(validSpaces)): cmds.setAttr(spacesNode + '.' + weightAliasList[i], i == newTargetIndex)
        # Set ".spaces" attribute
        cmds.setAttr(spacesNode + '.spaces', newTargetIndex)

        # Reset to default offset values
        if not maintainPos:
            self.reset(ctrl, 0, 0)

        # Key current frame
        if key: self.key(ctrl, [], cmds.currentTime(q=True))

    def switchAllTo(self, target, char='', key=0, keyPrevious=0, maintainPos=1):
        """
        Switch all spaces nodes to the specified target
        @param target: Spaces target to switch all spaces nodes to
        @type target: str
        @param char: Character namespace to filter for when searching for spaces nodes
        @type char: str
        @param key: Set key for spaces state after switch
        @type key: bool
        @param keyPreviousFrame: Set key on previous frame for spaces state before switch. Only relevant when "key" is also True.
        @type keyPreviousFrame: bool
        """
        # Find all spacesNodes
        spaceNodeList = cmds.ls('*_spn', r=True, et='transform')
        for spacesNode in spaceNodeList:
            child = cmds.listRelatives(spacesNode, c=1)
            try:
                self.switch(child[0], target, key, keyPrevious, maintainPos)
            except:
                print(
                'Object ' + child[0] + ' is not able to be placed in the space of ' + target + '! Skipping control!!')

    def key(self, ctrl, targetList=[], frame=None):
        """
        Set keyframe on spaces relevant attribute for the given control and specified target(s).
        @param ctrl: Control to set spaces keys on
        @type ctrl: str
        @param targetList: List of targets to set keys on
        @type targetList: list
        @param frame: Frame to set keys on
        @type frame: float
        """
        # Check default frame value
        if frame == None: frame = cmds.currentTime(q=True)

        # Get spaces info
        spacesNode = self.getSpacesNode(ctrl)
        spacesNodeConstraint = self.getSpacesConstraint(ctrl)
        weightAliasList = cmds.parentConstraint(spacesNodeConstraint, q=True, weightAliasList=True)

        # Check target list
        if not len(targetList): targetList = self.targetList(ctrl)

        # Get target indices
        targetIndexList = []
        for target in targetList:
            targetIndexList.append(self.targetIndex(ctrl, target))

        # Set keys
        for i in targetIndexList:
            cmds.setKeyframe(spacesNode + '.' + weightAliasList[i], t=frame, itt='clamped', ott='step')
        cmds.setKeyframe(spacesNode + '.tot', t=frame, itt='clamped', ott='step')
        cmds.setKeyframe(spacesNode + '.tor', t=frame, itt='clamped', ott='step')
        cmds.setKeyframe(spacesNode + '.spaces', t=frame, itt='clamped', ott='step')

    def reset(self, ctrl, key=0, keyPreviousFrame=0):
        """
        Reset spaces constraint offsets for the specified control
        @param ctrl: Control whose spaces target offset values will be rest
        @type ctrl: str
        @param key: Set keyframe after reset
        @type key: bool
        @param keyPreviousFrame: Set keyframe before reset. Only relevant when "key" is also True.
        @type keyPreviousFrame: bool
        """
        # Get spaces info
        spacesNode = self.getSpacesNode(ctrl)
        spacesNodeConstraint = self.getSpacesConstraint(ctrl)

        # Check spaces attribute
        if not cmds.objExists(spacesNode + '.spaces'):
            raise UserInputError('Object ' + spacesNode + 'does not contain a ".spaces" attribute!')
        targetIndex = cmds.getAttr(spacesNode + '.spaces')
        target = self.targetList(ctrl)[targetIndex]

        # Key previous frame
        if keyPreviousFrame: self.key(ctrl, [], cmds.currentTime(q=True) - 1, )

        # Reset Offset Values
        translateOffset = cmds.getAttr(spacesNode + '.defaultOffset[' + str(targetIndex) + '].dot')[0]
        rotateOffset = cmds.getAttr(spacesNode + '.defaultOffset[' + str(targetIndex) + '].dor')[0]
        cmds.setAttr(spacesNode + '.tot', translateOffset[0], translateOffset[1], translateOffset[2])
        cmds.setAttr(spacesNode + '.tor', rotateOffset[0], rotateOffset[1], rotateOffset[2])

        # Key current frame
        if key: self.key(ctrl)

    def targetList(self, ctrl):
        """
        Return the spaces target list for the specified control or spaces node
        @param ctrl: Control whose spaces target list will be returned
        @type ctrl: str
        """
        # Check spaces attribute
        spacesNode = self.getSpacesNode(ctrl)
        # Get target list info
        spacesList = cmds.addAttr(spacesNode + '.spaces', q=True, en=True)
        return spacesList.split(':')

    def targetIndex(self, ctrl, target):
        """
        Return the target index for the specified control and spaces target
        @param ctrl: Control whose spaces target index will be returned
        @type ctrl: str
        @param target: Spaces target whose index will be returned
        @type ctrl: str
        """
        spacesNode = self.getSpacesNode(ctrl)
        validSpaces = cmds.addAttr(spacesNode + '.spaces', q=True, en=True).split(':')
        if not validSpaces.count(target):
            raise UserInputError('Object ' + target + ' is not a spaces target for ' + ctrl)
        return validSpaces.index(target)

    def getSpacesNode(self, ctrl):
        """
        Return the name of the spaces node of the specified control
        @param ctrl: Control whose spaces node will be returned
        @type ctrl: str
        """
        # Check control
        if cmds.objExists(ctrl + '.spaces') and cmds.objExists(ctrl + '.defaultOffset'): return ctrl

        # Determine spaces node
        parent = cmds.listRelatives(ctrl, p=True)
        if parent == None:
            raise UserInputError('Object ' + ctrl + ' is not the child of a valid spaces node!')
        if not parent[0].endswith('_spn'):
            raise UserInputError('Object ' + ctrl + ' is not the child of a valid spaces node!')
        # Check spaces attribute
        if not cmds.objExists(parent[0] + '.spaces'):
            raise UserInputError('Spaces node ' + parent[0] + 'does not contain a ".spaces" attribute!')
        return parent[0]

    def getSpacesConstraint(self, ctrl):
        """
        Return the name of the spaces constraint node of the specified control
        @param ctrl: Control whose spaces constraint node will be returned
        @type ctrl: str
        """
        spacesNode = self.getSpacesNode(ctrl)
        spaceTransConst = cmds.listConnections(spacesNode + '.tx', s=True, d=False, type='parentConstraint')
        spaceRotConst = cmds.listConnections(spacesNode + '.rx', s=True, d=False, type='parentConstraint')
        if type(spaceTransConst) != list or type(spaceRotConst) != list:
            raise UserInputError('No spaces constraint found for ' + ctrl)
        if spaceTransConst[0] != spaceRotConst[0]:
            raise UserInputError('Translate and Rotate Constraint Mis-match on ' + ctrl)
        return spaceTransConst[0]

    def updateOld(self):
        """
        Update old style spaces setup to work with new spaces procedures.
        """
        # Get list of existing spaces nodes
        spacesNodeList = cmds.ls('*_spn', r=1, et='transform')
        for spacesNode in spacesNodeList:
            spacesChild = cmds.listRelatives(spacesNode, c=True, type='transform')[0]

            # Transfer .spaces attribute
            if cmds.objExists(spacesChild + '.spaces'):
                enumString = cmds.addAttr(spacesChild + '.spaces', q=True, en=True)
                cmds.addAttr(spacesNode, ln='spaces', at='enum', en=enumString)
                cmds.setAttr(spacesNode + '.spaces', k=1)
                cmds.deleteAttr(spacesChild + '.spaces')

            # Transfer .nameTag attribute
            if cmds.objExists(spacesChild + '.nameTag'):
                nameTagStr = cmds.getAttr(spacesChild + '.nameTag')
                cmds.addAttr(spacesNode, ln='nameTag', dt='string')
                cmds.setAttr(spacesNode + '.nameTag', nameTagStr, type='string')
                cmds.deleteAttr(spacesChild + '.nameTag')

    # =====================================
    # UI METHODS =========================

    def ui_embed(self, parentLayout, char=''):
        """
        @param parentLayout: Parent UI layout to parent spaces UI to.
        @type parentLayout: str
        @param char: Character namespace to create UI for
        @type char: str
        """
        # Get Character Prefix
        if char: char += ':'

        # List all spaces with given prefix
        spaceNodeList = cmds.ls(char + '*_spn', r=True, et='transform')
        spaceNodeList = [i for i in spaceNodeList if not i.endswith('_con_spn')]

        # Generate target list with default elements
        targetList = ['SuperMover', 'Default']

        # Build Spaces List from eNum attributes
        for node in spaceNodeList:
            if cmds.objExists(node + '.spaces'):
                enumList = cmds.addAttr(node + '.spaces', q=True, en=True).split(':')
                [targetList.append(i) for i in enumList if not targetList.count(i)]

        # Begin UI Build
        if not cmds.layout(parentLayout, q=True, ex=True):
            raise UserInputError('Parent layout ' + parentLayout + ' does not exists! Unable to embed Spaces UI!')

        cmds.setParent(parentLayout)
        # Clear Layout
        childArray = cmds.layout(parentLayout, q=True, ca=True)
        if type(childArray) == list: cmds.deleteUI(childArray)

        # Add Spaces control layout
        cmds.rowColumnLayout(self.uiRCL, numberOfColumns=5, columnWidth=[(1, 160), (2, 160), (3, 80), (4, 80), (5, 80)])

        # Add KeyFrame CheckBoxs
        cmds.checkBoxGrp(self.uiKeyPreviousCBG, numberOfCheckBoxes=1, label="Key Before Switch", v1=0)
        cmds.checkBoxGrp(self.uiKeyCBG, numberOfCheckBoxes=1, label="Key After Switch", v1=0)

        for i in range(3): cmds.separator(h=20, style='none')

        cmds.checkBoxGrp(self.uiMaintainPosCBG, numberOfCheckBoxes=1, label="Maintain Position", v1=1)

        for i in range(4): cmds.separator(h=20, style='none')
        for i in range(5): cmds.separator(h=20, style='single')

        # ALL OptionMenu
        cmds.text(label='ALL')
        cmds.optionMenuGrp(self.uiAllOMG, cw=(1, 1), cal=(1, 'center'), label='',
                         cc='glTools.tools.spaces.Spaces().switchAllFromUI()')
        for item in targetList: cmds.menuItem(label=item)

        cmds.button(w=80, l='Reset', c='glTools.tools.spaces.Spaces().resetAllFromUI("' + char + '")')
        cmds.button(w=80, l='Select', c='cmds.select(cmds.ls("' + char + '*_spn"))')
        cmds.button(w=80, l='Key', c='glTools.tools.spaces.Spaces().keyAllFromUI("' + char + '")')

        for i in range(5): cmds.separator(h=20, style='single')

        # Create attrEnumOptionMenu controls to accurately represent attribute values at all times.
        # ie - Update on frame change
        for spacesNode in spaceNodeList:
            tag = cmds.getAttr(spacesNode + '.nameTag')
            cmds.text(label=tag)
            cmds.attrEnumOptionMenu(tag + '_switchAEO', w=160, label='', attribute=spacesNode + '.spaces',
                                  dtg=spacesNode + '.spaces',
                                  cc='glTools.tools.spaces.Spaces().switchFromUI("' + spacesNode + '")')
            cmds.button(w=80, l='Reset', c='glTools.tools.spaces.Spaces().resetFromUI("' + spacesNode + '")')
            cmds.button(w=80, l='Select', c='cmds.select("' + spacesNode + '")')
            cmds.button(w=80, l='Key', c='glTools.tools.spaces.Spaces().key("' + spacesNode + '")')
        # cmds.separator(h=20,style='none')

    def ui(self, char=''):
        """
        Creates the main control interface for manipulating spaces
        @param char: Character namespace to filter for when populating UI.
        @type char: str
        """
        # Generate window
        win = self.managerUI
        if cmds.window(win, q=True, ex=True): cmds.deleteUI(win)
        win = cmds.window(win, t='Spaces UI - ' + char.upper())

        # Create column layout for controls items
        spacesCL = cmds.columnLayout('spacesUI_CL', adjustableColumn=True)

        # Open window
        cmds.showWindow(win)

        # Embed control layout into window
        self.ui_embed(spacesCL, char)

    def switchFromUI(self, ctrl):
        """
        Switch a spaces nodes to the specified target from the spaces UI
        @param ctrl: Control whose spaces target will be switched
        @type ctrl: str
        """
        # Determine spaces node
        spacesNode = self.getSpacesNode(ctrl)
        tag = cmds.getAttr(spacesNode + '.nameTag')

        # Query Target
        # !!! optionMenu command no longer allows access to attrEnumOptionMenu !!!
        # target = cmds.optionMenu(tag+'_switchAEO',q=True,v=True)
        targetIndex = cmds.getAttr(cmds.attrEnumOptionMenu(tag + '_switchAEO', q=True, dtg=True))
        target = self.targetList(spacesNode)[targetIndex]

        # Check keyframe options
        key = cmds.checkBoxGrp(self.uiKeyCBG, q=True, v1=True)
        keyPrevious = cmds.checkBoxGrp(self.uiKeyPreviousCBG, q=True, v1=True)

        # Check offset options
        maintainPos = cmds.checkBoxGrp(self.uiMaintainPosCBG, q=True, v1=True)

        # Do switch
        self.switch(ctrl, target, key, keyPrevious, maintainPos)

    def switchAllFromUI(self, char=''):
        """
        Switch all spaces nodes to the specified target from the UI.
        @param char: Character whose spaces target will be switched
        @type char: str
        """
        # Determine target
        if not cmds.optionMenuGrp(self.uiAllOMG, q=True, ex=True):
            raise UserInputError('OptionMenuGrp ' + self.uiAllOMG + ' does not exist!')
        target = cmds.optionMenuGrp(self.uiAllOMG, q=True, v=True)

        # Check keyframe options
        key = cmds.checkBoxGrp(self.uiKeyCBG, q=True, v1=True)
        keyPrevious = cmds.checkBoxGrp(self.uiKeyPreviousCBG, q=True, v1=True)

        # Check offset options
        maintainPos = cmds.checkBoxGrp(self.uiMaintainPosCBG, q=True, v1=True)

        # Do switch
        self.switchAllTo(target, char, key, keyPrevious, maintainPos)

    def resetFromUI(self, ctrl):
        """
        Reset spaces constraint offsets for the specified control from the spaces UI
        @param ctrl: Control whose spaces target offset values will be rest
        @type ctrl: str
        """
        # Get reset options
        key = cmds.checkBoxGrp(self.uiKeyCBG, q=True, v1=True)
        keyPrevious = cmds.checkBoxGrp(self.uiKeyPreviousCBG, q=True, v1=True)

        # Reset
        self.reset(ctrl, key, keyPrevious)

    def resetAllFromUI(self, char):
        """
        Reset spaces constraint offsets for all controls in the specified character namespace
        @param char: Namespace of the character to reset spaces node offsets for
        @type char: str
        """
        # Get key options
        key = cmds.checkBoxGrp(self.uiKeyCBG, q=True, v1=True)
        keyPrevious = cmds.checkBoxGrp(self.uiKeyPreviousCBG, q=True, v1=True)

        # Reset Spaces Nodes
        for spacesNode in cmds.ls(char + '*_spn'):
            self.reset(spacesNode, key, keyPrevious)

    def keyAllFromUI(self, char):
        """
        Key all spaces nodes in the specified character namespace
        @param char: Namespace of the character to key spaces node for
        @type char: str
        """
        # Key Spaces Nodes
        for spacesNode in cmds.ls(char + '*_spn'): self.key(spacesNode)
