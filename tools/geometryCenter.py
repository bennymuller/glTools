import maya.cmds as cmds


def geometryCenterLocator(geo):
    """
    Create a locator attached the the bounding box ceter of the specified geometry
    @param geo: Geometry to connect the locator to
    @type geo: str
    """
    # Check geo
    if not cmds.objExists(geo):
        raise Exception('Geometry "' + geo + '" does not exist!')
    # Create Locator
    loc = cmds.spaceLocator(n=geo + '_center')

    # Determine geometry shape
    geoShape = cmds.listRelatives(geo, s=True, ni=True)
    if not geoShape:
        raise Exception('Unable to determine geoemtry shape for "' + geo + '"!')

    # Connect to geometry center
    cmds.connectAttr(geoShape[0] + '.center', loc[0] + '.translate', f=True)

    # Return result
    return loc[0]


def geometryBoundingBox(geo):
    """
    @param geo: Geometry to connect the bounding box to
    @type geo: str
    """
    # Check geometry
    if not cmds.objExists(geo):
        raise Exception('Geometry "' + geo + '" does not exist!')

    # Create Bounding Box
    bbox = cmds.polyCube(ch=False, n=geo + '_boundingBox')

    # Determine geometry shape
    geoShape = cmds.listRelatives(geo, s=True, ni=True)
    if not geoShape:
        raise Exception('Unable to determine geoemtry shape for "' + geo + '"!')

    # Connect to boundingBox
    cmds.connectAttr(geoShape[0] + '.center', bbox[0] + '.translate', f=True)
    cmds.connectAttr(geoShape[0] + '.boundingBoxSize', bbox[0] + '.scale', f=True)

    # Turn off boundingBox shading
    cmds.setAttr(geoShape[0] + '.overrideEnabled', 1)
    cmds.setAttr(geoShape[0] + '.overrideShading', 0)

    # Return result
    return bbox[0]
