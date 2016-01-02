import maya.cmds as cmds


def timeWarp(anicmdsurves, prefix):
    """
    """
    # Check anim curves
    if not anicmdsurves: return

    # Get anim playback start and end
    st = cmds.playbackOptions(q=True, min=True)
    en = cmds.playbackOptions(q=True, max=True)

    # Create time warp curve
    timeWarpCrv = cmds.createNode('anicmdsurveTT', n=prefix + '_timeWarp')
    cmds.setKeyframe(timeWarpCrv, t=st, v=st)
    cmds.setKeyframe(timeWarpCrv, t=en, v=en)

    # Attach timeWarp
    for anicmdsurve in anicmdsurves:

        # Check curve type
        crvType = cmds.objectType(anicmdsurve)
        if crvType == 'anicmdsurveTL' or crvType == 'anicmdsurveTA' or crvType == 'anicmdsurveTU':
            cmds.connectAttr(timeWarpCrv + '.output', anicmdsurve + '.input', f=True)
