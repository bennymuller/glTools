import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import glTools.utils.base
import glTools.utils.connection
import glTools.utils.wrap
import deformerData


class WrapData(deformerData.DeformerData):
    """
    WrapData class object.
    """

    def __init__(self):
        """
        """
        # ==================================
        # - Execute Super Class Initilizer -
        # ==================================

        super(WrapData, self).__init__()

        # ========================
        # - Initialize Wrap Data -
        # ========================

        self._data['attrValueList'].append('weightThreshold')
        self._data['attrValueList'].append('maxDistance')
        self._data['attrValueList'].append('autoWeightThreshold')
        self._data['attrValueList'].append('exclusiveBind')
        self._data['attrValueList'].append('falloffMode')

        self._data['attrConnectionList'].append('geomMatrix')

    def buildData(self, wrap):
        """
        Build wrap data and store as class object dictionary entries
        @param wrap: Wrap deformer to store data for.
        @type wrap: str
        """
        # ==========
        # - Checks -
        # ==========

        # Verify node
        glTools.utils.base.verifyNode(wrap, 'wrap')

        # =====================
        # - Get Deformer Data -
        # =====================

        # Clear Data
        self.reset()

        # Get influence curves
        influenceList = glTools.utils.connection.connectionListToAttr(wire, 'deformedWire')

        # Custom Attribute Data
        for inf in influenceList.keys():
            ind = influenceList[inf][1]
            self._data['attrConnectionList'].append('dropoffDistance[' + str(ind) + ']')
            self._data['attrConnectionList'].append('scale[' + str(ind) + ']')

        super(WrapData, self).buildData(wrap)

        # ======================
        # - Get Influence Data -
        # ======================

        for influence in influenceList.keys():
            infIndex = influenceList[influence][1]
            self._influenceData[influence] = {}
            self._influenceData[influence]['index'] = infIndex
            self._influenceData[influence]['influenceBase'] = \
            cmds.listConnections(wire + '.baseWire[' + str(infIndex) + ']', s=True, d=False)[0]
            self._influenceData[influence]['dropoffDist'] = cmds.getAttr(wire + '.dropoffDistance[' + str(infIndex) + ']')
            self._influenceData[influence]['scale'] = cmds.getAttr(wire + '.scale[' + str(infIndex) + ']')

        # ============================
        # - Get Dropoff Locator Data -
        # ============================

        dropoffLocatorList = glTools.utils.connection.connectionListToAttr(wire, 'wireLocatorParameter')

        for locator in dropoffLocatorList.keys():
            # Initialize dropoff locator data dictionary
            self._locatorData[locator] = {}

            # Build dropoff locator data
            locIndex = dropoffLocatorList[locator][1]
            self._locatorData[locator]['index'] = locIndex
            self._locatorData[locator]['envelope'] = cmds.getAttr(wire + '.wireLocatorEnvelope[' + str(locIndex) + ']')
            self._locatorData[locator]['twist'] = cmds.getAttr(wire + '.wireLocatorTwist[' + str(locIndex) + ']')
            self._locatorData[locator]['percent'] = cmds.getAttr(locator + '.percent')
            self._locatorData[locator]['parameter'] = cmds.getAttr(locator + '.param')

            # Get wire curve parent
            locParent = cmds.listRelatives(locator, p=True)[0]
            crvParent = cmds.listRelatives(locParent, p=True)[0]
            self._locatorData[locator]['parent'] = crvParent

    def rebuild(self):
        """
        Rebuild the wire deformer from the recorded deformerData
        """
        # ==========
        # - Checks -
        # ==========

        # Check Data
        for influence in self._influenceData.iterkeys():

            # Check Wire Curve
            if not cmds.objExists(influence):
                print('Wire curve "' + influence + '" does not exist! Curve will not be added to deformer!')

            # Check Base Curves
            baseCurve = self._influenceData[influence]['influenceBase']
            if not cmds.objExists(baseCurve):
                print(
                'Wire curve base "' + baseCurve + '" does not exist! A static base curve will be generated from the deforming wire curve!')

        # Check Dropoff Locators
        for locator in self._locatorData.iterkeys():
            if cmds.objExists(locator):
                cmds.delete(cmds.listRelatives(locator, p=True)[0])

        # ====================
        # - Rebuild Deformer -
        # ====================

        result = super(WireData, self).rebuild()
        wireDeformer = result['deformer']

        # =======================
        # - Connect Wire Curves -
        # =======================

        for influence in self._influenceData.iterkeys():

            # Get current wire curve pair
            wireCurve = influence
            infIndex = self._influenceData[influence]['index']
            baseCurve = self._influenceData[influence]['influenceBase']

            # Connect deformed wire
            if not cmds.objExists(influence): continue
            cmds.connectAttr(wireCurve + '.worldSpace[0]', wireDeformer + '.deformedWire[' + str(infIndex) + ']', f=True)

            # Connect base wire
            if not cmds.objExists(baseCurve): baseCurve = cmds.duplicate(influence, n=baseCurve)[0]
            cmds.connectAttr(baseCurve + '.worldSpace[0]', wireDeformer + '.baseWire[' + str(infIndex) + ']', f=True)
            cmds.setAttr(baseCurve + '.v', 0)

            # Set Influence Attributes
            if cmds.getAttr(wireDeformer + '.dropoffDistance[' + str(infIndex) + ']', se=True):
                cmds.setAttr(wireDeformer + '.dropoffDistance[' + str(infIndex) + ']',
                           self._influenceData[influence]['dropoffDist'])
            if cmds.getAttr(wireDeformer + '.scale[' + str(infIndex) + ']', se=True):
                cmds.setAttr(wireDeformer + '.scale[' + str(infIndex) + ']', self._influenceData[influence]['scale'])

        # ============================
        # - Rebuild Dropoff Locators -
        # ============================

        for locator in self._locatorData.iterkeys():
            # Get data
            parent = self._locatorData[locator]['parent']
            param = self._locatorData[locator]['parameter']
            env = self._locatorData[locator]['envelope']
            percent = self._locatorData[locator]['percent']
            twist = self._locatorData[locator]['twist']

            # Create Locator
            loc = cmds.dropoffLocator(env, percent, wire, parent + '.u[' + str(param) + ']')[0]

            # Apply Twist
            locConn = cmds.listConnections(loc + '.param', s=False, d=True, p=True)[0]
            locConnIndex = locConn.split('[')[-1].split(']')[0]
            cmds.setAttr(wireDeformer + '.wireLocatorTwist[' + str(locConnIndex) + ']', twist)

        # =================
        # - Return Result -
        # =================

        self.result['influence'] = self._influenceData.keys()
        self.result['dropoffLocator'] = self._locatorData.keys()

        return self.result
