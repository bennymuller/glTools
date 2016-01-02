import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import glTools.utils.channelState
import glTools.utils.colorize
import glTools.utils.constraint
import glTools.utils.stringUtils
import glTools.utils.transform
import glTools.rig.utils
import glTools.tools.controlBuilder


def createParentControl(name, ctrlShape='cross', translate=[0, 0, 0], rotate=[0, 0, 0], scale=1):
    """
    Create constraint target control parent transform
    @param name: Name of the resulting constraint target control parent transform
    @type name: str
    @param ctrlShape: Type of control to build
    @type ctrlShape: str
    @param translate: Translational offset for control curve
    @type translate: list or tuple
    @param rotate: Rotational offset for control curve
    @type rotate: list or tuple
    @param scale: Scale offset for control curve
    @type scale: list or tuple
    """
    # ==========
    # - Checks -
    # ==========

    # Name
    if cmds.objExists(name):
        raise Exception('Object "' + name + '" already exists!')

    # Control Shape
    ctrlBuilder = glTools.tools.controlBuilder.ControlBuilder()
    if not ctrlBuilder.controlType.count(ctrlShape):
        raise Exception('Invalid control shape ("' + ctrlShape + '")!')

    # =========================
    # - Create Parent Control -
    # =========================

    # Create Transform Node
    pCtrl = cmds.createNode('transform', n=name)

    # Attach Shape
    ctrlBuilder.controlShape(pCtrl, ctrlShape, translate=translate, rotate=rotate, scale=scale)

    # Tag Control
    glTools.rig.utils.tagCtrl(pCtrl, 'primary')

    # ==================
    # - Add Attributes -
    # ==================

    # Constraint Transform (message)
    cmds.addAttr(pCtrl, ln='constraintTransform', at='message', m=True)
    cmds.addAttr(pCtrl, ln='constraintTarget', at='message', m=True)
    cmds.addAttr(pCtrl, ln='constraintLabel', at='message', m=True)

    # Display Labels
    cmds.addAttr(pCtrl, ln='displayLabels', at='enum', en=':Off:On:', dv=0)
    cmds.setAttr(pCtrl + '.displayLabels', k=False, cb=True)

    # =================
    # - Return Result -
    # =================

    return pCtrl


def createTargetLocator(targetTransform='', targetLabel=''):
    """
    Create a constraint target locator.
    Constraint target locators are added to rig templates for automated creation of rig attach constraints.
    @param targetTransform: The target transform for the rig attach constrain
    @type targetTransform: str
    @param targetLabel: The target label which will be used as a naming and attribute prefix on the constraint control.
    @type targetLabel: str
    """
    # ====================
    # - Check Input Args -
    # ====================

    # Target Transform
    if not targetTransform:

        # Check interactive maya python session
        if OpenMaya.MGlobal.mayaState() != 0:
            raise Exception('No valid targetTransform value provided!')

        result = cmds.promptDialog(title='Constraint Target Transform',
                                 message='Enter Target Transform:',
                                 button=['Create', 'Cancel'],
                                 defaultButton='Create',
                                 cancelButton='Cancel',
                                 dismissString='Cancel')

        if result == 'Create':
            targetTransform = cmds.promptDialog(q=True, text=True)
        if not targetTransform:
            raise Exception('Invalid targetTransform value!')
        if not cmds.objExists(targetTransform):
            raise Exception('Target transform "' + targetTransform + '" does not exist!')

    # Target Label
    if not targetLabel:

        # Check interactive maya python session
        if OpenMaya.MGlobal.mayaState() != 0:
            raise Exception('No valid targetLabel value provided!')

        result = cmds.promptDialog(title='Constraint Target Label',
                                 message='Enter Target Label:',
                                 button=['Create', 'Cancel'],
                                 defaultButton='Create',
                                 cancelButton='Cancel',
                                 dismissString='Cancel')

        if result == 'Create':
            targetLabel = cmds.promptDialog(q=True, text=True)
        if not targetLabel:
            raise Exception('Invalid targetLabel value!')

    # =========================
    # - Create Target Locator -
    # =========================

    # Create Locator
    targetLocator = cmds.spaceLocator(n=targetLabel + '_constraintLoc')[0]

    # Add Locator Attribute
    cmds.addAttr(targetLocator, ln='targetTransform', dt='string')
    cmds.setAttr(targetLocator + '.targetTransform', targetTransform, type='string')
    cmds.addAttr(targetLocator, ln='targetLabel', dt='string')
    cmds.setAttr(targetLocator + '.targetLabel', targetLabel, type='string')

    # Match Transform
    glTools.utils.transform.match(targetLocator, targetTransform)

    # Set Colour
    glTools.utils.colorize.setColour(targetLocator)

    # =================
    # - Return Result -
    # =================

    return targetLocator


