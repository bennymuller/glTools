import maya.cmds as cmds
import glTools.utils.mesh


def pointSampleWeight(samplePt, pntList, weightCalc=[True, True, True], prefix=''):
    """
    """
    # Check prefix
    if not prefix: prefix = 'triSampleWeight'

    # Get tri points
    posList = [cmds.xform(pntList[0], q=True, ws=True, rp=True),
               cmds.xform(pntList[1], q=True, ws=True, rp=True),
               cmds.xform(pntList[2], q=True, ws=True, rp=True)]

    # Build pntFace mesh
    pntFace = cmds.polyCreateFacet(p=posList, n=prefix + '_sample_mesh')[0]
    cmds.setAttr(pntFace + '.inheritsTransform', 0, l=True)

    # Attach triPt locator to pntFace mesh
    pntLoc = glTools.utils.mesh.locatorMesh(pntFace, prefix=prefix)

    # Attach follow pt
    followLoc = cmds.spaceLocator(n=prefix + '_follow_locator')[0]
    followGeoCon = cmds.geometryConstraint(pntFace, followLoc)
    followPntCon = cmds.pointConstraint(samplePt, followLoc)

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

    # Calculate triPt weights
    for i in range(3):

        # Check weight calculation (bool)
        if weightCalc[i]:
            # Calculate triArea
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

    # Group mesh locators
    pntLoc_grp = cmds.group(pntLoc, n=prefix + '_3Point_grp')
    cmds.parent(pntFace, pntLoc_grp)

    # Return result
    return [pntLoc, pntFace, pntLoc_grp]
