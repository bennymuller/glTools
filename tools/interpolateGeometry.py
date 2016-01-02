import maya.cmds as cmds
import random


def interpolateGeometry(geoList, numGeo, prefix='interpGeo'):
    """
    """
    # Initialize outoput list
    dupGeoList = []

    # Generate base Geo
    baseGeo = cmds.duplicate(geoList[0], n=prefix + '_baseGeo')[0]
    baseTargetList = geoList[1:]
    baseBlendShape = cmds.blendShape(baseTargetList, baseGeo)[0]
    baseBlendAlias = cmds.listAttr(baseBlendShape + '.w', m=True)
    baseBlendCount = len(baseBlendAlias)
    baseBlendWeight = 1.0 / baseBlendCount
    for i in range(baseBlendCount): cmds.setAttr(baseBlendShape + '.' + baseBlendAlias[i], baseBlendWeight)

    # Generate interpolated geometry
    for i in range(numGeo):

        # Duplicate Geo as blended
        intGeo = cmds.duplicate(baseGeo, n=prefix + '#')[0]
        cmds.parent(intGeo, w=True)

        # Blend to source geometry
        intBlendShape = cmds.blendShape(geoList, intGeo)[0]
        intBlendAlias = cmds.listAttr(intBlendShape + '.w', m=True)
        intBlendCount = len(intBlendAlias)

        # Generate blend weights
        wt = []
        wtTotal = 0.0
        for i in range(intBlendCount):
            wt.append(random.random())
            wtTotal += wt[-1]
        for i in range(len(wt)):
            wt[i] /= wtTotal

        # Assign blend weights
        for i in range(intBlendCount):
            cmds.setAttr(intBlendShape + '.' + intBlendAlias[i], wt[i])

        # Append output list
        dupGeoList.append(intGeo)

    # Delete base Geo
    cmds.delete(baseGeo)

    # Return result
    return dupGeoList
