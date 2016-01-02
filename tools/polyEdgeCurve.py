import maya.cmds as cmds
import glTools.utils.colorize


def buildMasterCurveGroup(grpName):
    """
    Build master group name
    @param grpName: Existing mocap namespace
    @type grpName: str
    """
    grp = grpName
    if not cmds.objExists(grpName): grp = cmds.group(em=True, n=grpName)
    return grp


def buildCurveGroup(name, color=None):
    """
    Build master group name
    @param name: Curve group name. Final group will be suffiex with "_grp"
    @type name: str
    @param color: Color to apply to the edge curve (group).
    @type color: int or str or None
    """
    grp = name + '_edgeCurves_grp'
    if not cmds.objExists(grp): grp = cmds.group(em=True, n=grp)
    if color: glTools.utils.colorize.colorize(grp, color)
    # cmds.setAttr(grp+'.overrideEnabled',1)
    # cmds.setAttr(grp+'.overrideDisplayType',2) # Reference
    return grp


def buildEdgeCurves(edges, name, color=None):
    """
    Build poly edge curves.
    Group, name and color resulting curves.
    @param edges: List of poly edges to extract as curves.
    @type edges: str
    @param name: Curve and group name prefix.
    @type name: str
    @param color: Color to apply to the edge curve (group).
    @type color: int or str or None
    """
    # Get Edges
    edges = cmds.filterExpand(ex=True, sm=32)  # Poly Edges
    if not edges: raise Exception('Invalid or empty edge list!')

    # Get Master Group
    masterGrp = buildMasterCurveGroup('edgeCurveGroup')

    # Get Curve Group
    curveGrp = buildCurveGroup(name, color)
    try:
        cmds.parent(curveGrp, masterGrp)
    except:
        pass

    # Build Edge Curves
    crvList = []
    for edge in edges:
        crv = cmds.polyToCurve(edge, form=2, degree=1)[0]
        for at in 'trs': cmds.setAttr(crv + '.' + at, l=True, cb=False)
        cmds.parent(crv, curveGrp)

    # Return Result
    return curveGrp


def buildEdgeCurvesUI():
    """
    Build Edge Curves UI
    """
    # Window
    window = 'buildEdgeCurvesUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Build PolyEdge Curves', s=True)

    # Layout
    CL = cmds.columnLayout()

    # UI Elements
    cmds.textFieldGrp('buildEdgeCurves_nameTFG', label='Curve Group Name', text='', editable=True)
    cmds.colorIndexSliderGrp('buildEdgeCurves_colorCISG', label="Curve Color", min=1, max=32, value=16)
    cmds.button('buildEdgeCurvesB', l='Create', w=390, c='glTools.tools.polyEdgeCurve.buildEdgeCurvesFromUI()')

    # Show Window
    cmds.window(window, e=True, wh=[392, 64])
    cmds.showWindow(window)


def buildEdgeCurvesFromUI():
    """
    Build Edge Curves From UI
    """
    # Get Selected Edges
    sel = cmds.ls(sl=True, fl=True)
    edges = cmds.filterExpand(sel, ex=True, sm=32)
    if not edges:
        print('Invalid Selection! Select polygon edges and run again...')
        return

    # Get UI Parameters
    name = cmds.textFieldGrp('buildEdgeCurves_nameTFG', q=True, text=True)
    color = cmds.colorIndexSliderGrp('buildEdgeCurves_colorCISG', q=True, v=True) - 1

    # Build Edge Curves
    crvGrp = buildEdgeCurves(edges, name, color)
    cmds.select(crvGrp)
