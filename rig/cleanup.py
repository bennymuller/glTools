import maya.mel as mel
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import glTools.utils.cleanup
import glTools.utils.defaultAttrState
import glTools.utils.deformer
import glTools.utils.reference
import glTools.utils.namespace
import glTools.utils.skinCluster
import glTools.rig.utils


def clean(showProgress=False):
    """
    Clean Rig
    @param showProgress:
    """
    print('===========================================')
    print('=============== RIG CLEANUP ===============')
    print('===========================================')

    # Delete Unused Nodes
    deleteUnusedNodes()

    # Channel States
    channelStateSet()

    # Toggle End/Con Joints
    toggleJointVis()

    # Reorder Shapes
    reorderShapes()

    # Clean Deformers
    # cleanDeformers(weightThreshold=0.001,showProgress)

    # Clean SkinClusters
    cleanSkinClusters(showProgress)

    # Lock Joint Orients
    lockJointAttrs()

    # Lock Influence Weights
    lockInfluenceWeights()

    # Lock and Hide Unused Attributes
    lockAndHideAttributes()

    # Copy Input Shape User Attributes
    copyInputShapeAttrs()

    print('============================================')
    print('=========== RIG CLEANUP COMPLETE ===========')
    print('============================================')


def lockAndHideAttributes():
    """
    Lock and hide unused attribute.
    """
    # Mesh Attributes
    meshAttr = ['smoothOffset', 'uvSet']
    for attr in meshAttr:
        for mesh in cmds.ls(cmds.ls('*.' + attr, o=True, r=True), type='mesh'):
            if cmds.getAttr(mesh + '.' + attr, settable=True):
                try:
                    cmds.setAttr(mesh + '.' + attr, l=True, k=False)
                except:
                    print "Can not lock :: %s.%s" % (mesh, attr)


def deleteUnusedNodes():
    """
    Delete unused nodes
    """
    # Start Timer
    timer = cmds.timerX()

    # BindPose
    print('Deleting bind pose ("dagPose") nodes')
    dagPoseNodes = cmds.ls(type='dagPose')
    if dagPoseNodes: cmds.delete(dagPoseNodes)

    # Unknown
    print('Deleting unknown nodes')
    glTools.utils.cleanup.deleteUnknownNodes()

    # Sets
    # print('Deleting empty sets')
    # glTools.utils.cleanup.deleteEmptySets()

    # Display Layers
    print('Deleting display layers')
    glTools.utils.cleanup.deleteDisplayLayers()

    # Render Layers
    print('Deleting render layers')
    glTools.utils.cleanup.deleteRenderLayers()

    # Turtle
    print('Removing Turtle plugin')
    glTools.utils.cleanup.removeTurtle()

    # Print Timed Result
    print('# Clean Rig: Delete Unused Nodes - ' + str(cmds.timerX(st=timer)))


def channelStateSet():
    """
    Enable channel states.
    Store Default Attr States.
    """
    # Start Timer
    timer = cmds.timerX()

    # Channel State - All ON
    print('Channel States Enabled')
    glTools.utils.channelState.ChannelState().set(1)

    # Default Attr State - All ON
    print('Default Attribute States Enabled')
    glTools.utils.defaultAttrState.setDisplayOverridesState(displayOverrideState=1)
    glTools.utils.defaultAttrState.setVisibilityState(visibilityState=1)

    # Print Timed Result
    print('# Clean Rig: Channel States - ' + str(cmds.timerX(st=timer)))


def toggleJointVis():
    """
    Toggle "End" and "Con" joint visibility and display overrides.
    """
    # Start Timer
    timer = cmds.timerX()

    print('# Clean Rig: Lock Unused Joints (toggle display overrides for all "End" and "Con" joints)')
    glTools.utils.cleanup.toggleEnds(0)
    glTools.utils.cleanup.toggleCons(0)

    # Print Timed Result
    print('# Clean Rig: End/Con Joints Locked - ' + str(cmds.timerX(st=timer)))


def reorderShapes():
    """
    """
    # Start Timer
    timer = cmds.timerX()

    print('Reordering Constraints Nodes (push constraints to end of child list)')
    constraintList = cmds.ls(type='constraint')
    if constraintList: cmds.reorder(constraintList, b=True)

    # Print Timed Result
    print('# Clean Rig: Reorder Constraints - ' + str(cmds.timerX(st=timer)))

    # Start Timer
    timer = cmds.timerX()

    print('Reordering Shape Nodes (push shapes to end of child list)')
    shapeList = cmds.ls(type=['mesh', 'nurbsCurve', 'nurbsCurve'])
    if shapeList: cmds.reorder(shapeList, b=True)

    # Print Timed Result
    print('# Clean Rig: Reorder Shapes - ' + str(cmds.timerX(st=timer)))


