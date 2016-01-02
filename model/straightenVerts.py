import maya.mel as mel
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import glTools.tools.extractCurves
import glTools.utils.base
import glTools.utils.blendShape
import glTools.utils.component
import glTools.utils.mathUtils
import glTools.utils.mesh
import glTools.utils.wire
import copy


def straightenVerts(edgeList,
                    falloff=0.01,
                    influence=1.0,
                    snapToOriginal=False,
                    keepEdgeSpacing=False,
                    deleteHistory=False):
    """
    Straighten specified polygon vertices.
    @param edgeList: List of polygon edges to straighten.
    @type edgeList: list
    @param falloff: Falloff distance around selected vertices.
    @type falloff: float
    @param snapToOriginal: Snap vertices back to closest point on original mesh.
    @type snapToOriginal: bool
    @param deleteHistory: Delete construction history.
    @type deleteHistory: bool
    """
    # Get Edge List
    edgeList = cmds.filterExpand(edgeList, ex=True, sm=32) or []
    if not edgeList:
        raise Exception('Invalid or empty edge list! Unable to straighten vertices...')

    # Build Edge Curve from Vertices
    edgeCrvList = glTools.tools.extractCurves.extractEdgeCurves(edgeList, keepHistory=False)
    straightCrvList = []
    for edgeCrv in edgeCrvList:

        # Build Straight Curve
        straightCrv = cmds.rebuildCurve(edgeCrv,
                                      ch=False,
                                      rpo=False,
                                      rt=0,
                                      end=1,
                                      kr=False,
                                      kcp=False,
                                      kep=True,
                                      kt=False,
                                      s=1,
                                      d=1,
                                      tol=0)[0]

        # Rebuild Straight Curve
        dist = []
        total = 0.0
        params = []
        pts = glTools.utils.base.getMPointArray(edgeCrv)
        max = cmds.getAttr(straightCrv + '.maxValue')
        if keepEdgeSpacing:
            for i in range(pts.length() - 1):
                d = (pts[i] - pts[i + 1]).length()
                dist.append(d)
                total += d
            for i in range(len(dist)):
                d = dist[i] / total * max
                if i: d += params[-1]
                params.append(d)
        else:
            params = glTools.utils.mathUtils.distributeValue(pts.length(), rangeEnd=max)[1:-1]

        params = [straightCrv + '.u[' + str(i) + ']' for i in params]
        cmds.insertKnotCurve(params, ch=False, numberOfKnots=1, add=True, ib=False, rpo=True)

        # Snap To Mesh
        mesh = cmds.ls(edgeList, o=True)[0]
        if snapToOriginal:
            pts = glTools.utils.component.getComponentStrList(straightCrv)
            glTools.utils.mesh.snapPtsToMesh(mesh, pts)

        # Append List
        straightCrvList.append(straightCrv)

    # =================
    # - Deform Points -
    # =================

    # Build Wire Deformer
    wire = glTools.utils.wire.createMulti(mesh, edgeCrvList, dropoffDist=falloff, prefix=mesh.split(':')[-1])
    cmds.setAttr(wire[0] + '.rotation', 0)

    # Blend to Straight Curve
    for i in range(len(edgeCrvList)):
        blendShape = glTools.utils.blendShape.create(baseGeo=edgeCrvList[i], targetGeo=[straightCrvList[i]])
        cmds.setAttr(blendShape + '.' + straightCrvList[i], influence)

    # ==================
    # - Delete History -
    # ==================

    if deleteHistory:
        wireBaseList = glTools.utils.wire.getWireBase(wire[0])
        cmds.delete(mesh, ch=True)
        for edgeCrv in edgeCrvList:
            if cmds.objExists(edgeCrv):
                cmds.delete(edgeCrv)
        for straightCrv in straightCrvList:
            if cmds.objExists(straightCrv):
                cmds.delete(straightCrv)
        for wireBase in wireBaseList:
            if cmds.objExists(wireBase):
                cmds.delete(wireBase)

    # =================
    # - Return Result -
    # =================

    if edgeList:
        cmds.hilite(mesh)
        cmds.select(edgeList)

    return edgeList