def createTargetLocatorFromSel(sel=[]):
    """
    Create constraint target locators based on the current user selection.
    Constraint target locators are added to rig templates for automated creation of rig attach constraints.
    @param sel: List of transforms to create constraint target locators from. If empty, get current active selection.
    @type sel: list
    """
    if not sel:
        # Get User Selection
        sel = cmds.ls(sl=1)

    # For each item in selection
    targetLocatorList = []
    for obj in sel:

        # Check Transform
        if not glTools.utils.transform.isTransform(obj):
            raise Exception('Object "' + obj + '" is not a valid transform!')

        # Get Label Prefix
        label = glTools.utils.stringUtils.stripSuffix(obj)

        # Create Constraint Target Locator
        targetLocator = createTargetLocator(targetTransform=obj, targetLabel=label)
        targetLocatorList.append(targetLocator)

    # Return Result
    return targetLocatorList


def addConstraintTransform(parentCtrl, prefix):
    """
    Create constraint target transform and add to an existing constraint target control parent control.
    @param parentCtrl: Parent constraint target control to connect to the new constraint target
    @type parentCtrl: str
    @param prefix: Naming prefix for new constraint target transform
    @type prefix: str
    """
    # ==========
    # - Checks -
    # ==========

    # Check Parent Control
    if not cmds.objExists(parentCtrl + '.constraintTransform'):
        raise Exception('Object "' + parentCtrl + '" is not a valid constraint target control parent transform!')

    # ======================================
    # - Create Constraint Target Transform -
    # ======================================

    # Create Ctrl Transform
    name = prefix + '_constraintTarget_ctrl'
    targetTransform = cmds.createNode('transform', n=name, p=parentCtrl)

    # Tag Control
    glTools.rig.utils.tagCtrl(targetTransform, 'primary')

    # Add Constraint Interp Type Attr
    if not cmds.objExists(targetTransform + '.interpType'):
        cmds.addAttr(targetTransform, ln='interpType', at='enum', en=':No Flip:Average:Shortest:Longest:Cache:', dv=1)
    # Set Interp Type Default
    cmds.setAttr(targetTransform + '.interpType', 2)  # Shortest

    # Add control shape
    ctrlBuilder = glTools.tools.controlBuilder.ControlBuilder()
    ctrlBuilder.controlShape(targetTransform, 'locator')

    # Connect to Parent Control
    connIndex = cmds.getAttr(parentCtrl + '.constraintTransform', s=True)
    cmds.connectAttr(targetTransform + '.message', parentCtrl + '.constraintTransform[' + str(connIndex) + ']', f=True)

    # Add Visibility Toggle to Parent Control
    cmds.addAttr(parentCtrl, ln=prefix + '_Vis', at='enum', en=':Off:On:', dv=0)
    cmds.setAttr(parentCtrl + '.' + prefix + '_Vis', k=False, cb=True)
    cmds.connectAttr(parentCtrl + '.' + prefix + '_Vis', targetTransform + '.v', f=True)

    # =================
    # - Return Result -
    # =================

    return targetTransform


def getConstraintTransforms(parentCtrl):
    """
    Get a list of connected constraint target transforms from a specified constraint target control parent transform
    @param parentCtrl: Parent constraint target control to get constraint transforms from
    @type parentCtrl: str
    """
    # ==========
    # - Checks -
    # ==========

    # Check Parent Control
    if not cmds.objExists(parentCtrl + '.constraintTransform'):
        raise Exception('Object "' + parentCtrl + '" is not a valid constraint target control parent transform!')

    # =======================================
    # - Get Connected Constraint Transforms -
    # =======================================

    targetTransformList = cmds.listConnections(parentCtrl + '.constraintTransform', s=True, d=False)
    if not targetTransformList: targetTransformList = []

    # =================
    # - Return Result -
    # =================

    return targetTransformList


