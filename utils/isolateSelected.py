import maya.cmds as cmds


def getPanel():
    """
    Get current model panel with focus
    """
    # Get Panel with Focus
    panel = cmds.getPanel(wf=True)

    # Check Model Panel
    if not cmds.modelPanel(panel, q=True, ex=True):
        panel = cmds.getPanel(type='modelPanel')[0]

    # Return Result
    return panel


def isolate(state, sel=None, panel=None):
    """
    Isolated selected objects in the specified model panel
    @param state: Rig namespace to bake mocap override keys for.
    @type state: bool
    @param sel: List of objects to isolate in the viewport. If [], use current selection. If None, show nothing.
    @type sel: list
    @param panel: The model viewport to enable isolateSelected for. If empty, use model panel with focus.
    @type panel: str
    """
    # ==========
    # - Checks -
    # ==========

    # Check Selection
    if (sel != None) and (not sel): sel = cmds.ls(sl=1)

    # Check Panel
    if not panel:
        try:
            panel = getPanel()
        except:
            print('Unable to determine model panel! Aborting...')
            return

    # ====================
    # - Isolate Selected -
    # ====================

    if state:

        # Clear Selection
        cmds.select(cl=True)

        # Isolate Selected - Enable
        cmds.isolateSelect(panel, state=True)

        # Update Selection
        if sel: cmds.select(sel)

        # Load Selected
        cmds.isolateSelect(panel, loadSelected=True)

        # Update Isolate Set
        cmds.isolateSelect(panel, update=True)

    else:

        # Isolate Selected - Disable
        cmds.isolateSelect(panel, state=False)


def getPanelVis(panel=None):
    """
    Get list of viewport display options.
    @param panel: The model viewport to get visibility options from.
    @type panel: str
    """
    # Check Panel
    if not panel: panel = getPanel()

    # Get Panel Vis
    panelVis = []
    panelVis.append(cmds.modelEditor(panel, q=True, nurbsCurves=True))
    panelVis.append(cmds.modelEditor(panel, q=True, nurbsSurfaces=True))
    panelVis.append(cmds.modelEditor(panel, q=True, polymeshes=True))
    panelVis.append(cmds.modelEditor(panel, q=True, subdivSurfaces=True))
    panelVis.append(cmds.modelEditor(panel, q=True, planes=True))
    panelVis.append(cmds.modelEditor(panel, q=True, lights=True))
    panelVis.append(cmds.modelEditor(panel, q=True, cameras=True))
    panelVis.append(cmds.modelEditor(panel, q=True, controlVertices=True))
    panelVis.append(cmds.modelEditor(panel, q=True, grid=True))
    panelVis.append(cmds.modelEditor(panel, q=True, hulls=True))
    panelVis.append(cmds.modelEditor(panel, q=True, joints=True))
    panelVis.append(cmds.modelEditor(panel, q=True, ikHandles=True))
    panelVis.append(cmds.modelEditor(panel, q=True, deformers=True))
    panelVis.append(cmds.modelEditor(panel, q=True, dynamics=True))
    panelVis.append(cmds.modelEditor(panel, q=True, fluids=True))
    panelVis.append(cmds.modelEditor(panel, q=True, hairSystems=True))
    panelVis.append(cmds.modelEditor(panel, q=True, follicles=True))
    panelVis.append(cmds.modelEditor(panel, q=True, nCloths=True))
    panelVis.append(cmds.modelEditor(panel, q=True, nParticles=True))
    panelVis.append(cmds.modelEditor(panel, q=True, nRigids=True))
    panelVis.append(cmds.modelEditor(panel, q=True, dynamicConstraints=True))
    panelVis.append(cmds.modelEditor(panel, q=True, locators=True))
    panelVis.append(cmds.modelEditor(panel, q=True, manipulators=True))
    panelVis.append(cmds.modelEditor(panel, q=True, dimensions=True))
    panelVis.append(cmds.modelEditor(panel, q=True, handles=True))
    panelVis.append(cmds.modelEditor(panel, q=True, pivots=True))
    panelVis.append(cmds.modelEditor(panel, q=True, textures=True))
    panelVis.append(cmds.modelEditor(panel, q=True, strokes=True))
    return panelVis