def straightenVertsUI():
    """
    Straighten Vertices UI
    """
    # Window
    window = 'straightenVertsUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Straighten Vertices', s=True)

    # Layout
    CL = cmds.columnLayout()

    # UI Elements
    cmds.floatSliderGrp('straightenVerts_falloffFSG', label='Falloff Distance', field=True, precision=3, minValue=0.0,
                      maxValue=10.0, fieldMinValue=0.0, fieldMaxValue=100.0, value=0.01)
    cmds.checkBoxGrp('straightenVerts_edgeSpacingCBG', label='Maintain Edge Spacing', numberOfCheckBoxes=1, v1=False)
    cmds.checkBoxGrp('straightenVerts_snapToOrigCBG', label='Maintain Shape', numberOfCheckBoxes=1,
                   v1=False)  # columnWidth2=[100,165]
    cmds.checkBoxGrp('straightenVerts_deleteHistoryCBG', label='Delete History', numberOfCheckBoxes=1, v1=False)
    cmds.button('straightenVertsB', l='Straighten', w=390, c='glTools.model.straightenVerts.straightenVertsFromUI()')

    # Show Window
    cmds.window(window, e=True, wh=[392, 92])
    cmds.showWindow(window)


def straightenVertsFromUI():
    """
    Straighten Vertices From UI
    """
    # Get Edge Selection
    sel = cmds.ls(sl=True, fl=True)
    edges = cmds.filterExpand(sel, ex=True, sm=32)
    verts = cmds.filterExpand(sel, ex=True, sm=31)
    if not edges and verts:
        cmds.select(verts)
        mel.eval('ConvertSelectionToContainedEdges')
        edges = cmds.filterExpand(ex=True, sm=32)
    if not edges:
        print('Select a list of connected vertices or edges and run again...')
        return

    # Get Mesh from vertices
    mesh = cmds.ls(edges, o=True)

    # Get UI Parameters
    falloff = cmds.floatSliderGrp('straightenVerts_falloffFSG', q=True, value=True)
    edgeSpacing = cmds.checkBoxGrp('straightenVerts_edgeSpacingCBG', q=True, v1=True)
    snapToOrig = cmds.checkBoxGrp('straightenVerts_snapToOrigCBG', q=True, v1=True)
    delHistory = cmds.checkBoxGrp('straightenVerts_deleteHistoryCBG', q=True, v1=True)

    # Straighten Vertices
    straightenVerts(edgeList=edges,
                    falloff=falloff,
                    keepEdgeSpacing=edgeSpacing,
                    snapToOriginal=snapToOrig,
                    deleteHistory=delHistory)

    # Restore Selection
    if sel:
        cmds.selectMode(component=True)
        cmds.selectType(edge=True)
        cmds.hilite(mesh)
        cmds.select(edges)


