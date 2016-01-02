import maya.cmds as cmds
import glTools.utils.surface


def create(samplePt, pntList, weightCalc=[True, True, True], prefix=None):
    """
    Generate the barycentric point weight setup based on the input arguments
    @param samplePt: The locator used to define the triangle sample point to generate weights for
    @type samplePt: str
    @param pntList: List of points to define triangle
    @type pntList: list
    @param weightCalc: List of booleans to define which point weights are calculated
    @type weightCalc: list
    @param prefix: String name prefix for all created nodes
    @type prefix: str
    """
    # ==========
    # - Checks -
    # ==========

    # Check Sample Point (Locator)
    if not cmds.objExists(samplePt):
        raise Exception('Sample point "' + samplePt + '" does not exist!!')

    # Check prefix
    if not prefix: prefix = 'barycentricPointWeight'

    # ========================
    # - Setup Full Area Calc -
    # ========================

    # Build pntFace surface
    pntFace = cmds.nurbsPlane(p=(0, 0, 0), ax=(0, 1, 0), d=1, ch=False, n=prefix + '_sample_surface')[0]
    pntLoc = glTools.utils.surface.locatorSurface(pntFace, prefix=prefix)
    cmds.delete(cmds.pointConstraint(pntList[0], pntLoc[0]))
    cmds.delete(cmds.pointConstraint(pntList[1], pntLoc[1]))
    cmds.delete(cmds.pointConstraint(pntList[2], pntLoc[2]))
    cmds.delete(cmds.pointConstraint(pntList[2], pntLoc[3]))

    # Attach follow pt
    followLoc = cmds.spaceLocator(n=prefix + '_follow_locator')[0]
    follow_cpos = cmds.createNode('closestPointOnSurface', n=prefix + '_closestPointOnSurface')
    cmds.connectAttr(samplePt + '.worldPosition[0]', follow_cpos + '.inPosition', f=True)
    cmds.connectAttr(pntFace + '.worldSpace[0]', follow_cpos + '.inputSurface', f=True)
    cmds.connectAttr(follow_cpos + '.position', followLoc + '.translate', f=True)

    # Calculate triArea
    triEdge1_pma = cmds.createNode('plusMinusAverage', n=prefix + '_triEdge1Vec_plusMinusAverage')
    triEdge2_pma = cmds.createNode('plusMinusAverage', n=prefix + '_triEdge2Vec_plusMinusAverage')
    cmds.setAttr(triEdge1_pma + '.operation', 2)  # Subtract
    cmds.setAttr(triEdge2_pma + '.operation', 2)  # Subtract
    cmds.connectAttr(pntLoc[1] + '.worldPosition[0]', triEdge1_pma + '.input3D[0]', f=True)
    cmds.connectAttr(pntLoc[0] + '.worldPosition[0]', triEdge1_pma + '.input3D[1]', f=True)
    cmds.connectAttr(pntLoc[2] + '.worldPosition[0]', triEdge2_pma + '.input3D[0]', f=True)
    cmds.connectAttr(pntLoc[0] + '.worldPosition[0]', triEdge2_pma + '.input3D[1]', f=True)

    triArea_vpn = cmds.createNode('vectorProduct', n=prefix + '_triArea_vectorProduct')
    cmds.setAttr(triArea_vpn + '.operation', 2)  # Cross Product
    cmds.connectAttr(triEdge1_pma + '.output3D', triArea_vpn + '.input1', f=True)
    cmds.connectAttr(triEdge2_pma + '.output3D', triArea_vpn + '.input2', f=True)

    triArea_dist = cmds.createNode('distanceBetween', n=prefix + '_triArea_distanceBetween')
    cmds.connectAttr(triArea_vpn + '.output', triArea_dist + '.point1', f=True)

    # =======================
    # - Setup Sub Area Calc -
    # =======================

    # Calculate triPt weights
    for i in range(3):

        # Check weight calculation (bool)
        if weightCalc[i]:
            # Calculate sub-TriArea
            pntEdge1_pma = cmds.createNode('plusMinusAverage', n=prefix + '_pt' + str(i) + 'Edge1Vec_plusMinusAverage')
            pntEdge2_pma = cmds.createNode('plusMinusAverage', n=prefix + '_pt' + str(i) + 'Edge2Vec_plusMinusAverage')
            cmds.setAttr(pntEdge1_pma + '.operation', 2)  # Subtract
            cmds.setAttr(pntEdge2_pma + '.operation', 2)  # Subtract
            cmds.connectAttr(pntLoc[(i + 1) % 3] + '.worldPosition[0]', pntEdge1_pma + '.input3D[0]', f=True)
            cmds.connectAttr(followLoc + '.worldPosition[0]', pntEdge1_pma + '.input3D[1]', f=True)
            cmds.connectAttr(pntLoc[(i + 2) % 3] + '.worldPosition[0]', pntEdge2_pma + '.input3D[0]', f=True)
            cmds.connectAttr(followLoc + '.worldPosition[0]', pntEdge2_pma + '.input3D[1]', f=True)

            pntArea_vpn = cmds.createNode('vectorProduct', n=prefix + '_pt' + str(i) + 'Area_vectorProduct')
            cmds.setAttr(pntArea_vpn + '.operation', 2)  # Cross Product
            cmds.connectAttr(pntEdge1_pma + '.output3D', pntArea_vpn + '.input1', f=True)
            cmds.connectAttr(pntEdge2_pma + '.output3D', pntArea_vpn + '.input2', f=True)

            pntArea_dist = cmds.createNode('distanceBetween', n=prefix + '_pt' + str(i) + 'Area_distanceBetween')
            cmds.connectAttr(pntArea_vpn + '.output', pntArea_dist + '.point1', f=True)

            # Divide ptArea by triArea to get weight
            pntWeight_mdn = cmds.createNode('multiplyDivide', n=prefix + '_pt' + str(i) + 'Weight_multiplyDivide')
            cmds.setAttr(pntWeight_mdn + '.operation', 2)  # Divide
            cmds.connectAttr(pntArea_dist + '.distance', pntWeight_mdn + '.input1X', f=True)
            cmds.connectAttr(triArea_dist + '.distance', pntWeight_mdn + '.input2X', f=True)

            # Add weight attribute to pntLoc
            cmds.addAttr(pntLoc[i], ln='weight', min=0.0, max=1.0, dv=0.0)
            cmds.connectAttr(pntWeight_mdn + '.outputX', pntLoc[i] + '.weight', f=True)

    # ============
    # - CLEAN UP -
    # ============

    # Group mesh locators
    pntLoc_grp = cmds.group(pntLoc, n=prefix + '_3Point_grp')
    cmds.parent(pntFace, pntLoc_grp)

    # Turn off inheritTransforms for tri point face
    cmds.setAttr(pntFace + '.inheritsTransform', 0)

    # Scale follow locator
    cmds.setAttr(followLoc + '.localScale', 0.05, 0.05, 0.05)

    # Parent and hide coincident locator
    cmds.parent(pntLoc[3], pntLoc[2])
    cmds.setAttr(pntLoc[3] + '.v', 0)

    # =================
    # - Return Result -
    # =================

    # Return result
    return [pntLoc, pntFace, pntLoc_grp]