def getConstraintTargets(parentCtrl):
    """
    Get a list of connected constraint targets from the specified constraint target control parent transform
    @param parentCtrl: Parent constraint target control to get constraint targets from
    @type parentCtrl: str
    """
    # ==========
    # - Checks -
    # ==========

    # Check Parent Control
    if not cmds.objExists(parentCtrl + '.constraintTarget'):
        raise Exception('Object "' + parentCtrl + '" is not a valid constraint target control parent transform!')

    # =======================================
    # - Get Connected Constraint Transforms -
    # =======================================

    constraintTargetList = cmds.listConnections(parentCtrl + '.constraintTarget', s=True, d=False)
    if not constraintTargetList: constraintTargetList = []

    # =================
    # - Return Result -
    # =================

    return constraintTargetList


def addTarget(parentCtrl, targetTransform, matchTransform='', label=''):
    """
    Add a constraint target to a specified constraint target control parent transform
    @param parentCtrl: Parent constraint target control to add constraint target to
    @type parentCtrl: str
    @param targetTransform: Constraint target transform
    @type targetTransform: str
    @param matchTransform: The transform to match the new constraint target transform to. Used to set specific orientational and translational offsets.
    @type matchTransform: str
    @param label: Constraint target label
    @type label: str
    """
    # ==========
    # - Checks -
    # ==========

    # Check Parent Control
    if not cmds.objExists(parentCtrl + '.constraintTarget'):
        raise Exception('Object "' + parentCtrl + '" is not a valid constraint target control parent transform!')

    # Check Constraint Target List
    constraintTargetList = getConstraintTargets(parentCtrl)
    if constraintTargetList.count(targetTransform):
        raise Exception(
            'Constraint target control "' + parentCtrl + '" is already connected to target "' + targetTransform + '"!')

    if matchTransform and not cmds.objExists(matchTransform):
        raise Exception('Constraint target match transform "' + matchTransform + '" does not exist!')

    # Check Target Label
    if cmds.objExists(targetTransform + '.targetLabel'):
        targetLabelCon = cmds.listConnections(targetTransform + '.targetLabel', s=True, d=False)
        if targetLabelCon:
            raise Exception('Target transform "' + targetTransform + '" is already a constraint target!')

    # =========================
    # - Add Constraint Target -
    # =========================

    # Create Label Annotation
    targetShape = cmds.createNode('annotationShape', n=targetTransform + '_targetShape')
    target = cmds.listRelatives(targetShape, p=True, pa=True)[0]
    target = cmds.rename(target, targetTransform + '_target')
    cmds.parent(target, targetTransform)
    glTools.utils.colorize.setColour(targetShape)

    # Set Annotation Attributes
    cmds.setAttr(targetShape + '.text', label, type='string')
    cmds.setAttr(targetShape + '.displayArrow', 0, l=True)

    # Add Label String Attribute
    if not cmds.objExists(target + '.label'):
        cmds.addAttr(target, ln='label', dt='string')
    cmds.setAttr(target + '.label', label, type='string', l=True)

    # Connect Label to Target Transform
    if not cmds.objExists(targetTransform + '.targetLabel'):
        cmds.addAttr(targetTransform, ln='targetLabel', at='message')
    cmds.connectAttr(target + '.message', targetTransform + '.targetLabel', f=True)

    # Match Transform
    if matchTransform:
        glTools.utils.transform.match(target, matchTransform)
    else:
        glTools.utils.transform.match(target, targetTransform)

    # Set Channel State
    channelState = glTools.utils.channelState.ChannelState()
    channelState.setFlags([2, 2, 2, 2, 2, 2, 2, 2, 2, 1], objectList=[target])

    # =============================
    # - Connect to Parent Control -
    # =============================

    # Connect Label Vis
    cmds.connectAttr(parentCtrl + '.displayLabels', targetShape + '.v', f=True)

    # Connect Target Message
    connIndex = cmds.getAttr(parentCtrl + '.constraintTarget', s=True)
    cmds.connectAttr(targetTransform + '.message', parentCtrl + '.constraintTarget[' + str(connIndex) + ']', f=True)

    # Connect Label Message
    connIndex = cmds.getAttr(parentCtrl + '.constraintLabel', s=True)
    cmds.connectAttr(target + '.message', parentCtrl + '.constraintLabel[' + str(connIndex) + ']', f=True)

    # =================
    # - Return Result -
    # =================

    return target


