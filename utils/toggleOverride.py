import maya.cmds as cmds


def ui():
    """
    Toggles override display state of selected element surfaces
    Open existing asset scene, select a control on your asset(example - supermover)
    Launch toggleOverride_GUI from the rigTools menu, select the options you want and execute.

    @keyword: rig, cfin, utilities, gui, interface, window

        @appVersion: 8.5, 2008
    """

    if cmds.window('toggleUIwin', q=1, ex=1):
        cmds.deleteUI('toggleUIwin')

    uiWidth = 500
    uiHeight = 200

    # VERY IMPORTANT TO TURN OFF "REMEMBER SIZE AND POSITION" IN PREFERENCES

    # define the interface

    toggleUI = cmds.window('toggleUIwin', title='toggleOverride_GUI - v.5', iconName='toggleOverride_GUI', w=uiWidth,
                         h=uiHeight, resizeToFitChildren=False)

    cmds.frameLayout(marginHeight=30, labelVisible=0, borderStyle='out')

    genForm = cmds.formLayout(numberOfDivisions=100)

    genColumn = cmds.columnLayout(adjustableColumn=True, rowSpacing=5)

    cmds.rowLayout(nc=4, cat=[(1, 'right', 5), (2, 'both', 5), (3, 'right', 5), (4, 'both', 5)],
                 cw=[(1, 100), (2, 110), (3, 100), (4, 100)])

    cmds.text(label='Toggle To', annotation='select PolyCage toggle type.')

    cmds.optionMenu('polyToggleTypeDropdown', label='')

    ## should read these values to find the current state
    cmds.menuItem(label='Normal')
    cmds.menuItem(label='Template')
    cmds.menuItem(label='Reference')

    # back up to Column Layout
    cmds.setParent('..')

    cmds.rowLayout(nc=2, cat=[(1, 'right', 116)], cw=[(1, 305), (2, 305)])

    radioPolyEnableOverrides = cmds.checkBox('polyEnable', v=True, label='overrides', h=30)

    # back up to Column Layout
    cmds.setParent('..')

    cmds.rowLayout(nc=2, cat=[(1, 'right', 128)], cw=[(1, 305), (2, 305)])

    radioPolyEnableShadingOverrides = cmds.checkBox('polyEnableShading', v=True, label='shading', h=30)

    # back up to Column Layout
    cmds.setParent('..')

    cmds.rowLayout(nc=2, cat=[(1, 'right', 116), (2, 'right', 290)], cw=[(1, 305), (2, 305)])

    ok = cmds.button(w=85, h=30, backgroundColor=(0, 1, 0), al='center',
                   command='glTools.utils.toggleOverride.toggleOverride_WRP()', label='OK')

    cancel = cmds.button(w=85, h=30, backgroundColor=(1, 0, 0), al='center', command='cmds.deleteUI("' + toggleUI + '")',
                       label='Cancel')

    # tell Maya to draw the window
    cmds.showWindow('toggleUIwin')


def toggleOverride_WRP():
    """
    Wrapper to execute toggleOverride with inputs from
    toggleOverride_GUI

    @keyword: rig, cfin, utilities, gui, interface, window

        @appVersion: 8.5, 2008

    """

    sel = cmds.ls(sl=True)

    mEnableOverrides = cmds.checkBox('polyEnable', q=True, v=True)
    mDisplayMode = cmds.optionMenu('polyToggleTypeDropdown', q=True, select=True)
    mEnableShading = cmds.checkBox('polyEnableShading', q=True, v=True)

    if not len(sel):
        raise Exception('error You must select a control in order to toggle display override on!')

    toggleOverride(sel[0], 'model', mEnableOverrides, (mDisplayMode - 1), mEnableShading)


def toggleOverride(assetNode, geoGroup, enableOverrides, displayMode, enableShading):
    """
    executable for toggleOverride. The executable needs to be given a node
    from the asset in your scene to perform the operation on
    available modes are as follows:
        Normal(0) - geometry is selectable
        Template(1) - geometry is in template mode
        Reference(2) - geometry is in reference mode

    @param assetNode: Node on the asset on which to toggleOverrides
    @type assetNode: str
    @param geoGroup: Node which contains all meshes for asset
    @type geoGroup: str
    @param enableOverrides: 1 or 0 to enable the overrides. Default is on
    @type enableOverrides: int
    @param displayNode: 0, 1, or 2 to define modes
    @type displayNode: int
    @param enableShading: 1 or 0 to enable the shading. Default is on.
    @type: displayNode: int

    @keyword: rig, cfin, utilities, gui, interface, window

    @example: toggleOverride jack:cn_hed01_ccc model 1 2 1;

        @appVersion: 8.5, 2008
    """

    ##find all the geo in that group
    if not cmds.objExists(assetNode): raise Exception('')
    if assetNode.count(':'):
        geoGroup = assetNode.split(':')[0] + ':' + geoGroup

    if not cmds.objExists(geoGroup): raise Exception('')
    geo = cmds.listRelatives(geoGroup, ad=1, ni=1, typ=['mesh', 'nurbsSurface'])

    ##cycle through that geo and set its state based on the mode, overrides, and shading
    for shape in geo:
        cmds.setAttr(shape + ".overrideEnabled", enableOverrides)
        if (enableOverrides):
            cmds.setAttr(shape + ".overrideShading", enableShading)
            cmds.setAttr(shape + ".overrideDisplayType", displayMode)

    ##finished
    print 'Done toggling overrides'