def setPanelVis(panel, panelVis):
    """
    Set specified viewport display options based on the provided list of values.
    @param panel: The model viewport to set visibility options for.
    @type panel: str
    @param panelVis: List of panel visibility option values. See getPanelVis() for list order.
    @type panelVis: list
    """
    cmds.modelEditor(panel, e=True, nurbsCurves=panelVis[0])
    cmds.modelEditor(panel, e=True, nurbsSurfaces=panelVis[1])
    cmds.modelEditor(panel, e=True, polymeshes=panelVis[2])
    cmds.modelEditor(panel, e=True, subdivSurfaces=panelVis[3])
    cmds.modelEditor(panel, e=True, planes=panelVis[4])
    cmds.modelEditor(panel, e=True, lights=panelVis[5])
    cmds.modelEditor(panel, e=True, cameras=panelVis[6])
    cmds.modelEditor(panel, e=True, controlVertices=panelVis[7])
    cmds.modelEditor(panel, e=True, grid=panelVis[8])
    cmds.modelEditor(panel, e=True, hulls=panelVis[9])
    cmds.modelEditor(panel, e=True, joints=panelVis[10])
    cmds.modelEditor(panel, e=True, ikHandles=panelVis[11])
    cmds.modelEditor(panel, e=True, deformers=panelVis[12])
    cmds.modelEditor(panel, e=True, dynamics=panelVis[13])
    cmds.modelEditor(panel, e=True, fluids=panelVis[14])
    cmds.modelEditor(panel, e=True, hairSystems=panelVis[15])
    cmds.modelEditor(panel, e=True, follicles=panelVis[16])
    cmds.modelEditor(panel, e=True, nCloths=panelVis[17])
    cmds.modelEditor(panel, e=True, nParticles=panelVis[18])
    cmds.modelEditor(panel, e=True, nRigids=panelVis[19])
    cmds.modelEditor(panel, e=True, dynamicConstraints=panelVis[20])
    cmds.modelEditor(panel, e=True, locators=panelVis[21])
    cmds.modelEditor(panel, e=True, manipulators=panelVis[22])
    cmds.modelEditor(panel, e=True, dimensions=panelVis[23])
    cmds.modelEditor(panel, e=True, handles=panelVis[24])
    cmds.modelEditor(panel, e=True, pivots=panelVis[25])
    cmds.modelEditor(panel, e=True, textures=panelVis[26])
    cmds.modelEditor(panel, e=True, strokes=panelVis[27])


def disablePanelVis(panel):
    """
    Disable all viewport display options for the specified viewport panel.
    @param panel: The model viewport to disable visibility options for.
    @type panel: str
    """
    cmds.modelEditor(panel, e=True, nurbsCurves=False)
    cmds.modelEditor(panel, e=True, nurbsSurfaces=False)
    cmds.modelEditor(panel, e=True, polymeshes=False)
    cmds.modelEditor(panel, e=True, subdivSurfaces=False)
    cmds.modelEditor(panel, e=True, planes=False)
    cmds.modelEditor(panel, e=True, lights=False)
    cmds.modelEditor(panel, e=True, cameras=False)
    cmds.modelEditor(panel, e=True, controlVertices=False)
    cmds.modelEditor(panel, e=True, grid=False)
    cmds.modelEditor(panel, e=True, hulls=False)
    cmds.modelEditor(panel, e=True, joints=False)
    cmds.modelEditor(panel, e=True, ikHandles=False)
    cmds.modelEditor(panel, e=True, deformers=False)
    cmds.modelEditor(panel, e=True, dynamics=False)
    cmds.modelEditor(panel, e=True, fluids=False)
    cmds.modelEditor(panel, e=True, hairSystems=False)
    cmds.modelEditor(panel, e=True, follicles=False)
    cmds.modelEditor(panel, e=True, nCloths=False)
    cmds.modelEditor(panel, e=True, nParticles=False)
    cmds.modelEditor(panel, e=True, nRigids=False)
    cmds.modelEditor(panel, e=True, dynamicConstraints=False)
    cmds.modelEditor(panel, e=True, locators=False)
    cmds.modelEditor(panel, e=True, manipulators=False)
    cmds.modelEditor(panel, e=True, dimensions=False)
    cmds.modelEditor(panel, e=True, handles=False)
    cmds.modelEditor(panel, e=True, pivots=False)
    cmds.modelEditor(panel, e=True, textures=False)
    cmds.modelEditor(panel, e=True, strokes=False)


def disableAllPanelVis():
    """
    Disable and store visibilty of all items for all model panels.
    """
    # Get Visible Panels
    panels = cmds.getPanel(type='modelPanel') or []

    # Store/Disable Panel Vis States
    panelVis = {}
    for panel in panels:
        panelVis[panel] = getPanelVis(panel=panel)
        disablePanelVis(panel)

    # Return Result
    return panelVis


def enableAllPanelVis(panelVis):
    """
    Restore and enable visibilty of all items for all model panels.
    @param panelVis: The model panel visibility state dictionary.
    @type panelVis: dict
    """
    # Get Stored Panel List
    panels = panelVis.keys() or []

    # Restore/Enable Panel Vis States
    for panel in panels:
        if cmds.modelPanel(panel, q=True, ex=True):
            setPanelVis(panel, panelVis[panel])

    # Return Result
    return panels
