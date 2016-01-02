import maya.cmds as cmds
import glTools.ui.utils
import glTools.utils.lidSurface


class UIError(Exception): pass


# LidSurface Create ===============

def lidSurfaceCreateUI():
    """
    LidSurface Create UI
    """
    # Create Window
    win = 'lidSurfaceCreateUI'
    if cmds.window(win, q=True, ex=True): cmds.deleteUI(win)
    win = cmds.window(win, t='Create LidSurface')

    # Layout
    FL = cmds.formLayout(numberOfDivisions=100)

    # Curve List
    crvListTXT = cmds.text(l='Curve List')
    crvListTSL = cmds.textScrollList('lidSurface_crvListTSL', ams=True)
    crvListAddB = cmds.button(l='Add', c='glTools.ui.utils.addToTSL("' + crvListTSL + '")')
    crvListRemB = cmds.button(l='Remove', c='glTools.ui.utils.removeFromTSL("' + crvListTSL + '")')

    # Prefix
    prefixTFG = cmds.textFieldGrp('lidSurface_prefixTFG', l='Prefix', tx='')
    # Side
    sideTFG = cmds.textFieldGrp('lidSurface_sideTFG', l='Side', tx='lf')

    # Spans
    spansFSG = cmds.intSliderGrp('lidSurface_spansFSG', label='Spans', field=True, minValue=2, maxValue=10,
                               fieldMinValue=0, fieldMaxValue=100, value=4)

    # Attribute Object
    attrObjTFB = cmds.textFieldButtonGrp('lidSurface_attrObjTFB', l='Attribute Object', bl='Load Sel')
    # Collision Object
    collObjTFB = cmds.textFieldButtonGrp('lidSurface_collObjTFB', l='Collision Object', bl='Load Sel')

    # Create / Close
    createB = cmds.button(l='Create', c='')
    closeB = cmds.button(l='Close', c='cmds.deleteUI("' + win + '")')

    # UI Callbacks
    cmds.textScrollList(crvListTSL, e=True, dkc='glTools.ui.utils.removeFromTSL("' + crvListTSL + '")')
    cmds.textFieldGrp(prefixTFG, e=True, cc='glTools.ui.lidSurface.lidSurfaceCreate_updateSide()')
    cmds.textFieldButtonGrp(attrObjTFB, e=True, bc='glTools.ui.utils.loadObjectSel("' + attrObjTFB + '")')
    cmds.textFieldButtonGrp(collObjTFB, e=True, bc='glTools.ui.utils.loadObjectSel("' + collObjTFB + '")')

    # FormLayout - MAIN
    cmds.formLayout(FL, e=True, af=[(crvListTXT, 'left', 5), (crvListTXT, 'top', 5)], ap=[(crvListTXT, 'right', 5, 30)])
    cmds.formLayout(FL, e=True, af=[(crvListRemB, 'left', 5), (crvListRemB, 'bottom', 5)],
                  ap=[(crvListRemB, 'right', 5, 30)])
    cmds.formLayout(FL, e=True, af=[(crvListAddB, 'left', 5)], ap=[(crvListAddB, 'right', 5, 30)],
                  ac=[(crvListAddB, 'bottom', 5, crvListRemB)])
    cmds.formLayout(FL, e=True, af=[(crvListTSL, 'left', 5)], ap=[(crvListTSL, 'right', 5, 30)],
                  ac=[(crvListTSL, 'top', 5, crvListTXT), (crvListTSL, 'bottom', 5, crvListAddB)])
    cmds.formLayout(FL, e=True, af=[(prefixTFG, 'right', 5), (prefixTFG, 'top', 5)], ap=[(prefixTFG, 'left', 5, 30)])
    cmds.formLayout(FL, e=True, af=[(sideTFG, 'right', 5)], ap=[(sideTFG, 'left', 5, 30)],
                  ac=[(sideTFG, 'top', 5, prefixTFG)])
    cmds.formLayout(FL, e=True, af=[(spansFSG, 'right', 5)], ap=[(spansFSG, 'left', 5, 30)],
                  ac=[(spansFSG, 'top', 5, sideTFG)])
    cmds.formLayout(FL, e=True, af=[(attrObjTFB, 'right', 5)], ap=[(attrObjTFB, 'left', 5, 30)],
                  ac=[(attrObjTFB, 'top', 5, spansFSG)])
    cmds.formLayout(FL, e=True, af=[(collObjTFB, 'right', 5)], ap=[(collObjTFB, 'left', 5, 30)],
                  ac=[(collObjTFB, 'top', 5, attrObjTFB)])
    cmds.formLayout(FL, e=True, af=[(closeB, 'right', 5), (closeB, 'bottom', 5)], ap=[(closeB, 'left', 5, 30)])
    cmds.formLayout(FL, e=True, af=[(createB, 'right', 5)], ap=[(createB, 'left', 5, 30)],
                  ac=[(createB, 'bottom', 5, closeB)])

    # Show Window
    cmds.showWindow(win)


def lidSurfaceCreateFromUI():
    """
    """
    # Check window
    win = 'lidSurfaceCreateUI'
    if cmds.window(win, q=True, ex=True): raise UIError('LidSurface Create UI does not exist!')

    # Get UI values
    crvList = cmds.textScrollList('lidSurface_crvListTSL', q=True, ai=True)
    spans = cmds.intSliderGrp('lidSurface_spansFSG', q=True, v=True)
    attrObj = cmds.textFieldButtonGrp('lidSurface_attrObjTFB', q=True, tx=True)
    collObj = cmds.textFieldButtonGrp('lidSurface_collObjTFB', q=True, tx=True)
    side = cmds.textFieldGrp('lidSurface_sideTFG', q=True, tx=True)
    prefix = cmds.textFieldGrp('lidSurface_prefixTFG', q=True, tx=True)

    # Execute command
    glTools.utils.lidSurface.lidSurface_create(curveList=crvList, spans=spans, attributeObject=attrObj,
                                               collisionObject=collObj, side=side, prefix=prefix)


def lidSurfaceCreate_updateSide():
    """
    LidSurface Create UI method
    Updates the side text field based on updates to the prefix text field
    """
    prefix = cmds.textFieldGrp('lidSurface_prefixTFG', q=True, tx=True)
    if prefix:
        side = prefix.split('_')[0]
        if side:
            cmds.textFieldGrp('lidSurface_sideTFG', e=True, tx=side)


# LidSurface 3 Control Setup ===============

def threeCtrlSetupUI():
    """
    """
    pass


def threeCtrlSetupFromUI():
    """
    """
    pass


# LidSurface 4 Control Setup ===============

def fourCtrlSetupUI():
    """
    """
    pass


def fourCtrlSetupFromUI():
    """
    """
    pass
