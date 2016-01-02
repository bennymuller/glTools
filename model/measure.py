import maya.cmds as cmds


def measureBoundingBox(geo):
    """
    Create visual distance dimensions for the specified geometry or geometry group.
    @param geo: Geometry or geometry group to create distance dimensions for.
    @type geo: str
    """
    # Check Geo
    if not cmds.objExists(geo): raise Exception('Geometry "' + geo + '" does not exist!!')

    # ==============================
    # - Create Distance Dimensions -
    # ==============================

    del_locs = []

    # Height
    hDimensionShape = cmds.distanceDimension(sp=(0, 0, 0), ep=(1, 1, 1))
    locs = cmds.listConnections(hDimensionShape, s=True, d=False) or []
    del_locs += locs
    hDimension = cmds.listRelatives(hDimensionShape, p=True)[0]
    hDimension = cmds.rename(hDimension, geo + '_height_measure')

    # Width
    wDimensionShape = cmds.distanceDimension(sp=(0, 0, 0), ep=(1, 1, 1))
    locs = cmds.listConnections(wDimensionShape, s=True, d=False) or []
    del_locs += locs
    wDimension = cmds.listRelatives(wDimensionShape, p=True)[0]
    wDimension = cmds.rename(wDimension, geo + '_width_measure')

    # Depth
    dDimensionShape = cmds.distanceDimension(sp=(0, 0, 0), ep=(1, 1, 1))
    locs = cmds.listConnections(dDimensionShape, s=True, d=False) or []
    del_locs += locs
    dDimension = cmds.listRelatives(dDimensionShape, p=True)[0]
    dDimension = cmds.rename(dDimension, geo + '_depth_measure')

    # Group
    measure_grp = cmds.group([hDimension, wDimension, dDimension], n=geo + '_measure_grp')

    # ===============================
    # - Connect Distance Dimensions -
    # ===============================

    # Height
    cmds.connectAttr(geo + '.boundingBoxMin', hDimension + '.startPoint', f=True)
    addHeightNode = cmds.createNode('plusMinusAverage', n=geo + '_height_plusMinusAverage')
    cmds.connectAttr(geo + '.boundingBoxMin', addHeightNode + '.input3D[0]', f=True)
    cmds.connectAttr(geo + '.boundingBoxSizeY', addHeightNode + '.input3D[1].input3Dy', f=True)
    cmds.connectAttr(addHeightNode + '.output3D', hDimension + '.endPoint', f=True)

    # Width
    cmds.connectAttr(geo + '.boundingBoxMin', wDimension + '.startPoint', f=True)
    addWidthNode = cmds.createNode('plusMinusAverage', n=geo + '_width_plusMinusAverage')
    cmds.connectAttr(geo + '.boundingBoxMin', addWidthNode + '.input3D[0]', f=True)
    cmds.connectAttr(geo + '.boundingBoxSizeX', addWidthNode + '.input3D[1].input3Dx', f=True)
    cmds.connectAttr(addWidthNode + '.output3D', wDimension + '.endPoint', f=True)

    # Depth
    cmds.connectAttr(geo + '.boundingBoxMin', dDimension + '.startPoint', f=True)
    addDepthNode = cmds.createNode('plusMinusAverage', n=geo + '_depth_plusMinusAverage')
    cmds.connectAttr(geo + '.boundingBoxMin', addDepthNode + '.input3D[0]', f=True)
    cmds.connectAttr(geo + '.boundingBoxSizeZ', addDepthNode + '.input3D[1].input3Dz', f=True)
    cmds.connectAttr(addDepthNode + '.output3D', dDimension + '.endPoint', f=True)

    # Delete Unused Locators
    if del_locs: cmds.delete(del_locs)

    # Return Result
    return measure_grp
