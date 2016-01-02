import maya.cmds as cmds
import glTools.utils.channelState
import glTools.utils.constraint
import glTools.utils.transform


def switchConstraint(attachType,
                     transform,
                     targetList,
                     aliasList=[],
                     createTarget=True,
                     switchCtrl=None,
                     switchAttr=None,
                     prefix=''):
    """
    Setup a single or multi target switchable constraint based on the input arguments
    @param attachType: Attach constraint type. Accepted types are "point", "orient", "parent", "scale" and "all".
    @type attachType: str
    @param transform: The transform that will be the slave of the attach constraint.
    @type transform: str
    @param targetList: A list of transforms that will be the parent/master of the attach constraint.
    @type targetList: list
    @param aliasList: A list of name alias' for each item in targetList. Uses to populate the enum attr for constraint target switching.
    @type aliasList: list
    @param createTarget: If True, create a new null transform under the current target that will result in a zero offset constraint. If False, use the transform specified in targetList.
    @type createTarget: bool
    @param switchCtrl: The control object that will hold the constraint target switch attribute.
    @type switchCtrl: str
    @param switchAttr: Name of the constraint target switch attribute.
    @type switchAttr: str
    @param prefix: Name prefix for new nodes.
    @type prefix: str
    """
    # ==========
    # - Checks -
    # ==========

    # Attach Type
    if not attachType in ['point', 'orient', 'parent', 'scale', 'all']:
        raise Exception('Invalid attach type! ("' + attachType + '")')

    # Prefix
    if not prefix: prefix = transform

    # Transform
    if not cmds.objExists(transform):
        raise Exception('Transform "' + transform + '" does not exist!')

    # Target
    for target in targetList:
        if not cmds.objExists(target):
            raise Exception('Target transform "' + target + '" does not exist!')

    # Target Alias List
    if not aliasList: aliasList = targetList

    # Switch Control
    if switchCtrl and not cmds.objExists(switchCtrl):
        raise Exception('Switch control "' + switchCtrl + '" does not exist!')

    # =====================
    # - Switch Attributes -
    # =====================

    # Create Switch Attribute
    if switchCtrl:
        if not cmds.objExists(switchCtrl + '.' + switchAttr):
            cmds.addAttr(switchCtrl, ln=switchAttr, at='enum', en=':'.join(aliasList), k=True)

    # ============================
    # - Create Target Transforms -
    # ============================

    # Initialize new target list
    if createTarget:

        # For Each Target
        cTargetList = []
        for t in range(len(targetList)):

            # Duplicate transform to generate new target
            cTarget = cmds.createNode('transform', n=prefix + '_' + aliasList[t] + '_target')
            glTools.utils.transform.match(cTarget, transform)

            # Parent Control Target to Current Constraint Target
            try:
                cTarget = cmds.parent(cTarget, targetList[t])[0]
            except:
                raise Exception(
                    'Unable to parent target null "' + cTarget + '" to target transform "' + targetList[t] + '"!')

            # Target Display Override
            glTools.utils.base.displayOverride(cTarget, overrideEnable=1, overrideDisplay=2)

            # Append to Target List
            cTargetList.append(cTarget)

        # Update target list
        targetList = cTargetList

        # Set Channel States
        chStateUtil = glTools.utils.channelState.ChannelState()
        chStateUtil.setFlags([2, 2, 2, 2, 2, 2, 2, 2, 2, 2], objectList=targetList)

    # =====================
    # - Create Constraint -
    # =====================

    # Initialize scale constraint valiables ("all" only)
    scaleConstraint = None
    scaleWtAlias = []

    if attachType == 'point':
        constraint = cmds.pointConstraint(targetList, transform, mo=False, n=prefix + '_pointConstraint')[0]
        wtAlias = cmds.pointConstraint(constraint, q=True, wal=True)
    if attachType == 'orient':
        constraint = cmds.orientConstraint(targetList, transform, mo=False, n=prefix + '_orientConstraint')[0]
        wtAlias = cmds.orientConstraint(constraint, q=True, wal=True)
    if attachType == 'parent':
        constraint = cmds.parentConstraint(targetList, transform, mo=False, n=prefix + '_parentConstraint')[0]
        wtAlias = cmds.parentConstraint(constraint, q=True, wal=True)
    if attachType == 'scale':
        constraint = cmds.scaleConstraint(targetList, transform, mo=False, n=prefix + '_scaleConstraint')[0]
        wtAlias = cmds.parentConstraint(constraint, q=True, wal=True)
    if attachType == 'all':
        constraint = cmds.parentConstraint(targetList, transform, mo=False, n=prefix + '_parentConstraint')[0]
        wtAlias = cmds.parentConstraint(constraint, q=True, wal=True)
        scaleConstraint = cmds.scaleConstraint(targetList, transform, mo=False, n=prefix + '_scaleConstraint')[0]
        scaleWtAlias = cmds.scaleConstraint(scaleConstraint, q=True, wal=True)

    # =============================
    # - Connect to Switch Control -
    # =============================

    if switchCtrl:

        # Initialize switch list
        switchNodes = []
        for i in range(len(targetList)):

            # Create Switch Node
            switchNode = cmds.createNode('condition', n=prefix + '_' + wtAlias[i] + '_condition')

            # Connect to switch attr
            cmds.connectAttr(switchCtrl + '.' + switchAttr, switchNode + '.firstTerm', f=True)
            cmds.setAttr(switchNode + '.secondTerm', i)
            cmds.setAttr(switchNode + '.operation', 0)  # Equal
            cmds.setAttr(switchNode + '.colorIfTrue', 1, 0, 0)
            cmds.setAttr(switchNode + '.colorIfFalse', 0, 1, 1)

            # Connect to constraint target weight
            cmds.connectAttr(switchNode + '.outColorR', constraint + '.' + wtAlias[i])

            # Connect to scale constraint, if necessary ("all" only)
            if scaleConstraint:
                cmds.connectAttr(switchNode + '.outColorR', scaleConstraint + '.' + scaleWtAlias[i])

            # Append switch list
            switchNodes.append(switchNode)

    # =================
    # - Return Result -
    # =================

    return constraint