def evenEdgeSpacing(edgeList,
                    smooth=0,
                    influence=1.0,
                    snapToOrig=False,
                    deleteHistory=False):
    """
    @param edgeList: List of polygon edges to evenly space
    @type edgeList: list
    @param smooth: Number of smooth iterations to apply
    @type smooth: int
    @param influence: Amount of result to apply to original vertex positions
    @type influence: float
    @param snapToOrig: Snap points back to original mesh
    @type snapToOrig: bool
    @param deleteHistory: Delete construction history.
    @type deleteHistory: bool
    """
    # Get Edge List
    edgeList = cmds.filterExpand(edgeList, ex=True, sm=32) or []
    if not edgeList:
        raise Exception('Invalid or empty edge list! Unable to even edge spacing...')

    edgeCrvList = glTools.tools.extractCurves.extractEdgeCurves(edgeList, keepHistory=False)
    evenCrvList = []
    for edgeCrv in edgeCrvList:

        # Rebuild Even Curve
        evenCrv = cmds.rebuildCurve(edgeCrv,
                                  ch=False,
                                  rpo=False,
                                  rt=0,
                                  end=1,
                                  kr=False,
                                  kcp=False,
                                  kep=True,
                                  kt=False,
                                  s=0,
                                  d=1,
                                  tol=0)[0]

        # Smooth Curve
        if smooth: smoothCurve(evenCrv, smooth, True)

        # Snap To Mesh
        mesh = cmds.ls(edgeList, o=True)[0]
        if snapToOrig:
            pts = glTools.utils.component.getComponentStrList(evenCrv)
            glTools.utils.mesh.snapPtsToMesh(mesh, pts)

        evenCrvList.append(evenCrv)

    # Apply Even Spacing to Mesh Edge Vertices
    wire = glTools.utils.wire.createMulti(mesh, edgeCrvList, dropoffDist=0.01, prefix=mesh.split(':')[-1])
    cmds.setAttr(wire[0] + '.rotation', 0)
    cmds.setAttr(wire[0] + '.envelope', influence)

    # Blend to Even Curve
    for i in range(len(edgeCrvList)):
        blendShape = glTools.utils.blendShape.create(baseGeo=edgeCrvList[i], targetGeo=[evenCrvList[i]])
        cmds.setAttr(blendShape + '.' + evenCrvList[i], 1)

    # ==================
    # - Delete History -
    # ==================

    if deleteHistory:
        wireBaseList = glTools.utils.wire.getWireBase(wire[0])
        cmds.delete(mesh, ch=True)
        for edgeCrv in edgeCrvList:
            if cmds.objExists(edgeCrv):
                cmds.delete(edgeCrv)
        for evenCrv in evenCrvList:
            if cmds.objExists(evenCrv):
                cmds.delete(evenCrv)
        for wireBase in wireBaseList:
            if cmds.objExists(wireBase):
                cmds.delete(wireBase)

    # =================
    # - Return Result -
    # =================

    if edgeList:
        cmds.hilite(mesh)
        cmds.select(edgeList)

    return edgeList


def evenEdgeSpacingUI():
    """
    Even Edge Spacing UI
    """
    # Window
    window = 'evenEdgeSpacingUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Even Edge Spacing', s=True)

    # Layout
    CL = cmds.columnLayout()

    # UI Elements
    cmds.intSliderGrp('evenEdgeSpacing_smoothISG', label='Smooth', field=True, minValue=0, maxValue=20, fieldMinValue=0,
                    fieldMaxValue=100, value=4)
    cmds.floatSliderGrp('evenEdgeSpacing_influenceFSG', label='Influence', field=True, minValue=0.0, maxValue=1.0,
                      fieldMinValue=0.0, fieldMaxValue=1.0, value=1.0)
    cmds.checkBoxGrp('evenEdgeSpacing_snapToOrigCBG', label='Maintain Shape', numberOfCheckBoxes=1,
                   v1=False)  # columnWidth2=[100,165]
    cmds.checkBoxGrp('evenEdgeSpacing_deleteHistoryCBG', label='Delete History', numberOfCheckBoxes=1, v1=False)
    cmds.button('evenEdgeSpacingB', l='Even Edge Spacing', w=390,
              c='glTools.model.straightenVerts.evenEdgeSpacingFromUI()')

    # Show Window
    cmds.window(window, e=True, wh=[392, 99])
    cmds.showWindow(window)


def evenEdgeSpacingFromUI():
    """
    Even Edge Spacing From UI
    """
    # Get Edge Selection
    sel = cmds.ls(sl=True, fl=True)
    edges = cmds.filterExpand(sel, ex=True, sm=32)
    verts = cmds.filterExpand(sel, ex=True, sm=31)
    if not edges and verts:
        cmds.select(verts)
        mel.eval('ConvertSelectionToContainedEdges')
        edges = cmds.filterExpand(ex=True, sm=32)
    if not edges:
        print('Select a list of connected vertices or edges and run again...')
        return

    # Get Mesh from vertices
    mesh = cmds.ls(edges, o=True)

    # Get UI Parameters
    smooth = cmds.intSliderGrp('evenEdgeSpacing_smoothISG', q=True, v=True)
    influence = cmds.floatSliderGrp('evenEdgeSpacing_influenceFSG', q=True, v=True)
    snapToOrig = cmds.checkBoxGrp('evenEdgeSpacing_snapToOrigCBG', q=True, v1=True)
    delHistory = cmds.checkBoxGrp('evenEdgeSpacing_deleteHistoryCBG', q=True, v1=True)

    # Even Edge Spacing
    evenEdgeSpacing(edgeList=edges,
                    smooth=smooth,
                    influence=influence,
                    snapToOrig=snapToOrig,
                    deleteHistory=delHistory)

    # Restore Selection
    if sel:
        cmds.selectMode(component=True)
        cmds.selectType(edge=True)
        cmds.hilite(mesh)
        cmds.select(edges)


