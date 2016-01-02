import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import deformerData


class LatticeData(deformerData.DeformerData):
    """
    LatticeData class object.
    """

    def __init__(self, deformer=None):
        """
        """
        # Update Attr Value/Connection List
        # self._data['attrValueList']
        # self._data['attrConnectionList']

        # Execute Super Class Initilizer
        super(LatticeData, self).__init__(deformer)

    def buildData(self, deformer):
        """
        """
        # ==========
        # - Checks -
        # ==========

        # Verify node
        lattice = deformer
        if not cmds.objExists(lattice):
            raise Exception('Lattice deformer ' + lattice + ' does not exists! No influence data recorded!!')

        objType = cmds.objectType(lattice)
        if objType == 'transform':
            lattice = cmds.listRelatives(lattice, s=True, ni=True)[0]
            objType = cmds.objectType(lattice)
        if objType == 'lattice':
            lattice = cmds.listConnections(lattice + '.latticeOutput', s=False, d=True, type='ffd')[0]
            objType = cmds.objectType(lattice)
        if objType != 'ffd':
            raise Exception(
                'Object ' + lattice + ' is not a vaild lattice deformer! Incorrect class for node type ' + objType + '!!')

        # =====================
        # - Get Deformer Data -
        # =====================

        # FFD Attributes
        self.local = cmds.getAttr(lattice + '.local')
        self.outside = cmds.getAttr(lattice + '.outsideLattice')
        self.falloff = cmds.getAttr(lattice + '.outsideFalloffDist')
        self.resolution = cmds.getAttr(lattice + '.usePartialResolution')
        self.partialResolution = cmds.getAttr(lattice + '.partialResolution')
        self.freeze = cmds.getAttr(lattice + '.freezeGeometry')
        self.localInfluenceS = cmds.getAttr(lattice + '.localInfluenceS')
        self.localInfluenceT = cmds.getAttr(lattice + '.localInfluenceT')
        self.localInfluenceU = cmds.getAttr(lattice + '.localInfluenceU')

        # Get Input Lattice and Base
        self.latticeShape = cmds.listConnections(lattice + '.deformedLatticePoints', sh=True)[0]
        self.lattice = cmds.listRelatives(self.latticeShape, p=True)[0]
        self.latticeBaseShape = cmds.listConnections(lattice + '.baseLatticeMatrix', sh=True)[0]
        self.latticeBase = cmds.listRelatives(self.latticeBaseShape, p=True)[0]

        # Get Lattice Data
        self.sDivisions = cmds.getAttr(self.latticeShape + '.sDivisions')
        self.tDivisions = cmds.getAttr(self.latticeShape + '.tDivisions')
        self.uDivisions = cmds.getAttr(self.latticeShape + '.uDivisions')
        self.latticeXform = cmds.xform(self.lattice, q=True, ws=True, m=True)

        # Get Lattice Base Data
        self.baseXform = cmds.xform(self.latticeBase, q=True, ws=True, m=True)

    def rebuild(self):
        """
        Rebuild the lattice deformer from the recorded deformerData
        """
        # Rebuild deformer
        ffd = cmds.lattice(self.getMemberList(), n=self.deformerName)
        lattice = ffd[0]
        latticeShape = ffd[1]
        latticeBase = ffd[2]

        # Set Deformer Attributes
        cmds.setAttr(lattice + '.local', self.local)
        cmds.setAttr(lattice + '.outsideLattice', self.outside)
        cmds.setAttr(lattice + '.outsideFalloffDist', self.falloff)
        cmds.setAttr(lattice + '.usePartialResolution', self.resolution)
        cmds.setAttr(lattice + '.partialResolution', self.partialResolution)
        cmds.setAttr(lattice + '.freezeGeometry', self.freeze)
        cmds.setAttr(lattice + '.localInfluenceS', self.localInfluenceS)
        cmds.setAttr(lattice + '.localInfluenceT', self.localInfluenceT)
        cmds.setAttr(lattice + '.localInfluenceU', self.localInfluenceU)

        # Set Lattice Shape Attributes
        cmds.setAttr(latticeShape + '.sDivisions', self.sDivisions)
        cmds.setAttr(latticeShape + '.tDivisions', self.tDivisions)
        cmds.setAttr(latticeShape + '.uDivisions', self.uDivisions)

        # Restore World Transform Data
        cmds.xform(lattice, ws=True, m=self.latticeXform)
        cmds.xform(latticeBase, ws=True, m=self.baseXform)

        # Return result
        return lattice