def connectTargets(parentCtrl):
    """
    Add all constraint targets to constraint transforms connected to the specified constraint target control parent transform
    @param parentCtrl: Parent constraint target control to create connections for
    @type parentCtrl: str
    """
    # ==========
    # - Checks -
    # ==========

    # Check Parent Control
    if not cmds.objExists(parentCtrl + '.constraintTarget'):
        raise Exception('Object "' + parentCtrl + '" is not a valid constraint target control parent transform!')

    # =============================================
    # - Get Constraint Transform and Target Lists -
    # =============================================

    constraintTransformList = getConstraintTransforms(parentCtrl)
    constraintTargetList = getConstraintTargets(parentCtrl)

    if not constraintTransformList:
        raise Exception('No valid constraint transforms connected to parent control "' + parentCtrl + '"!')
    if not constraintTargetList:
        raise Exception('No valid constraint targets connected to parent control "' + parentCtrl + '"!')

    # ======================
    # - Create Constraints -
    # ======================

    for constraintTransform in constraintTransformList:

        # Check existing constraint node
        pTargetList = []
        sTargetList = []
        pConstraintNode = ''
        sConstraintNode = ''
        existingParentConstraint = cmds.listConnections(constraintTransform + '.t', s=True, d=False,
                                                      type='parentConstraint')
        existingScaleConstraint = cmds.listConnections(constraintTransform + '.s', s=True, d=False,
                                                     type='scaleConstraint')

        # Get Existing Constraint Target Lists
        if existingParentConstraint:
            pConstraintNode = existingParentConstraint[0]
            pTargetList = glTools.utils.constraint.targetList(pConstraintNode)
        if existingScaleConstraint:
            sConstraintNode = existingScaleConstraint[0]
            sTargetList = glTools.utils.constraint.targetList(sConstraintNode)

        # For Each Constraint Target
        for constraintTarget in constraintTargetList:

            # Check Target Label Attribute
            if not cmds.objExists(constraintTarget + '.targetLabel'):
                raise Exception(
                    'Constraint target "' + constraintTarget + '" has no "targetLabel" attribute! Unable to determine associated target label transform.')

            # Check Target Label Connection
            targetCon = cmds.listConnections(constraintTarget + '.targetLabel', s=True, d=False)
            if not targetCon:
                raise Exception(
                    'Constraint target "' + constraintTarget + '" has no "targetLabel" connection! Unable to determine associated target label transform.')
            target = targetCon[0]

            # Check existing Constraint Target
            if pTargetList.count(target):
                raise Exception(
                    'Constraint target "' + target + '" is already a target transform for constraint node "' + pConstraintNode + '"!')
            if sTargetList.count(target):
                raise Exception(
                    'Constraint target "' + target + '" is already a target transform for constraint node "' + sConstraintNode + '"!')

            # Get Target Label
            if not cmds.objExists(target + '.label'):
                raise Exception(
                    'Constraint target "' + target + '" has no "label" attribute! Unable to determine label string.')
            label = cmds.getAttr(target + '.label')

            # Attach as Constraint Target
            pConstraintNode = cmds.parentConstraint(target, constraintTransform, mo=False)[0]
            pConstraintTargetAlias = glTools.utils.constraint.targetAlias(pConstraintNode, target)
            sConstraintNode = cmds.scaleConstraint(target, constraintTransform, mo=False)[0]
            sConstraintTargetAlias = glTools.utils.constraint.targetAlias(sConstraintNode, target)

            # Connect To Constraint Target Weight
            if not cmds.objExists(constraintTransform + '.' + label):
                cmds.addAttr(constraintTransform, ln=label, min=0, max=1, dv=0, k=True)
            cmds.connectAttr(constraintTransform + '.' + label, pConstraintNode + '.' + pConstraintTargetAlias, f=True)
            cmds.connectAttr(constraintTransform + '.' + label, sConstraintNode + '.' + sConstraintTargetAlias, f=True)

            # Set Constraint Rest Values
            cmds.setAttr(pConstraintNode + '.restTranslate', 0, 0, 0)
            cmds.setAttr(pConstraintNode + '.restRotate', 0, 0, 0)

            # Connect Interpolation Type
            pConstraintInterpCon = cmds.listConnections(pConstraintNode + '.interpType', s=True, d=False, p=True)
            if not pConstraintInterpCon: pConstraintInterpCon = []
            if not pConstraintInterpCon.count(constraintTransform + '.interpType'):
                try:
                    cmds.connectAttr(constraintTransform + '.interpType', pConstraintNode + '.interpType', f=True)
                except:
                    pass