def smoothEdgeLine(edgeList,
                   smooth=4,
                   falloff=0.01,
                   snapToOrig=False,
                   keepEdgeSpacing=False,
                   deleteHistory=False):
    """
    """
    # Get Edge List
    edgeList = cmds.filterExpand(edgeList, ex=True, sm=32) or []
    if not edgeList:
        raise Exception('Invalid or empty edge list! Unable to even edge spacing...')

    edgeCrvList = glTools.tools.extractCurves.extractEdgeCurves(edgeList, keepHistory=False)
    smoothCrvList = []
    for edgeCrv in edgeCrvList:

        # Smooth Edge Line
        smoothCrv = cmds.duplicate(edgeCrv, n=edgeCrv + '_smoothed')[0]
        smoothCurve(crv=smoothCrv,
                    iterations=smooth,
                    keepEnds=True,
                    keepSpacing=keepEdgeSpacing)

        # Snap To Mesh
        mesh = cmds.ls(edgeList, o=True)[0]
        if snapToOrig:
            pts = glTools.utils.component.getComponentStrList(smoothCrv)
            glTools.utils.mesh.snapPtsToMesh(mesh, pts)

        # Append List
        smoothCrvList.append(smoothCrv)

    # Apply Smoothed Edge to Vertices
    wire = glTools.utils.wire.createMulti(mesh, edgeCrvList, dropoffDist=falloff, prefix=mesh.split(':')[-1])
    cmds.setAttr(wire[0] + '.rotation', 0)

    # Blend to Smooth Curve
    for i in range(len(edgeCrvList)):
        blendShape = glTools.utils.blendShape.create(baseGeo=edgeCrvList[i], targetGeo=[smoothCrvList[i]])
        cmds.setAttr(blendShape + '.' + smoothCrvList[i], 1)

    # ==================
    # - Delete History -
    # ==================

    if deleteHistory:
        wireBaseList = glTools.utils.wire.getWireBase(wire[0])
        cmds.delete(mesh, ch=True)
        for edgeCrv in edgeCrvList:
            if cmds.objExists(edgeCrv):
                cmds.delete(edgeCrv)
        for smoothCrv in smoothCrvList:
            if cmds.objExists(smoothCrv):
                cmds.delete(smoothCrv)
        for wireBase in wireBaseList:
            if cmds.objExists(wireBase):
                cmds.delete(wireBase)

    # =================
    # - Return Result -
    # =================

    if edgeList:
        cmds.hilite(mesh)
        cmds.select(edgeList)

    return edgeList


def smoothEdgeLineUI():
    """
    Smooth Edge Line UI
    """
    # Window
    window = 'smoothEdgesUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Smooth Edge Line', s=True)

    # Layout
    CL = cmds.columnLayout()

    # UI Elements
    cmds.intSliderGrp('smoothEdges_smoothISG', label='Smooth', field=True, minValue=1, maxValue=20, fieldMinValue=1,
                    fieldMaxValue=100, value=4)
    cmds.floatSliderGrp('smoothEdges_falloffFSG', label='Falloff Distance', field=True, precision=3, minValue=0.0,
                      maxValue=10.0, fieldMinValue=0.0, fieldMaxValue=100.0, value=0.01)
    cmds.checkBoxGrp('smoothEdges_edgeSpacingCBG', label='Maintain Edge Spacing', numberOfCheckBoxes=1, v1=False)
    cmds.checkBoxGrp('smoothEdges_snapToOrigCBG', label='Maintain Shape', numberOfCheckBoxes=1,
                   v1=False)  # columnWidth2=[100,165]
    cmds.checkBoxGrp('smoothEdges_deleteHistoryCBG', label='Delete History', numberOfCheckBoxes=1, v1=False)
    cmds.button('smoothEdgesB', l='Smooth', w=390, c='glTools.model.straightenVerts.smoothEdgeLineFromUI()')

    # Show Window
    cmds.window(window, e=True, wh=[392, 115])
    cmds.showWindow(window)


