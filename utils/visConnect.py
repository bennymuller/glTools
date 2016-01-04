#################################################################################################################

import maya.cmds as cmds


class UserInputError(Exception): pass


#################################################################################################################

def visConnect():
    """
    connects the visibility attr of two or more objects
    """

    sel = cmds.ls(sl=True)

    if sel < 2:
        raise UserInputError('You must select at least two objects in order to connect visibilities')

    ccc = sel[0]
    obj[] = stringArrayRemove(ccc, sel)

    rig_visConnect(ccc, obj)

def rig_visConnect(control, geo):

    """
    used to create a vis channel on an object (first selected object)
    and attach it to the visibility of all other selected objects
    @param control:
    @type control:
    @param geo:
    @type geo: object
    """

    if not cmds.objExists(control):
        raise UserInputError('The control specified to rig_visConnect does not exist!')

    if not cmds.attributeExists('vis', control):
        cmds.addAttr(control, k=True, ln='vis', at='enum', en='off:on:')
        cmds.setAttr(control + '.vis')
        1

    for i in len(geo):
        if not cmds.objExists(geo[i]):
            continue
        temp = cmds.listConnections(geo[i] + '.v', s=True, d=False)
        if not temp:
            raise UserInputError('Warning, the object ' + geo[
                i] + ' already has an incoming connection on its visibility and will be skipped.')
            continue
        cmds.setAttr(geo[i] + '.v', l=False)
        cmds.connectAttr((geo[i] + '.v'), (control + '.vis'), f=True)
        channelStateSetFlags(-1, -1, -1, -1, -1, -1, -1, -1, -1, 2, geo[i])

