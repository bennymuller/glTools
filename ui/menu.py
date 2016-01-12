import maya.cmds as cmds
import maya.mel as mel

def create():
    """
    This generates the menu for all rigTools.
    """
    # This is a temporary hack to get maya to evaluate $gMainWindow
    gMainWindow = mel.eval('string $temp = $gMainWindow')
    if cmds.menu('rigToolsMenu', q=True, ex=True): cmds.deleteUI('rigToolsMenu')

    if (len(gMainWindow)):
        cmds.setParent(gMainWindow)
        cmds.menu('rigToolsMenu', label='Rig Tools', tearOff=True, allowOptionBoxes=True)

        # ----------------------------------------#

        # > CHECKS
        cmds.menuItem(label='Checks', subMenu=True, tearOff=True)

        cmds.menuItem(label='Run Checks',
                    command='import glTools.spotcheck.runChecks;reload(glTools.spotcheck.runChecks);glTools.spotcheck.runChecks.run(envKey="IKA_RIG_SPOTCHECKS",checkTitle="Rig Checks",selectedNodes=False)')
        cmds.menuItem(label='Run Checks On Selected',
                    command='import glTools.spotcheck.runChecks;reload(glTools.spotcheck.runChecks);glTools.spotcheck.runChecks.run(envKey="IKA_RIG_SPOTCHECKS",checkTitle="Rig Checks",selectedNodes=True)')
        cmds.menuItem(divider=True)
        cmds.menuItem(label='Check NonReference Geo Inputs',
                    command='import glTools.tools.fixNonReferenceInputShape;reload(glTools.tools.fixNonReferenceInputShape);glTools.tools.fixNonReferenceInputShape.checkNonReferenceInputShapes(cmds.ls(sl=1)[0],verbose=True)')

        cmds.setParent('..', menu=True)

        # ----------------------------------------#

        # > FIXES
        cmds.menuItem(label='Fixes', subMenu=True, tearOff=True)

        cmds.menuItem(label='Fix NonReference Geo Inputs',
                    command='import glTools.tools.fixNonReferenceInputShape;reload(glTools.tools.fixNonReferenceInputShape);glTools.tools.fixNonReferenceInputShape.fixNonReferenceInputShapes(cmds.ls(sl=1)[0],verbose=True)')

        cmds.setParent('..', menu=True)

        # > MENU

        cmds.menuItem(label='Menu', subMenu=True, tearOff=True)

        cmds.menuItem(label='Create Surface Skin Menu',
                    command='import glTools.surfaceSkin; glTools.surfaceSkin.SurfaceSkinUI().menu()')

        cmds.setParent('..', menu=True)

        # ----------------------------------------#

        cmds.menuItem(divider=True)

        # > GENERAL
        cmds.menuItem(allowOptionBoxes=True, label='General', subMenu=True, tearOff=True)

        cmds.menuItem(label='Renamer', command='mel.eval("renamer")', ann='Open Renamer UI')
        cmds.menuItem(label='Colorize UI', command='mel.eval("colorize")', ann='Open Colorizer UI')
        cmds.menuItem(label='Set Colour',
                    command='import glTools.utils.colorize;reload(glTools.utils.colorize);[glTools.utils.colorize.setColour(i) for i in cmds.ls(sl=1)]',
                    ann='Set colours based on object naming')
        cmds.menuItem(label='Colour Hierarchy',
                    command='import glTools.utils.colorize;reload(glTools.utils.colorize);[glTools.utils.colorize.colourHierarchy(i) for i in cmds.ls(sl=1)]',
                    ann='Set colours for all nodes in hierarchy based on object naming')
        cmds.menuItem(label='Namespacer', command='mel.eval("namespacer")', ann='Open Namespacer UI')
        cmds.menuItem(label='Dag Sort',
                    command='import glTools.utils.base;reload(glTools.utils.base);glTools.utils.base.dagSort()',
                    ann='Sort DAG objects by name')
        cmds.menuItem(label='Rename Duplicates',
                    command='import glTools.utils.base;reload(glTools.utils.base);glTools.utils.base.renameDuplicates()',
                    ann='Rename duplicate objects')
        cmds.menuItem(label='Select By Attribute',
                    command='import glTools.utils.selection;reload(glTools.utils.selection);cmds.select(glTools.utils.selection.selectByAttr())',
                    ann='Select objects by attribute name')
        cmds.menuItem(label='Parent List', command='glTools.ui.base.parentListUI()', ann='Open Parent List UI')
        cmds.menuItem(label='Parent Shapes',
                    command='import glTools.utils.shape;reload(glTools.utils.shape);glTools.utils.shape.parent(cmds.ls(sl=True)[0],cmds.ls(sl=True)[1])',
                    ann='Parent shape(s) to a different transform. Select shape node or transform, follwed by the target transform')
        cmds.menuItem(label='Unparent Shapes',
                    command='import glTools.utils.shape;reload(glTools.utils.shape);[glTools.utils.shape.unparent(i) for i in cmds.ls(sl=True)]',
                    ann='Unparent shapes from the selected tarnsform')
        cmds.menuItem(label='Rename Shapes',
                    command='import glTools.utils.shape;reload(glTools.utils.shape);[glTools.utils.shape.rename(i) for i in cmds.ls(sl=1)]',
                    ann='Rename shape nodes based on the parent transform')
        cmds.menuItem(label='Reorder Attributes', command='glTools.tools.reorderAttr.reorderAttrUI()',
                    ann='Open Reorder Attributes UI')
        cmds.menuItem(label='Rename History Nodes', command='glTools.ui.base.renameHistoryNodesUI()',
                    ann='Open Rename History Nodes UI')
        cmds.menuItem(label='Create Intermediate Shape', command='glTools.utils.shape.createIntermediate(cmds.ls(sl=1)[0])',
                    ann='Create Intermediate Shape for the selected geometry.')
        cmds.menuItem(label='Attribute Presets', command='glTools.ui.attrPreset.ui()', ann='Open attribute presets UI')
        cmds.menuItem(label='Swap Nodes',
                    command='import glTools.utils.connection;reload(glTools.utils.connection);glTools.utils.connection.swap(cmds.ls(sl=1)[0],cmds.ls(sl=1)[1])',
                    ann='Swap Node Connections')
        cmds.menuItem(label='Delete Unknown Nodes',
                    command='import glTools.utils.cleanup;reload(glTools.utils.cleanup);glTools.utils.cleanup.deleteUnknownNodes()',
                    ann='Delete all "unknown" nodes')

        cmds.menuItem(label='Match Transform',
                    command='import glTools.utils.transform;reload(glTools.utils.transform);sel=cmds.ls(sl=1);glTools.utils.transform.match(sel[0],sel[1])',
                    ann='Match first selected transform to second selected transform')
        cmds.menuItem(label='Match Bounding Box',
                    command='import glTools.utils.boundingBox;reload(glTools.utils.boundingBox);sel=cmds.ls(sl=1);glTools.utils.boundingBox.match(sel[0],sel[1])',
                    ann='Match first selected transform to second selected transform based on bounding box comparison')
        # cmds.menuItem(label='Match Position', command='import glTools.utils.transform;reload(glTools.utils.transform);sel=cmds.ls(sl=1);glTools.utils.transform.match(sel[0],sel[1])',ann='Match first selected object position to second selected object')
        # cmds.menuItem(label='Match Orientation', command='import glTools.utils.transform;reload(glTools.utils.transform);sel=cmds.ls(sl=1);glTools.utils.transform.match(sel[0],sel[1])',ann='Match first selected object orientation/rotation to second selected object')
        # cmds.menuItem(label='Match Scale', command='import glTools.utils.transform;reload(glTools.utils.transform);sel=cmds.ls(sl=1);glTools.utils.transform.match(sel[0],sel[1])',ann='Match first selected object scale to second selected object')

        # >> MATCH ATTRIBUTES
        cmds.menuItem(allowOptionBoxes=True, label='Match Attrs', subMenu=True, tearOff=True)

        cmds.menuItem(label='Match All',
                    command='import glTools.tools.match;reload(glTools.tools.match);sel=cmds.ls(sl=1);glTools.tools.match.matchAttrs(sel[0],sel[1],["tx","ty","tz","rx","ry","rz","sx","sy","sz"])',
                    ann='Match all local transform values')
        cmds.menuItem(label='Match Translate',
                    command='import glTools.tools.match;reload(glTools.tools.match);sel=cmds.ls(sl=1);glTools.tools.match.matchAttrs(sel[0],sel[1],["tx","ty","tz"])',
                    ann='Match local translate values')
        cmds.menuItem(label='Match Rotate',
                    command='import glTools.tools.match;reload(glTools.tools.match);sel=cmds.ls(sl=1);glTools.tools.match.matchAttrs(sel[0],sel[1],["rx","ry","rz"])',
                    ann='Match local rotate values')
        cmds.menuItem(label='Match Scale',
                    command='import glTools.tools.match;reload(glTools.tools.match);sel=cmds.ls(sl=1);glTools.tools.match.matchAttrs(sel[0],sel[1],["sx","sy","sz"])',
                    ann='Match local scale values')
        cmds.menuItem(label='Match From CB',
                    command='import glTools.tools.match;reload(glTools.tools.match);sel=cmds.ls(sl=1);glTools.tools.match.matchAttrs(sel[0],sel[1],"frocmdshannelBox")',
                    ann='Match all values based on channel selection (channelBox)')

        cmds.setParent('..', menu=True)

        cmds.menuItem(label='Graph Profiler',
                    command='import glTools.ui.qt.graphProfiler;reload(glTools.ui.qt.graphProfiler);glTools.ui.qt.graphProfiler.GraphProfiler().show()',
                    ann='Tools to Collect and Display Dependency Graph Data')

        cmds.setParent('..', menu=True)

        # > TOOLS
        cmds.menuItem(allowOptionBoxes=True, label='Tools', subMenu=True, tearOff=True)

        cmds.menuItem(label='Center Pt Locator',
                    command='import glTools.tools.center;reload(glTools.tools.center);glTools.tools.center.centerPointLocator(cmds.ls(sl=True,fl=True))',
                    ann='Create locator at center of point selection.')
        cmds.menuItem(label='Center to Geometry',
                    command='import glTools.tools.center;reload(glTools.tools.center);sel = cmds.ls(sl=True,fl=True);glTools.tools.center.centerToGeometry(sel[0],sel[1])',
                    ann='Select the geometry and the object to position.')
        cmds.menuItem(label='Center to Points',
                    command='import glTools.tools.center;reload(glTools.tools.center);sel = cmds.ls(sl=True,fl=True);glTools.tools.center.centerToPoints(sel[:-1],sel[-1])',
                    ann='Select the points and the object to position.')
        cmds.menuItem(label='Point Face Mesh',
                    command='import glTools.tools.pointFaceMesh;reload(glTools.tools.pointFaceMesh);glTools.tools.pointFaceMesh.pointFaceMesh(cmds.ls(sl=True,fl=True),combine=False)',
                    ann='Create single mesh face at each point in selection.')

        cmds.menuItem(label='Slide Deformer',
                    command='import glTools.model.utils;reload(glTools.model.utils);[glTools.model.utils.slideDeformer(i) for i in cmds.ls(sl=1)]')
        cmds.menuItem(label='Strain Relaxer',
                    command='import glTools.model.utils;reload(glTools.model.utils);[glTools.model.utils.strainRelaxer(i) for i in cmds.ls(sl=1)]')
        cmds.menuItem(label='Directional Smooth',
                    command='import glTools.model.utils;reload(glTools.model.utils);[glTools.model.utils.directionalSmooth(i) for i in cmds.ls(sl=1)]')
        cmds.menuItem(label='Delta Mush',
                    command='import glTools.model.utils;reload(glTools.model.utils);[glTools.model.utils.deltaMush(i) for i in cmds.ls(sl=1)]')

        cmds.setParent('..', menu=True)

        # > SELECTION
        cmds.menuItem(allowOptionBoxes=True, label='Select', subMenu=True, tearOff=True)

        cmds.menuItem(label='Select Hierarchy', command='mel.eval("SelectHierarchy")')

        cmds.menuItem(allowOptionBoxes=True, label='Select All Below (by type)', subMenu=True, tearOff=True)
        cmds.menuItem(label='constraint',
                    command='cmds.select(cmds.ls(cmds.listRelatives(ad=True,pa=True) or [],type="constraint"))')
        cmds.menuItem(label='ikHandle',
                    command='cmds.select(cmds.ls(cmds.listRelatives(ad=True,pa=True) or [],type="ikHandle"))')
        cmds.menuItem(label='joint', command='cmds.select(cmds.ls(cmds.listRelatives(ad=True,pa=True) or [],type="joint"))')

        cmds.setParent('..', menu=True)

        cmds.menuItem(allowOptionBoxes=True, label='Select Directly Below (by type)', subMenu=True, tearOff=True)
        cmds.menuItem(label='constraint',
                    command='cmds.select(cmds.ls(cmds.listRelatives(c=True,pa=True) or [],type="constraint"))')
        cmds.menuItem(label='ikHandle',
                    command='cmds.select(cmds.ls(cmds.listRelatives(c=True,pa=True) or [],type="ikHandle"))')
        cmds.menuItem(label='joint', command='cmds.select(cmds.ls(cmds.listRelatives(c=True,pa=True) or [],type="joint"))')

        cmds.setParent('..', menu=True)
        cmds.menuItem(label='Mirror Polygon Selection',
                    command='import glTools.utils.edgeFlowMirror;reload(glTools.utils.edgeFlowMirror);glTools.utils.edgeFlowMirror.mirrorSelection()')

        cmds.setParent('..', menu=True)

        cmds.setParent('..', menu=True)

        # > REFERENCE
        cmds.menuItem(allowOptionBoxes=True, label='Reference', subMenu=True, tearOff=True)

        cmds.menuItem(label='Reload Reference',
                    command='import glTools.anim.reference_utils;reload(glTools.anim.reference_utils);glTools.anim.reference_utils.reloadSelected()')
        cmds.menuItem(label='Unload Reference',
                    command='import glTools.anim.reference_utils;reload(glTools.anim.reference_utils);glTools.anim.reference_utils.unloadSelected()')
        cmds.menuItem(label='Remove Reference',
                    command='import glTools.anim.reference_utils;reload(glTools.anim.reference_utils);glTools.anim.reference_utils.removeSelected(removeNS=False)')
        cmds.menuItem(label='Remove Reference and NS',
                    command='import glTools.anim.reference_utils;reload(glTools.anim.reference_utils);glTools.anim.reference_utils.removeSelected(removeNS=True)')
        cmds.menuItem(label='Remove Unloaded References',
                    command='import glTools.utils.reference;reload(glTools.utils.reference);glTools.utils.reference.removeUnloadedReferences()')
        cmds.menuItem(label='Remove Reference Edits',
                    command='import glTools.tools.removeReferenceEdits;reload(glTools.tools.removeReferenceEdits);glTools.tools.removeReferenceEdits.removeReferenceEditsUI()')

        cmds.setParent('..', menu=True)

        # > SHADER
        cmds.menuItem(allowOptionBoxes=True, label='Shader', subMenu=True, tearOff=True)

        cmds.menuItem(label='Apply Reference Shader',
                    command='import glTools.utils.shader;reload(glTools.utils.shader);[glTools.utils.shader.applyReferencedShader(i) for i in cmds.ls(sl=1)]')
        cmds.menuItem(label='Reconnect Shader',
                    command='import glTools.utils.shader;reload(glTools.utils.shader);[glTools.utils.shader.reconnectShader(i) for i in cmds.ls(sl=1)]')

        cmds.setParent('..', menu=True)

        # > RIG
        cmds.menuItem(allowOptionBoxes=True, label='Rig', subMenu=True, tearOff=True)

        # cmds.menuItem(label='Create Base Rig', command='glTools.builder.BaseRig().build()')
        cmds.menuItem(label='Rename Chain',
                    command='import glTools.utils.base;reload(glTools.utils.base);glTools.utils.base.renameChain(cmds.ls(sl=1,l=False)[0])',
                    ann='Rename the selected joint hierarchy')
        cmds.menuItem(label='Control Builder', command='glTools.ui.controlBuilder.controlBuilderUI()',
                    ann='Open ControlBuilder UI')
        cmds.menuItem(label='Group',
                    command='for i in cmds.ls(sl=True,type=["transform","joint","ikHandle"]): glTools.utils.base.group(i,True,True)',
                    ann='Create a centered and oriented transform group for the selected object/s')
        cmds.menuItem(label='Toggle Override', command='glTools.utils.toggleOverride.ui()', ann='Open Toggle Override UI')
        cmds.menuItem(label='Replace Geometry', command='glTools.ui.replaceGeometry.replaceGeometryFromUI()',
                    ann='First select the replacement geometry and then the geometry to be replaced.')
        cmds.menuItem(label='Create Bind Joint Set', command='cmds.sets(cmds.ls("*.bindJoint",o=True),n="bindJoints")',
                    ann='Create a bindJoints set for all tagged bind joints. ("*.bindJoint")')
        cmds.menuItem(label='Clean Rig',
                    command='import glTools.rig.cleanup;reload(glTools.rig.cleanup);glTools.rig.cleanup.clean()',
                    ann='Clean Rig Workfile')

        # > > Flatten Scene
        cmds.menuItem(allowOptionBoxes=True, label='Flatten Scene', subMenu=True, tearOff=True)

        cmds.menuItem(label='Flatten Scene',
                    command='import glTools.tools.flattenScene;reload(glTools.tools.flattenScene);glTools.tools.flattenScene.flatten()',
                    ann='Flatten Scene - Import all references and delete all namespaces etc.')
        # ----------------------------------------#
        cmds.menuItem(divider=True)
        # ----------------------------------------#
        cmds.menuItem(label='NodesToDelete Set',
                    command='import glTools.tools.flattenScene;reload(glTools.tools.flattenScene);glTools.tools.flattenScene.createNodesToDeleteSet(cmds.ls(sl=True))',
                    ann='Create "nodesToDelete" set')
        cmds.menuItem(label='Add Rename Attr',
                    command='import glTools.tools.flattenScene;reload(glTools.tools.flattenScene);[glTools.tools.flattenScene.addRenameAttr(i) for i in cmds.ls(sl=True)]',
                    ann='Add "renameOnFlatten" attribute.')
        cmds.menuItem(label='Add Reparent Attr',
                    command='import glTools.tools.flattenScene;reload(glTools.tools.flattenScene);glTools.tools.flattenScene.addReparentAttrFromSel()',
                    ann='Add "reparentOnFlatten" attribute based on current selection.')
        cmds.menuItem(label='Add Delete History Attr',
                    command='import glTools.tools.flattenScene;reload(glTools.tools.flattenScene);[glTools.tools.flattenScene.addDeleteHistoryAttr(i) for i in cmds.ls(sl=True,dag=True)]',
                    ann='Add "deleteHistoryOnFlatten" attribute based on current selection.')
        cmds.menuItem(label='Add Reference Path Attr',
                    command='import glTools.tools.flattenScene;reload(glTools.tools.flattenScene);[glTools.tools.flattenScene.addReferencePathAttr(i) for i in cmds.ls(sl=True)]',
                    ann='Add "fixNonReferenceInputsRoot" attribute based on current selection.')
        cmds.menuItem(label='Add Fix NonReference Inputs Attr',
                    command='import glTools.tools.flattenScene;reload(glTools.tools.flattenScene);[glTools.tools.flattenScene.addFixNonReferenceInputAttr(i) for i in cmds.ls(sl=True)]',
                    ann='Add "encodeReferenceFilePath" attribute based on current selection.')

        cmds.setParent('..', menu=True)

        # > > Channel State
        cmds.menuItem(allowOptionBoxes=True, label='Channel State', subMenu=True, tearOff=True)

        cmds.menuItem(label='Channel State',
                    command='import glTools.utils.channelState; reload(glTools.utils.channelState); glTools.utils.channelState.ChannelState().ui()',
                    ann='Open ChannelState UI')
        cmds.menuItem(divider=True)
        cmds.menuItem(label='Record Visibility State',
                    command='import glTools.utils.defaultAttrState;reload(glTools.utils.defaultAttrState);glTools.utils.defaultAttrState.recordVisibility(cmds.listRelatives("all",ad=True))',
                    ann='Record default visibility state for all nodes under rig root node ("all").')
        cmds.menuItem(label='Record Display Override State',
                    command='import glTools.utils.defaultAttrState;reload(glTools.utils.defaultAttrState);glTools.utils.defaultAttrState.recordDisplayOverrides(cmds.listRelatives("all",ad=True))',
                    ann='Record default display override state for all nodes under rig root node ("all").')
        cmds.menuItem(divider=True)
        cmds.menuItem(label='Disable Visibility State',
                    command='import glTools.utils.defaultAttrState;reload(glTools.utils.defaultAttrState);glTools.utils.defaultAttrState.setVisibilityState(visibilityState=0)',
                    ann='Disable visibility state for all nodes with recorded default visibility state.')
        cmds.menuItem(label='Disable Display Override State',
                    command='import glTools.utils.defaultAttrState;reload(glTools.utils.defaultAttrState);glTools.utils.defaultAttrState.setDisplayOverridesState(displayOverrideState=0)',
                    ann='Disable display override state for all nodes with recorded default display override state.')
        cmds.menuItem(divider=True)
        cmds.menuItem(label='Restore Visibility State',
                    command='import glTools.utils.defaultAttrState;reload(glTools.utils.defaultAttrState);glTools.utils.defaultAttrState.setVisibilityState(visibilityState=1)',
                    ann='Restore visibility state for all nodes with recorded default visibility state.')
        cmds.menuItem(label='Restore Display Override State',
                    command='import glTools.utils.defaultAttrState;reload(glTools.utils.defaultAttrState);glTools.utils.defaultAttrState.setDisplayOverridesState(displayOverrideState=1)',
                    ann='Restore display override state for all nodes with recorded default display override state.')

        cmds.setParent('..', menu=True)

        # > > Export Attrs
        cmds.menuItem(allowOptionBoxes=True, label='Export Attrs', subMenu=True, tearOff=True)

        cmds.menuItem(label='Rest Cache Name',
                    command='import glTools.snapshot.utils;reload(glTools.snapshot.utils);[glTools.snapshot.utils.restCacheName(i) for i in cmds.ls(sl=1)]',
                    ann='Add "restCacheName" attribute to the selected components')
        cmds.menuItem(label='Include in Snapshot',
                    command='import glTools.snapshot.utils;reload(glTools.snapshot.utils);[glTools.snapshot.utils.includeInSnapshot(i) for i in cmds.ls(sl=1)]',
                    ann='Add "includeInSnapshot" attribute to the selected objects')
        cmds.menuItem(label='Distance To Camera',
                    command='import glTools.snapshot.utils;reload(glTools.snapshot.utils);sel = cmds.ls(sl=1);glTools.snapshot.utils.distToCamObjAttr(sel[0],sel[1])',
                    ann='Add "distToCamObj" attribute to the first selected object, and connect to the second selected object')
        cmds.menuItem(divider=True)
        cmds.menuItem(label='Set NonRenderable Faces',
                    command='import glTools.rig.utils;reload(glTools.rig.utils);glTools.rig.utils.nonRenderableFaceSet(facelist=cmds.ls(sl=1))',
                    ann='Add a non-renderable faceset attribute to a mesh(es) based on the selected polygon faces.')
        cmds.menuItem(label='Select NonRenderable Faces',
                    command='import glTools.rig.utils;reload(glTools.rig.utils);sel = cmds.ls(sl=1);glTools.rig.utils.selectNonRenderableFaces(sel[0])',
                    ann='Select non-renderable faces on the first selected mesh.')

        cmds.setParent('..', menu=True)

        # > > Proxy Mesh
        cmds.menuItem(allowOptionBoxes=True, label='Proxy Mesh', subMenu=True, tearOff=True)

        cmds.menuItem(label='Joint Proxy Bounds',
                    command='import glTools.tools.proxyMesh;reload(glTools.tools.proxyMesh);glTools.tools.proxyMesh.skeletonProxyCage(cmds.ls(sl=1,type="joint"))')
        cmds.menuItem(label='Joint Proxy Mirror',
                    command='import glTools.tools.proxyMesh;reload(glTools.tools.proxyMesh);[glTools.tools.proxyMesh.mirrorProxy(i) for i in cmds.ls(sl=True)]')
        cmds.menuItem(label='Make Proxy Bounds',
                    command='import glTools.tools.proxyMesh;reload(glTools.tools.proxyMesh);[glTools.tools.proxyMesh.makeProxyBounds(i) for i in cmds.ls(sl=True)]')
        cmds.menuItem(label='Reset Proxy Bounds',
                    command='import glTools.utils.mesh;reload(glTools.utils.mesh);[glTools.utils.mesh.resetVertices(i) for i in cmds.ls(sl=True)]')
        cmds.menuItem(label='Fit To Mesh',
                    command='import glTools.tools.proxyMesh;reload(glTools.tools.proxyMesh);glTools.tools.proxyMesh.proxyFitMeshSel(-1.0)')
        cmds.menuItem(label='Fit To Joint',
                    command='import glTools.tools.proxyMesh;reload(glTools.tools.proxyMesh);[glTools.tools.proxyMesh.proxyFitJoint(i) for i in cmds.ls(sl=1)]')
        cmds.menuItem(label='Snap to Joint',
                    command='import glTools.tools.proxyMesh;reload(glTools.tools.proxyMesh);[glTools.tools.proxyMesh.proxyConstraint(prx,deleteConstraint=True) for prx in cmds.ls(sl=True,type="transform")]')
        cmds.menuItem(label='Freeze to Joint',
                    command='import glTools.tools.proxyMesh;reload(glTools.tools.proxyMesh);[glTools.tools.proxyMesh.freezeToJoint(prx) for prx in cmds.ls(sl=True,type="transform")]')
        cmds.menuItem(label='Set Proxy Cut Geometry',
                    command='import glTools.tools.proxyMesh;reload(glTools.tools.proxyMesh);glTools.tools.proxyMesh.setCutGeoFromSel()')
        cmds.menuItem(label='Set Proxy Add Geometry',
                    command='import glTools.tools.proxyMesh;reload(glTools.tools.proxyMesh);glTools.tools.proxyMesh.setAddGeoFromSel()')
        cmds.menuItem(label='Set Apply Initial SG',
                    command='import glTools.tools.proxyMesh;reload(glTools.tools.proxyMesh);glTools.tools.proxyMesh.setApplyInitialSGFromSel()')
        cmds.menuItem(label='Apply Proxies',
                    command='import glTools.tools.proxyMesh;reload(glTools.tools.proxyMesh);glTools.tools.proxyMesh.applyProxies(cmds.ls(sl=True,type="transform"))')
        cmds.menuItem(label='Create SkinClusters',
                    command='import glTools.tools.proxyMesh;reload(glTools.tools.proxyMesh);glTools.tools.proxyMesh.proxySkinClusters()')

        cmds.setParent('..', menu=True)

        # > > AUTO MODULE
        cmds.menuItem(allowOptionBoxes=True, label='Auto Module', subMenu=True, tearOff=True)

        cmds.menuItem(label='Base Template',
                    command='import glTools.rig.autoModuleTemplate;reload(glTools.rig.autoModuleTemplate);glTools.rig.autoModuleTemplate.moduleTemplateDialog(glTools.rig.autoModuleTemplate.baseModuleTemplate)')
        cmds.menuItem(label='FK Chain Template',
                    command='import glTools.rig.autoModuleTemplate;reload(glTools.rig.autoModuleTemplate);glTools.rig.autoModuleTemplate.moduleTemplateDialog(glTools.rig.autoModuleTemplate.fkChainModuleTemplate)')
        cmds.menuItem(label='IK Chain Template',
                    command='import glTools.rig.autoModuleTemplate;reload(glTools.rig.autoModuleTemplate);glTools.rig.autoModuleTemplate.moduleTemplateDialog(glTools.rig.autoModuleTemplate.ikChainModuleTemplate)')
        cmds.menuItem(divider=True)
        cmds.menuItem(label='Build Selected Module(s)',
                    command='import glTools.rig.autoModuleBuild;reload(glTools.rig.autoModuleBuild);[glTools.rig.autoModuleBuild.moduleBuild(i) for i in cmds.ls(sl=True,type="transform")]')
        cmds.menuItem(label='Build All Modules',
                    command='import glTools.rig.autoModuleBuild;reload(glTools.rig.autoModuleBuild);glTools.rig.autoModuleBuild.moduleBuildAll()')

        cmds.setParent('..', menu=True)

        # > PROP
        cmds.menuItem(allowOptionBoxes=True, label='Prop', subMenu=True, tearOff=True)
        cmds.menuItem(label='Build Basic Prop',
                    command='import glTools.nrig.rig.prop;reload(glTools.nrig.rig.prop);glTools.nrig.rig.prop.PropRig().build(clean=True)')

        cmds.setParent('..', menu=True)

        cmds.setParent('..', menu=True)

        # Animation
        cmds.menuItem(allowOptionBoxes=True, label='Animation', subMenu=True, tearOff=True)

        cmds.menuItem(label='Set To Default',
                    command='import glTools.rig.utils;reload(glTools.rig.utils);[glTools.rig.utils.setToDefault(i) for i in cmds.ls(sl=True)]')
        cmds.menuItem(label='Mirror Selected',
                    command='import glTools.tools.match;reload(glTools.tools.match);glTools.tools.match.Match().twinSelection()')
        cmds.menuItem(label='Swap Selected',
                    command='import glTools.tools.match;reload(glTools.tools.match);glTools.tools.match.Match().swapSelection()')
        cmds.menuItem(label='Select Mirror',
                    command='import glTools.tools.match;reload(glTools.tools.match);glTools.tools.match.Match().selectTwin()')
        cmds.menuItem(label='IK/FK Match',
                    command='import glTools.rig.ikFkMatch;reload(glTools.rig.ikFkMatch);[glTools.rig.ikFkMatch.match(i) for i in cmds.ls(sl=True)]')
        cmds.menuItem(label='Dk Anim', command='mel.eval("dkAnim")')
        cmds.menuItem(label='Graph Editor Filter', command='glTools.tools.graphFilter.ui()')

        cmds.setParent('..', menu=True)

        # > JOINT
        cmds.menuItem(allowOptionBoxes=True, label='Joint', subMenu=True, tearOff=True)
        cmds.menuItem(label='Joint Group',
                    command='import glTools.utils.joint;reload(glTools.utils.joint);[glTools.utils.joint.group(joint=i,indexStr="") for i in cmds.ls(sl=1,type="joint")]')
        cmds.menuItem(label='Connect Inverse Scale',
                    command='import glTools.utils.joint;reload(glTools.utils.joint);[glTools.utils.joint.connectInverseScale(jnt) for jnt in cmds.ls(sl=True,type="joint")]')
        cmds.menuItem(label='Joint Orient Tool',
                    command='import glTools.ui.joint;reload(glTools.ui.joint);glTools.ui.joint.jointOrientUI()')
        cmds.menuItem(label='Joint Match Orient', command='glTools.utils.joint.orientTo(cmds.ls(sl=1)[1],cmds.ls(sl=1)[0])')
        cmds.menuItem(label='Zero Joint Orient',
                    command='[cmds.setAttr(jnt+".jo",0,0,0) for jnt in cmds.ls(sl=1,type="joint")]')
        cmds.menuItem(label='Freeze Joint Transform',
                    command='cmds.makeIdentity(cmds.ls(sl=True,type="joint"),apply=True,t=True,r=True,s=True,n=False)')
        cmds.menuItem(label='Draw Style (Bone)',
                    command='import glTools.utils.joint;reload(glTools.utils.joint);jnts = cmds.ls(sl=1);glTools.utils.joint.setDrawStyle(jnts,drawStyle="bone")')

        cmds.setParent('..', menu=True)

        # > IK
        cmds.menuItem(allowOptionBoxes=True, label='IK', subMenu=True, tearOff=True)
        cmds.menuItem(label='Create IK Handle', command='glTools.ui.ik.ikHandleUI()')
        cmds.menuItem(label='Stretchy IK Chain', command='glTools.ui.ik.stretchyIkChainUI()')
        cmds.menuItem(label='Stretchy IK Limb', command='glTools.ui.ik.stretchyIkLimbUI()')
        cmds.menuItem(label='Stretchy IK Spline', command='glTools.ui.ik.stretchyIkSplineUI()')

        cmds.setParent('..', menu=True)

        # > CURVE
        cmds.menuItem(allowOptionBoxes=True, label='Curve', subMenu=True, tearOff=True)

        cmds.menuItem(label='Mirror Curve',
                    command='import glTools.ui.curve;reload(glTools.ui.curve);glTools.ui.curve.mirrorCurveFromSel()')
        cmds.menuItem(label='Locator Curve',
                    command='import glTools.ui.curve;reload(glTools.ui.curve);glTools.ui.curve.locatorCurveUI()')
        cmds.menuItem(label='Attach To Curve',
                    command='import glTools.ui.curve;reload(glTools.ui.curve);glTools.ui.curve.attachToCurveUI()')
        cmds.menuItem(label='Curve To Locators',
                    command='import glTools.ui.curve;reload(glTools.ui.curve);glTools.ui.curve.curveToLocatorsUI()')
        cmds.menuItem(label='Create Along Curve',
                    command='import glTools.ui.curve;reload(glTools.ui.curve);glTools.ui.curve.createAlongCurveUI()')
        cmds.menuItem(label='Curve From Edge Loop',
                    command='import glTools.ui.curve;reload(glTools.ui.curve);glTools.ui.curve.edgeLoopCurveUI()')
        cmds.menuItem(label='Build Curve Command',
                    command='import glTools.utils.curve;reload(glTools.utils.curve);print glTools.utils.curve.buildCmd(cmds.ls(sl=1)[0],True)')
        cmds.menuItem(label='Uniform Rebuild',
                    command='import glTools.utils.curve;reload(glTools.utils.curve);glTools.ui.curve.uniformRebuildCurveUI()')

        # cmds.menuItem(allowOptionBoxes=True, label='LidRails', subMenu=True, tearOff=True)
        #
        # cmds.menuItem(label='Create LidSurface', command='glTools.ui.lidRails.lidSurfaceCreateUI()')
        # cmds.menuItem(label='3 Control Setup', command='glTools.ui.lidRails.threeCtrlSetupUI()')
        # cmds.menuItem(label='4 Control Setup', command='glTools.ui.lidRails.fourCtrlSetupUI()')
        #
        # cmds.setParent('..', menu=True)

        cmds.setParent('..', menu=True)

        # > SURFACE
        cmds.menuItem(allowOptionBoxes=True, label='Surface', subMenu=True, tearOff=True)

        cmds.menuItem(label='Locator Surface', command='glTools.ui.surface.locatorSurfaceUI()')
        cmds.menuItem(label='Snap To Surface', command='glTools.ui.surface.snapToSurfaceUI()')
        cmds.menuItem(label='Attach To Surface', command='glTools.ui.surface.attachToSurfaceUI()')
        cmds.menuItem(label='Surface Points', command='glTools.ui.surface.surfacePointsUI()')

        cmds.setParent('..', menu=True)

        # > MESH
        cmds.menuItem(allowOptionBoxes=True, label='Mesh', subMenu=True, tearOff=True)

        cmds.menuItem(label='Snap To Mesh', command='glTools.ui.mesh.snapToMeshUI()')
        cmds.menuItem(label='Interactive Snap Tool', command='glTools.ui.mesh.interactiveSnapToMeshUI()')
        cmds.menuItem(label='Attach To Mesh', command='glTools.ui.mesh.attachToMeshUI()')
        cmds.menuItem(label='Mirror (select middle edge)',
                    command='import glTools.utils.edgeFlowMirror;reload(glTools.utils.edgeFlowMirror);glTools.utils.edgeFlowMirror.mirrorGeo(cmds.ls(sl=True,fl=True)[0])')
        cmds.menuItem(label='Reconstruct Mesh',
                    command='import glTools.tools.mesh;reload(glTools.tools.mesh);sel = cmds.ls(sl=1);[glTools.tools.mesh.reconstructMesh(i,False) for i in sel]')
        cmds.menuItem(label='Reconstruct and Replace',
                    command='import glTools.tools.mesh;reload(glTools.tools.mesh);sel = cmds.ls(sl=1);[glTools.tools.mesh.reconstructMesh(i,True) for i in sel]')

        cmds.setParent('..', menu=True)

        # > SKINCLUSTER
        cmds.menuItem(allowOptionBoxes=True, label='SkinCluster', subMenu=True, tearOff=True)

        cmds.menuItem(label='Reset', command='glTools.ui.skinCluster.resetFromUI()')
        cmds.menuItem(label='Clean', command='glTools.ui.skinCluster.cleanFromUI()')
        cmds.menuItem(label='Rename', command='for i in cmds.ls(sl=1): glTools.utils.skinCluster.rename(i)')
        cmds.menuItem(label='Skin As',
                    command='import glTools.utils.skinCluster;reload(glTools.utils.skinCluster);sel = cmds.ls(sl=1);glTools.utils.skinCluster.skinAs(sel[0],sel[1])')
        cmds.menuItem(label='Skin Objects',
                    command='import glTools.utils.skinCluster;reload(glTools.utils.skinCluster);glTools.utils.skinCluster.skinObjectListFromUI()')
        cmds.menuItem(label='Copy To Many',
                    command='import glTools.tools.skinCluster;reload(glTools.tools.skinCluster);sel = cmds.ls(sl=1);glTools.tools.skinCluster.copyToMany(sel[0],sel[1:])')
        cmds.menuItem(label='Clear Weights',
                    command='import glTools.utils.skinCluster;reload(glTools.utils.skinCluster);glTools.utils.skinCluster.clearWeights(cmds.ls(sl=True)[0])')
        cmds.menuItem(label='Delete BindPose Nodes', command='cmds.delete(cmds.ls(type="dagPose"))')
        cmds.menuItem(label='Lores Weights',
                    command='import glTools.tools.proxyMesh;reload(glTools.tools.proxyMesh);glTools.tools.proxyMesh.proxySkinWeights(cmds.ls(sl=1)[0])')
        cmds.menuItem(label='Make Relative',
                    command='import glTools.utils.skinCluster;reload(glTools.utils.skinCluster);glTools.ui.skinCluster.makeRelativeUI()')
        cmds.menuItem(label='Lock SkinCluster Weights',
                    command='import glTools.utils.skinCluster;reload(glTools.utils.skinCluster);[glTools.utils.skinCluster.lockSkinClusterWeightsFromGeo(geo,True,True) for geo in cmds.ls(sl=1)]')
        cmds.menuItem(label='Unlock SkinCluster Weights',
                    command='import glTools.utils.skinCluster;reload(glTools.utils.skinCluster);[glTools.utils.skinCluster.lockSkinClusterWeightsFromGeo(geo,False,False) for geo in cmds.ls(sl=1)]')
        cmds.menuItem(label='Remove Multiple Base Infs',
                    command='import glTools.utils.skinCluster;reload(glTools.utils.skinCluster);sel = cmds.ls(sl=1);glTools.utils.skinCluster.removeMultipleInfluenceBases(sel[0],sel[1:])')
        cmds.menuItem(label='SkinCluster Data UI',
                    command='import glTools.ui.skinClusterData;reload(glTools.ui.skinClusterData);glTools.ui.skinClusterData.skinClusterDataUI()')
        cmds.menuItem(label='Weights Manager',
                    command='import glTools.ui.qt.weightsManager;reload(glTools.ui.qt.weightsManager);glTools.ui.qt.weightsManager.WeightsManager().show()')

        cmds.setParent('..', menu=True)

        # > BLENDSHAPE
        cmds.menuItem(allowOptionBoxes=True, label='BlendShape', subMenu=True, tearOff=True)

        cmds.menuItem(label='Create BlendShape',
                    command='import glTools.tools.blendShape;reload(glTools.tools.blendShape);glTools.tools.blendShape.createFromSelection()',
                    ann='Create basic blendShape from selection')
        cmds.menuItem(label='BlendShape Manager',
                    command='import glTools.ui.blendShape;reload(glTools.ui.blendShape);glTools.ui.blendShape.blendShapeManagerUI()',
                    ann='Open BlendShape Manager UI')
        cmds.menuItem(label='Update Targets',
                    command='import glTools.ui.blendShape;reload(glTools.ui.blendShape);glTools.ui.blendShape.updateTargetsUI()',
                    ann='Open Update BlendShape Targets UI')
        cmds.menuItem(divider=True)
        cmds.menuItem(label='Override BlendShape',
                    command='import glTools.tools.blendShape;reload(glTools.tools.blendShape);[glTools.tools.blendShape.endOfChainBlendShape(i) for i in cmds.ls(sl=1)]',
                    ann='Create override (end of chain) blendShape deformers on the selected geometry')
        cmds.menuItem(label='Add Override Target',
                    command='import glTools.tools.blendShape;reload(glTools.tools.blendShape);glTools.tools.blendShape.addOverrideTarget(cmds.ls(sl=1)[1],cmds.ls(sl=1)[0])',
                    ann='Add override blendShape target based on the selected geometry')

        cmds.setParent('..', menu=True)

        # > NDYNAMICS
        cmds.menuItem(allowOptionBoxes=True, label='nDynamics', subMenu=True, tearOff=True)

        cmds.menuItem(label='UI', command='glTools.ui.nDynamics.create()')
        cmds.menuItem(divider=True)
        cmds.menuItem(label='Create nucleus', command='glTools.utils.nDynamics.createNucleus()')
        cmds.menuItem(label='Create nCloth', command='for i in cmds.ls(sl=1): glTools.utils.nDynamics.createNCloth(i)')
        cmds.menuItem(label='Create nRigid', command='for i in cmds.ls(sl=1): glTools.utils.nDynamics.createNRigid(i)')
        cmds.menuItem(divider=True)
        cmds.menuItem(label='Delete nCloth', command='for i in cmds.ls(sl=1): glTools.utils.nDynamics.deleteNCloth(i)')

        cmds.setParent('..', menu=True)

        # > SPACES
        # cmds.menuItem(allowOptionBoxes=True, label='Spaces', subMenu=True, tearOff=True)
        # cmds.menuItem(label='Create/Add', command='glTools.ui.spaces.createAddUI()')
        # cmds.menuItem(label='Spaces UI', command='glTools.tools.spaces.Spaces().ui()')
        # cmds.menuItem(ob=True, command='glTools.ui.spaces.charUI()')
        # cmds.setParent('..', menu=True)

        # > POSE MATCH
        cmds.menuItem(allowOptionBoxes=True, label='Pose Match Setup', subMenu=True, tearOff=True)
        cmds.menuItem(label='Evaluation Order', command='glTools.ui.poseMatch.evaluationOrderUI()')
        cmds.menuItem(label='Match Rules', command='glTools.ui.poseMatch.matchRulesUI()')

        cmds.setParent('..', menu=True)

        # ----------------------------------------#
        cmds.menuItem(divider=True)
        # ----------------------------------------#

        cmds.menuItem(label='Refresh Menu',
                    command='import glTools.ui.menu;reload(glTools.ui.menu);glTools.ui.menu.create()')

        cmds.setParent('..')
