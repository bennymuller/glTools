import maya.cmds as cmds
import glTools.tools.controlBuilder


def create(geo, prefix=''):
    """
    """
    # Check prefix
    if not prefix: prefix = geo

    # Create Deformer
    sMod = cmds.softMod(geo, n=prefix + '_softMod')
    sModHandle = sMod[1]
    sMod = sMod[0]
    sModBase = cmds.duplicate(sModHandle, po=True, n=prefix + '_softModBase')[0]

    # Get Handle pivot
    piv = cmds.xform(sModHandle, q=True, ws=True, rp=True)

    # Initiate Control Builder
    ctrlBuilder = glTools.tools.controlBuilder.ControlBuilder()

    # Create Base control
    base_grp = cmds.createNode('transform', n=prefix + '_softModBase_grp')
    base_ctrl = cmds.createNode('transform', n=prefix + '_softModBase_ctrl', p=base_grp)
    base_ctrlShape = ctrlBuilder.controlShape(base_ctrl, 'box', scale=2)

    # Create Offset control
    offset_grp = cmds.createNode('transform', n=prefix + '_softModOffset_grp', p=base_ctrl)
    offset_ctrl = cmds.createNode('transform', n=prefix + '_softModOffset_ctrl', p=offset_grp)
    offset_ctrlShape = ctrlBuilder.controlShape(offset_ctrl, 'sphere', scale=0.25)

    # Create Falloff control
    falloff_grp = cmds.createNode('transform', n=prefix + '_softModFalloff_grp', p=base_ctrl)
    falloff_ctrl = cmds.createNode('transform', n=prefix + '_softModFalloff_ctrl', p=falloff_grp)
    falloff_ctrlShape = ctrlBuilder.controlShape(falloff_ctrl, 'circle', scale=1)
    falloff_loc = cmds.spaceLocator(n=prefix + '_softModFalloff_loc')[0]
    cmds.parent(falloff_loc, falloff_ctrl)
    cmds.addAttr(falloff_ctrl, ln='radius', min=0.001, dv=1, k=True)
    cmds.setAttr(falloff_loc + '.v', 0)

    # Move hierarchy into place
    cmds.move(piv[0], piv[1], piv[2], base_grp, a=True)

    # Connect to deformer
    cmds.connectAttr(falloff_loc + '.worldPosition[0]', sMod + '.falloffCenter', f=True)
    cmds.connectAttr(falloff_ctrl + '.radius', sMod + '.falloffRadius', f=True)
    cmds.connectAttr(sModBase + '.worldInverseMatrix[0]', sMod + '.bindPreMatrix', f=True)

    # Parent and constrain softMod elements
    cmds.parentConstraint(offset_ctrl, sModHandle, mo=True)
    cmds.scaleConstraint(offset_ctrl, sModHandle, mo=True)
    cmds.parentConstraint(base_ctrl, sModBase, mo=True)
    cmds.scaleConstraint(base_ctrl, sModBase, mo=True)
    cmds.parent(sModHandle, sModBase)
    cmds.parent(sModBase, base_grp)

    # Return result
    return sMod