def switchTargetVisibility(switchConstraint,
                           targetVisAttr=None,
                           targetLabels=False):
    """
    Create a switch target visibility toggle for the specified switchConstraint.
    Optionally, add target label visibility.
    @param switchConstraint: Switch constraint node to create visibility toggle for.
    @type switchConstraint: str
    @param targetVisAttr: Switch toggle control attribute name.
    @type targetVisAttr: str
    @param targetLabels: Enable target label visibility.
    @type targetLabels: str
    """
    # ==========
    # - Checks -
    # ==========

    # Check Constraint
    if not glTools.utils.constraint.isConstraint(switchConstraint):
        raise Exception('Object "' + switchConstraint + '" is not a valid constraint!')

    # ===============================
    # - Get Switch Constraint Nodes -
    # ===============================

    # Get Switch Conditions from Constraint
    switchCond = cmds.ls(cmds.listConnections(switchConstraint, s=True, d=False), type='condition')

    # Get Switch Control from Conditions
    switchAttr = list(set(cmds.listConnections(switchCond, s=True, d=False, p=True)))
    if len(switchAttr) > 1: raise Exception(
        'Multiple input attributes driving switchConstraint "' + switchConstraint + '"!')
    switchCtrl = cmds.ls(switchAttr[0], o=True)[0]
    switchAttr = switchAttr[0].split('.')[-1]

    # Get Switch Targets from Constraint
    switchTargets = glTools.utils.constraint.targetList(switchConstraint)
    switchAlias = cmds.addAttr(switchCtrl + '.' + switchAttr, q=True, en=True).split(':')

    # =============================
    # - Connect Target Visibility -
    # =============================

    # Check Target Visibility Attribute
    if not targetVisAttr: targetVisAttr = switchAttr + 'Vis'
    if not cmds.objExists(switchCtrl + '.' + targetVisAttr):
        cmds.addAttr(switchCtrl, ln=targetVisAttr, at='enum', en='Off:On')
        cmds.setAttr(switchCtrl + '.' + targetVisAttr, cb=True, l=False)

    # Target Label Visibility
    labelVisChoice = None
    if targetLabels:
        cmds.addAttr(switchCtrl + '.' + targetVisAttr, e=True, en='Off:On:Label')
        labelVisChoice = cmds.createNode('choice', n=switchAttr + '_labelVis_choice')
        cmds.connectAttr(switchCtrl + '.' + targetVisAttr, labelVisChoice + '.selector', f=True)
        cmds.setAttr(labelVisChoice + '.input[0]', 0)
        cmds.setAttr(labelVisChoice + '.input[1]', 0)
        cmds.setAttr(labelVisChoice + '.input[2]', 1)

    # For Each Target
    for t in range(len(switchTargets)):

        # Connect Display Handle Visibility
        cmds.setAttr(switchTargets[t] + '.displayHandle', 1, l=True)
        cmds.connectAttr(switchCtrl + '.' + targetVisAttr, switchTargets[t] + '.v', f=True)

        # Connect Target Label Visibility
        if targetLabels:
            labelShape = cmds.createNode('annotationShape', n=switchTargets[t] + 'Shape', p=switchTargets[t])
            cmds.connectAttr(labelVisChoice + '.output', labelShape + '.v', f=True)
            cmds.setAttr(labelShape + '.text', switchAlias[t], type='string')
            cmds.setAttr(labelShape + '.displayArrow', 0, l=True)