def smoothEdgeLineFromUI():
    """
    Smooth Edge Line From UI
    """
    # Get Edge Selection
    sel = cmds.ls(sl=True, fl=True)
    edges = cmds.filterExpand(sel, ex=True, sm=32)
    verts = cmds.filterExpand(sel, ex=True, sm=31)
    if not edges and verts:
        cmds.select(verts)
        mel.eval('ConvertSelectionToContainedEdges')
        edges = cmds.filterExpand(ex=True, sm=32)
    if not edges:
        print('Select a list of connected vertices or edges and run again...')
        return

    # Get Mesh from vertices
    mesh = cmds.ls(edges, o=True)

    # Get UI Parameters
    smooth = cmds.intSliderGrp('smoothEdges_smoothISG', q=True, v=True)
    falloff = cmds.floatSliderGrp('smoothEdges_falloffFSG', q=True, v=True)
    edgeSpacing = cmds.checkBoxGrp('smoothEdges_edgeSpacingCBG', q=True, v1=True)
    snapToOrig = cmds.checkBoxGrp('smoothEdges_snapToOrigCBG', q=True, v1=True)
    delHistory = cmds.checkBoxGrp('smoothEdges_deleteHistoryCBG', q=True, v1=True)

    # Smooth Edges
    smoothEdgeLine(edges,
                   smooth=smooth,
                   falloff=falloff,
                   snapToOrig=snapToOrig,
                   keepEdgeSpacing=edgeSpacing,
                   deleteHistory=delHistory)

    # Restore Selection
    if sel:
        cmds.selectMode(component=True)
        cmds.selectType(edge=True)
        cmds.hilite(mesh)
        cmds.select(edges)


def smoothLine(pts, iterations=1, keepEnds=True, keepSpacing=False):
    """
    Smooth Point Array
    @param pts: List of line point positions to smooth
    @type pts: list
    @param iterations: Number of smooth iterations to apply
    @type iterations: int
    @param keepEnds: Maintain end point positions
    @type keepEnds: bool
    @param keepSpacing: Maintain edge distance ratios
    @type keepSpacing: bool
    """
    # Smooth Iterations
    end = int(keepEnds)
    for it in range(iterations):
        ref = copy.deepcopy(pts)
        for i in range(end, len(pts) - end):
            curr = glTools.utils.base.getMPoint(ref[i])
            next = glTools.utils.base.getMPoint(ref[i + 1])
            prev = glTools.utils.base.getMPoint(ref[i - 1])
            if keepSpacing:
                nextDist = (curr - next).length()
                prevDist = (curr - prev).length()
                nextWt = prevDist / (nextDist + prevDist) * 0.6
                prevWt = nextDist / (nextDist + prevDist) * 0.6
                pt = (curr * 0.4) + OpenMaya.MVector(next * nextWt) + OpenMaya.MVector(prev * prevWt)
            else:
                pt = (curr * 0.4) + OpenMaya.MVector((next + OpenMaya.MVector(prev)) * 0.3)
            pts[i] = [pt.x, pt.y, pt.z]

    # Return Result
    return pts


def smoothCurve(crv, iterations, keepEnds=True, keepSpacing=False):
    """
    Smooth specified curve CVs.
    @param crv: Curve to smooth.
    @type crv: str
    @param iterations: Number of smooth iterations to apply
    @type iterations: int
    @param keepEnds: Maintain end point positions
    @type keepEnds: bool
    @param keepSpacing: Maintain edge distance ratios
    @type keepSpacing: bool
    """
    # Get Smoothed Points
    pts = smoothLine(pts=glTools.utils.base.getPointArray(crv),
                     iterations=iterations,
                     keepEnds=keepEnds,
                     keepSpacing=keepSpacing)

    # Flatten Smooth Points List
    ptsFlat = []
    [ptsFlat.extend(i) for i in pts]

    # Apply Smoothed Points
    cmds.setAttr(crv + '.cv[0:' + str(len(pts) - 1) + ']', *ptsFlat)