def cleanDeformers(eightThreshold=0.001, showProgress=False):
    """
    Cleaning all deformers
    Prune small weights and membership
    @param eightThreshold:
    @param showProgress:
    """
    print('# Clean Rig: Cleaning Deformers (prune weights and membership)')

    # Start Timer
    timer = cmds.timerX()

    deformerList = glTools.utils.deformer.getDeformerList(nodeType='weightGeometryFilter')

    if showProgress and interactive:
        cmds.progressBar(gMainProgressBar, e=True, bp=True, ii=True, status=('Cleaning Deformers...'), maxValue=len(deformerList))

    # For Each Deformer
    for deformer in deformerList:

        # Clean Deformers
        try:
            glTools.utils.deformer.clean(deformer, threshold=weightThreshold)
        except:
            print('# Clean Rig: XXXXXXXXX ======== Unable to clean deformer "' + deformer + '"! ======== XXXXXXXXX')

        # Update Progress Bar
        if showProgress and interactive:
            if cmds.progressBar(gMainProgressBar, q=True, isCancelled=True):
                cmds.progressBar(gMainProgressBar, e=True, endProgress=True)
                raise UserInterupted('Operation cancelled by user!')
            cmds.progressBar(gMainProgressBar, e=True, step=1)

    if showProgress and interactive:
        cmds.progressBar(gMainProgressBar, e=True, endProgress=True)

    # Print Timed Result
    print('# Clean Rig: Clean Deformers - ' + str(cmds.timerX(st=timer)))


def cleanSkinClusters(showProgress=False):
    """
    @param showProgress:
    """
    # Start Timer
    timer = cmds.timerX()

    # Clean SkinClusters
    skinClusterList = cmds.ls(type='skinCluster')

    if showProgress and interactive:
        cmds.progressBar(gMainProgressBar, e=True, bp=True, ii=True, status=('Cleaning SkinClusters...'),
                       maxValue=len(skinClusterList))

    for skinCluster in skinClusterList:
        try:
            glTools.utils.skinCluster.clean(skinCluster, tolerance=0.001)
        except:
            print(
            '# Clean Rig: XXXXXXXXX ======== Unable to clean skinCluster "' + skinCluster + '"! ======== XXXXXXXXX')

        # Update Progress Bar
        if showProgress and interactive:
            if cmds.progressBar(gMainProgressBar, q=True, isCancelled=True):
                cmds.progressBar(gMainProgressBar, e=True, endProgress=True)
                raise UserInterupted('Operation cancelled by user!')
            cmds.progressBar(gMainProgressBar, e=True, step=1)

    if showProgress and interactive:
        cmds.progressBar(gMainProgressBar, e=True, endProgress=True)

    # Print Timed Result
    print('# Clean Rig: Clean SkinClusters - ' + str(cmds.timerX(st=timer)))


def lockJointAttrs():
    """
    Locked Unused Joint Attributes
        - jointOrient
        - preferredAngle
    """
    # Start Timer
    timer = cmds.timerX()

    print('Locked Unused Joint Attributes (jointOrient, preferredAngle)')
    glTools.rig.utils.lockJointAttrs([])

    # Print Timed Result
    print('# Clean Rig: Clean Deformers - ' + str(cmds.timerX(st=timer)))


def lockInfluenceWeights():
    """
    Lock skinCluster influence weights
    """
    # Start Timer
    timer = cmds.timerX()

    print('Lock SkinCluster Influence Weights')
    influenceList = cmds.ls('*.liw', o=True, r=True)
    for influence in influenceList:
        glTools.utils.skinCluster.lockInfluenceWeights(influence, lock=True, lockAttr=True)

    # Print Timed Result
    print('# Clean Rig: Lock SkinCluster Influences - ' + str(cmds.timerX(st=timer)))


def copyInputShapeAttrs():
    """
    """
    # Start Timer
    timer = cmds.timerX()

    print('# Clean Rig: Copy Input Shape User Attributes')
    glTools.utils.cleanup.copyInputShapeAttrs(0)

    # Print Timed Result
    print('# Clean Rig: Copy Input Shape User Attributes - ' + str(cmds.timerX(st=timer)))
