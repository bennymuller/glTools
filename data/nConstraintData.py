import maya.cmds as cmds
import glTools.utils.nDynamics
import data


class NConstraintData(data.Data):
    """
    NConstraintData class object.
    Contains functions to save, load and rebuild maya nDynamics Constraints.
    """

    def __init__(self, nConstraint=None):
        """
        SetData class initializer.
        @param nConstraint: nDynamics constraint to initialize data from
        @type nConstraint: str
        """
        # Execute Super Class Initilizer
        super(NConstraintData, self).__init__()

        # Initialize Default Class Data Members
        self._data['name'] = ''
        self._data['membership'] = []
        self.mode = ['add', 'replace']

        # Build Data
        if setNode: self.buildData(nConstraint)

    def buildData(self, nConstraint):
        """
        Build setData class.
        @param nConstraint:
        """
        # ==========
        # - Checks -
        # ==========

        if not glTools.utils.nDynamics.isNConstraint(nConstraint):
            raise Exception('Object "' + nConstraint + '" is not a valid nDynamics constraint!')

        # ==============
        # - Build Data -
        # ==============

        # Start timer
        timer = cmds.timerX()

        # Reset Data
        self.reset()

        # Get nDynamics info
        self._data['name'] = nConstraint
        self._data['nucleus'] = glTools.utils.nDynamics.getConnectedNucleus(nConstraint)
        self._data['nComponent'] = glTools.utils.nDynamics.getConnectedNComponent(nConstraint)
        self._data['nMesh'] = glTools.utils.nDynamics.getConnectedMesh(self._data['nComponent'])
        self._data['componentIndices'] = cmds.getAttr(self._data['nComponent'] + '.componentIndices')[0]

        # Print timer result
        buildTime = cmds.timerX(st=timer)
        print('NConstraintData: Data build time for set "' + nConstraint + '": ' + str(buildTime))

        # =================
        # - Return Result -
        # =================

        return self._data['name']

    def rebuild(self):
        """
        Rebuild the set from the stored setData.
        """
        # ==========
        # - Checks -
        # ==========

        # Set Name
        if not self._data['name']:
            raise Exception('SetData has not been initialized!')

        # Member Items
        memberList = self._data['membership'] or []
        for obj in memberList:
            if not cmds.objExists(obj):
                print('Set member item "' + obj + '" does not exist! Unable to add to set...')
                memberList.remove(obj)

        # Flatten Membership List
        memberList = cmds.ls(memberList, fl=True) or []

        # Mode
        if not mode in self.mode:
            raise Exception('Invalid set membership mode "' + mode + '"! Use "add" or "replace"!')

        # ===============
        # - Rebuild Set -
        # ===============

        # Start timer
        timer = cmds.timerX()

        # Create Set
        setName = self._data['name']

        # Delete Set (REPLACE only)
        if cmds.objExists(setName) and mode == 'replace': cmds.delete(setName)

        # Create Set
        if not cmds.objExists(setName): setName = cmds.sets(n=setName)

        # Add Members
        if memberList:
            if forceMembership:
                for obj in memberList:
                    try:
                        cmds.sets(obj, e=True, fe=setName)
                    except Exception, e:
                        print('Error adding item "' + obj + '" to set "' + setName + '"! Skipping')
                        print(str(e))
            else:
                for obj in memberList:
                    try:
                        cmds.sets(obj, e=True, add=setName)
                    except Exception, e:
                        print('Error adding item "' + obj + '" to set "' + setName + '"! Skipping')
                        print(str(e))

        # Print Timer Result
        buildTime = cmds.timerX(st=timer)
        print('SetData: Rebuild time for set "' + setName + '": ' + str(buildTime))

        # =================
        # - Return Result -
        # =================

        self.setName = setName

        result = {}
        result['set'] = setName
        result['membership'] = memberList
        return result
