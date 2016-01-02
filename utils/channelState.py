import maya.cmds as cmds
import maya.mel as mel
import glTools.utils.transform


class ChannelState(object):
    def __init__(self):
        """
        ChannelState class initializer
        """
        self.channel = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']
        self.window = 'channelStateUI'
        self.labelArray = ['No Change', 'Keyable', 'NonKeyable', 'Locked']

    def add(self, objectList):
        """
        Adds the channel state attr to all specified objects
        @param objectList: List of objects to add flags to
        @type objectList: list
        """
        # Add Channel State Attrs
        for obj in objectList:

            # Check obj
            if not cmds.objExists(obj):
                raise Exception('Object "' + obj + '" does not exist!')
            if not glTools.utils.transform.isTransform(obj):
                raise Exception('Object "' + obj + '" is not a valid transform!')
            if cmds.objExists(obj + '.channelState'):
                print ('Object "' + obj + '" already has a "channelState" attribute! Skipping...')

            # Add channelState attr
            # cmds.addAttr(obj,ln='channelState',at='enum',en=':Keyable:NonKeyable:Locked:',m=1,dv=-1)
            cmds.addAttr(obj, ln='channelState', at='enum', en=':Keyable:NonKeyable:Locked:', m=1)

            # Set channelState flag values
            for i in range(len(self.channel)):
                if cmds.getAttr(obj + '.' + self.channel[i], l=1):
                    # Set Locked State
                    cmds.setAttr(obj + '.channelState[' + str(i) + ']', 2)
                elif not cmds.getAttr(obj + '.' + self.channel[i], k=1):
                    # Set NonKeyable State
                    cmds.setAttr(obj + '.channelState[' + str(i) + ']', 1)
                else:
                    # Set Keyable State
                    cmds.setAttr(obj + '.channelState[' + str(i) + ']', 0)
                # Alias Attribute
                cmds.aliasAttr(self.channel[i] + '_state', obj + '.channelState[' + str(i) + ']')

    def setFlags(self, flags=[0, 0, 0, 0, 0, 0, 0, 0, 0, 1], objectList=[]):
        """
        Sets the channelState attributes on all specified objects
        @param flags: Channel state values for object channels
        @type flags: list
        @param objectList: List of objects to set flags for
        @type objectList: list
        """
        # For each object
        for obj in objectList:

            # Check Obj
            if not obj: continue
            if not cmds.objExists(obj):
                raise Exception('Object "' + obj + '" does not exist!')
            if not glTools.utils.transform.isTransform(obj):
                raise Exception('Object "' + obj + '" is not a valid transform!')
            # Check ChannelState Attr
            if not cmds.objExists(obj + '.channelState'):
                self.add([obj])
            # Set Flags
            for i in range(len(self.channel)):
                if flags[i] != -1:
                    cmds.setAttr(obj + '.channelState[' + str(i) + ']', flags[i])

    def get(self, obj):
        """
        Get the channel state values from an object and return them in an list.
        An empty list will be returned if they are not tagged
        @param obj: Object to get channels states from
        @type obj: str
        """
        # Get channel state values from object attributes
        channelState = []
        if cmds.objExists(obj + '.channelState'):
            for i in range(len(self.channel)):
                channelState.append(cmds.getAttr(obj + '.channelState[' + str(i) + ']'))
        return channelState

    def set(self, state, objectList=[]):
        """
        Set channel states based on channelState multi attribute
        @param state: The state to set object channels to. 0 = OFF, 1 = ON
        @type state: int
        @param objList: List of objects to set channels states for
        @type objList: list
        """
        # Check objectList
        if type(objectList) == str: objectList = [objectList]
        if not objectList: objectList = cmds.ls('*.channelState', o=True)

        # For each object in list
        for obj in objectList:

            # Check Object
            if not obj: continue

            # Get/Check Channel State Values
            channelState = self.get(obj)
            if not channelState: continue
            if len(channelState) != len(self.channel):
                raise Exception(
                    'Attribute "' + obj + '.channelState" is not the expected length (' + str(len(self.channel)) + ')!')

            if state:
                for i in range(len(self.channel)):
                    if channelState[i] == 0:  # KEYABLE
                        cmds.setAttr(obj + '.' + self.channel[i], l=False, k=True)
                    elif channelState[i] == 1:  # NON-KEYABLE
                        cmds.setAttr(obj + '.' + self.channel[i], l=False, k=False, cb=False)
                    elif channelState[i] == 2:  # LOCKED
                        cmds.setAttr(obj + '.' + self.channel[i], l=True, k=False, cb=False)
                    else:  # INVALID OPTION
                        raise Exception('Invalid channel state value (' + str(channelState[i]) + ')!')

                # Joint Radius
                if cmds.objExists(obj + '.radius'): cmds.setAttr(obj + '.radius', l=False, k=False)

            else:
                # Unlock Channel State
                for attr in self.channel:
                    cmds.setAttr(obj + '.' + attr, l=False, k=True, cb=True)

                # Joint Radius
                if cmds.objectType == 'joint' and cmds.objExists(obj + '.radius'):
                    cmds.setAttr(obj + '.radius', l=False, k=True, cb=True)

    def toggleSelected(self, state):
        """
        Set channel states on all selected objects
        @param state: The state to set object channels to
        @type state: int
        """
        self.set(state, cmds.ls(sl=1))

    # ==============
    # - UI Methods -
    # ==============

    def ui(self):
        """
        Main UI function
        @usage: ChannelState.ui()
        """
        # Create Window
        if cmds.window(self.window, q=1, ex=1): cmds.deleteUI(self.window)
        cmds.window(self.window, t='Channel State Editor', w=630, h=445, rtf=1, mnb=1, mb=1)

        cmds.columnLayout(adj=1, w=500)

        cmds.separator(style='none', h=10)
        cmds.text(l='   SET CHANNEL FLAGS', font='boldLabelFont', align='left')
        cmds.separator(style='none', h=10)
        # SET ALL
        cmds.radioButtonGrp('rbgSetAll', numberOfRadioButtons=4, label='SET ALL', labelArray4=self.labelArray, sl=1)
        cmds.radioButtonGrp('rbgSetAll', e=1, on1='glTools.utils.channelState.ChannelState().uiSetAll(1)',
                          on2='glTools.utils.channelState.ChannelState().uiSetAll(2)',
                          on3='glTools.utils.channelState.ChannelState().uiSetAll(3)',
                          on4='glTools.utils.channelState.ChannelState().uiSetAll(4)')

        cmds.separator(style='in', h=10)
        # Transform attrs
        cmds.radioButtonGrp('rbgTX', numberOfRadioButtons=4, label='Translate X', labelArray4=self.labelArray, sl=1)
        cmds.radioButtonGrp('rbgTY', numberOfRadioButtons=4, label='Translate Y', labelArray4=self.labelArray, sl=1)
        cmds.radioButtonGrp('rbgTZ', numberOfRadioButtons=4, label='Translate Z', labelArray4=self.labelArray, sl=1)
        cmds.separator(style='none', h=5)
        cmds.radioButtonGrp('rbgRX', numberOfRadioButtons=4, label='Rotate X', labelArray4=self.labelArray, sl=1)
        cmds.radioButtonGrp('rbgRY', numberOfRadioButtons=4, label='Rotate Y', labelArray4=self.labelArray, sl=1)
        cmds.radioButtonGrp('rbgRZ', numberOfRadioButtons=4, label='Rotate Z', labelArray4=self.labelArray, sl=1)
        cmds.separator(style='none', h=5)
        cmds.radioButtonGrp('rbgSX', numberOfRadioButtons=4, label='Scale X', labelArray4=self.labelArray, sl=1)
        cmds.radioButtonGrp('rbgSY', numberOfRadioButtons=4, label='Scale Y', labelArray4=self.labelArray, sl=1)
        cmds.radioButtonGrp('rbgSZ', numberOfRadioButtons=4, label='Scale Z', labelArray4=self.labelArray, sl=1)
        cmds.separator(style='none', h=5)
        cmds.radioButtonGrp('rbgV', numberOfRadioButtons=4, label='Visibility', labelArray4=self.labelArray, sl=1)

        # Object Selection
        cmds.separator(style='in', h=20)
        cmds.text(l='   SET FLAGS/STATE ON', font='boldLabelFont', align='left')
        cmds.separator(style='none', h=10)

        cmds.rowColumnLayout(nc=3, cw=[(1, 140), (2, 300), (3, 145)])
        cmds.text(l='')
        cmds.radioButtonGrp('rbgObjType', numberOfRadioButtons=3, labelArray3=['Selection', 'All', 'Type'], sl=1,
                          on3='cmds.textField("tfType",e=1,visible=1)', of3='cmds.textField("tfType",e=1,visible=0)')
        cmds.textField('tfType', visible=0)
        cmds.setParent('..')
        cmds.separator(style='in', h=30)

        # Buttons
        cmds.rowColumnLayout(nc=4, cw=[(1, 60), (2, 175), (3, 175), (4, 175)])
        cmds.text(l='')
        cmds.button(l='Set Flags',
                  ann='Only sets the flags on the desired objects, it does not change their current state.',
                  c='glTools.utils.channelState.ChannelState().uiSetFlags()')
        cmds.button(l='Set State ON', ann='Sets all channels to the values indicated by thier flags.',
                  c='glTools.utils.channelState.ChannelState().uiState(1)')
        cmds.button(l='Set State OFF', ann='Same as making all channels keyable and visible.',
                  c='glTools.utils.channelState.ChannelState().uiState(0)')
        cmds.setParent('..')
        cmds.setParent('..')

        # Show Window
        cmds.showWindow(self.window)
        cmds.window(self.window, e=1, w=630, h=445)

    def uiSetAll(self, select):
        """
        Function used by ChannelState.ui().
        Sets all channel state radio buttons to a specified value
        @param select: The value to set the radio buttons to
        @type select: int
        """
        for attr in self.channel:
            # Set RadioButton Selection
            cmds.radioButtonGrp('rbg' + attr.upper(), e=1, sl=select)

    def uiSetFlags(self):
        """
        Gets the channel state data from the UI and then sets the flags.
        """
        # Get channel state flag values
        channelState = []
        for attr in self.channel:
            channelState.append(cmds.radioButtonGrp('rbg' + attr.upper(), q=1, sl=1) - 2)

        # Get list of objects to set flags for
        objType = cmds.radioButtonGrp('rbgObjType', q=1, sl=1)
        objectList = []

        if objType == 1:
            objectList = cmds.ls(sl=1)
        elif objType == 2:
            doit = cmds.confirmDialog(title='Confirm Set Flags on ALL Transforms',
                                    m='Are you sure you want to mass edit all the channel state attributes?',
                                    button=('Yes', 'No'),
                                    defaultButton='No',
                                    cancelButton='No',
                                    dismissString='NO')
            if doit == 'No': return
            objectList = cmds.ls('*.channelState', o=True)
        elif objType == 3:
            selType = cmds.textField('tfType', q=1, text=1)
            objectList = cmds.ls(type=selType)

        # Set Flags
        self.setFlags(channelState, objectList)

    def uiState(self, state):
        """
        This is a button wrapper for UI state
        """
        objType = cmds.radioButtonGrp('rbgObjType', q=1, sl=1)
        # Create the list of objects to set flags for
        objectList = []
        if objType == 1:
            objectList = cmds.ls(sl=1)
        elif objType == 2:
            objectList = cmds.ls('*.channelState', o=True)
        elif objType == 3:
            selType = cmds.textField('tfType', q=1, text=1)
            objectList = cmds.ls(type=selType)
        self.set(state, objectList)
