import maya.cmds as cmds
import glTools.tools.match
import glTools.ui.utils

global gEvalOrder


class UserInputError(Exception): pass


def evaluationOrderUI():
    """
    Main UI method for Evaluation Order setup tools
    """
    # Window
    win = 'evaluationOrderUI'
    if cmds.window(win, q=True, ex=True): cmds.deleteUI(win)
    win = cmds.window(win, t='Evaluation Order')
    # Form Layout
    evaluationOrderFL = cmds.formLayout(numberOfDivisions=100)

    # Evaluation Order List
    evalOrderTSL = cmds.textScrollList('evalOrderTSL', allowMultiSelection=True)

    # Buttons
    evalOrderRootB = cmds.button(label='Set Selected As Root', c='glTools.ui.poseMatch.evalOrderUIsetRoot()')
    evalOrderBuildB = cmds.button(label='Build Root Hierarchy', c='glTools.ui.poseMatch.evalOrderUIbuildHierarchy()')
    evalOrderIKB = cmds.button(label='Reorder Using IK', c='glTools.ui.poseMatch.evalOrderUIreorderIK()')
    evalOrderConstraintB = cmds.button(label='Reorder Using Constraints',
                                     c='glTools.ui.poseMatch.evalOrderUIreorderConstraints()')
    evalOrderReduceB = cmds.button(label='Reduce To Selection', c='glTools.ui.poseMatch.evalOrderUIreduceToSelection()')
    evalOrderMoveUpB = cmds.button(label='Move Up', c='glTools.ui.utils.moveUpTSLPosition("' + evalOrderTSL + '")')
    evalOrderMoveDnB = cmds.button(label='Move Down', c='glTools.ui.utils.moveDownTSLPosition("' + evalOrderTSL + '")')
    evalOrderMoveToBottomB = cmds.button(label='Move To Bottom',
                                       c='glTools.ui.utils.moveToTSLPosition("' + evalOrderTSL + '",-1)')
    evalOrderAddAttrB = cmds.button(label='Add "evalOrder" attribute', c='glTools.ui.poseMatch.evalOrderUIaddAttr()')

    # Separators
    evalOrderReorderSEP = cmds.separator(h=10, style='single')
    evalOrderReduceSEP = cmds.separator(h=10, style='single')
    evalOrderMoveSEP = cmds.separator(h=10, style='single')
    evalOrderAddAttrSEP = cmds.separator(h=10, style='single')

    # Form Layout - MAIM
    # -
    # evalOrderTSL
    cmds.formLayout(evaluationOrderFL, e=True,
                  af=[(evalOrderTSL, 'left', 5), (evalOrderTSL, 'bottom', 5), (evalOrderTSL, 'top', 5)])
    cmds.formLayout(evaluationOrderFL, e=True, ap=[(evalOrderTSL, 'right', 5, 50)])
    # evalOrderRootB
    cmds.formLayout(evaluationOrderFL, e=True, af=[(evalOrderRootB, 'top', 5), (evalOrderRootB, 'right', 5)])
    cmds.formLayout(evaluationOrderFL, e=True, ap=[(evalOrderRootB, 'left', 5, 50)])
    # evalOrderBuildB
    cmds.formLayout(evaluationOrderFL, e=True, af=[(evalOrderBuildB, 'right', 5)])
    cmds.formLayout(evaluationOrderFL, e=True, ac=[(evalOrderBuildB, 'top', 5, evalOrderRootB)])
    cmds.formLayout(evaluationOrderFL, e=True, ap=[(evalOrderBuildB, 'left', 5, 50)])

    cmds.formLayout(evaluationOrderFL, e=True, af=[(evalOrderReorderSEP, 'right', 5)])
    cmds.formLayout(evaluationOrderFL, e=True, ac=[(evalOrderReorderSEP, 'top', 5, evalOrderBuildB)])
    cmds.formLayout(evaluationOrderFL, e=True, ap=[(evalOrderReorderSEP, 'left', 5, 50)])

    # evalOrderIKB
    cmds.formLayout(evaluationOrderFL, e=True, af=[(evalOrderIKB, 'right', 5)])
    cmds.formLayout(evaluationOrderFL, e=True, ac=[(evalOrderIKB, 'top', 5, evalOrderReorderSEP)])
    cmds.formLayout(evaluationOrderFL, e=True, ap=[(evalOrderIKB, 'left', 5, 50)])
    # evalOrderConstraintB
    cmds.formLayout(evaluationOrderFL, e=True, af=[(evalOrderConstraintB, 'right', 5)])
    cmds.formLayout(evaluationOrderFL, e=True, ac=[(evalOrderConstraintB, 'top', 5, evalOrderIKB)])
    cmds.formLayout(evaluationOrderFL, e=True, ap=[(evalOrderConstraintB, 'left', 5, 50)])

    cmds.formLayout(evaluationOrderFL, e=True, af=[(evalOrderReduceSEP, 'right', 5)])
    cmds.formLayout(evaluationOrderFL, e=True, ac=[(evalOrderReduceSEP, 'top', 5, evalOrderConstraintB)])
    cmds.formLayout(evaluationOrderFL, e=True, ap=[(evalOrderReduceSEP, 'left', 5, 50)])

    # evalOrderReduceB
    cmds.formLayout(evaluationOrderFL, e=True, af=[(evalOrderReduceB, 'right', 5)])
    cmds.formLayout(evaluationOrderFL, e=True, ac=[(evalOrderReduceB, 'top', 5, evalOrderReduceSEP)])
    cmds.formLayout(evaluationOrderFL, e=True, ap=[(evalOrderReduceB, 'left', 5, 50)])

    cmds.formLayout(evaluationOrderFL, e=True, af=[(evalOrderMoveSEP, 'right', 5)])
    cmds.formLayout(evaluationOrderFL, e=True, ac=[(evalOrderMoveSEP, 'top', 5, evalOrderReduceB)])
    cmds.formLayout(evaluationOrderFL, e=True, ap=[(evalOrderMoveSEP, 'left', 5, 50)])

    # evalOrderMoveUpB
    cmds.formLayout(evaluationOrderFL, e=True, af=[(evalOrderMoveUpB, 'right', 5)])
    cmds.formLayout(evaluationOrderFL, e=True, ac=[(evalOrderMoveUpB, 'top', 5, evalOrderMoveSEP)])
    cmds.formLayout(evaluationOrderFL, e=True, ap=[(evalOrderMoveUpB, 'left', 5, 50)])
    # evalOrderMoveDnB
    cmds.formLayout(evaluationOrderFL, e=True, af=[(evalOrderMoveDnB, 'right', 5)])
    cmds.formLayout(evaluationOrderFL, e=True, ac=[(evalOrderMoveDnB, 'top', 5, evalOrderMoveUpB)])
    cmds.formLayout(evaluationOrderFL, e=True, ap=[(evalOrderMoveDnB, 'left', 5, 50)])
    # evalOrderMoveToBottomB
    cmds.formLayout(evaluationOrderFL, e=True, af=[(evalOrderMoveToBottomB, 'right', 5)])
    cmds.formLayout(evaluationOrderFL, e=True, ac=[(evalOrderMoveToBottomB, 'top', 5, evalOrderMoveDnB)])
    cmds.formLayout(evaluationOrderFL, e=True, ap=[(evalOrderMoveToBottomB, 'left', 5, 50)])

    cmds.formLayout(evaluationOrderFL, e=True, af=[(evalOrderAddAttrSEP, 'right', 5)])
    cmds.formLayout(evaluationOrderFL, e=True, ac=[(evalOrderAddAttrSEP, 'top', 5, evalOrderMoveToBottomB)])
    cmds.formLayout(evaluationOrderFL, e=True, ap=[(evalOrderAddAttrSEP, 'left', 5, 50)])

    # evalOrderAddAttrB
    cmds.formLayout(evaluationOrderFL, e=True, af=[(evalOrderAddAttrB, 'right', 5)])
    cmds.formLayout(evaluationOrderFL, e=True, ac=[(evalOrderAddAttrB, 'top', 5, evalOrderAddAttrSEP)])
    cmds.formLayout(evaluationOrderFL, e=True, ap=[(evalOrderAddAttrB, 'left', 5, 50)])

    # Show Window
    cmds.showWindow(win)


def evalOrderUIrefreshList(evalOrderList=[]):
    """
    UI method for Evaluation Order setup tools
    Refreshes the evaluation order textScrollList
    """
    # Get evalOrder list
    if not evalOrderList: evalOrderList = gEvalOrder.hierarchy.generationList()
    # Display evaluation order list in UI
    cmds.textScrollList('evalOrderTSL', e=True, ra=True)
    for item in evalOrderList: cmds.textScrollList('evalOrderTSL', e=True, a=item)


def evalOrderUIsetRoot():
    """
    UI method for Evaluation Order setup tools
    Set the root of the evaluation order to the selected object
    """
    # Check window
    win = 'evaluationOrderUI'
    if not cmds.window(win, q=True, ex=True):
        raise UserInputError('Evaluation Order UI is not open!!')

    # Get Selection
    sel = cmds.ls(sl=True, type='transform')
    if not sel: return

    # Add first selected item as root of evaluation order list
    cmds.textScrollList('evalOrderTSL', e=True, ra=True)
    cmds.textScrollList('evalOrderTSL', e=True, a=sel[0])


def evalOrderUIbuildHierarchy():
    """
    UI method for Evaluation Order setup tools
    Build evaluation order list from hierarchy root object
    """
    global gEvalOrder

    # Check window
    win = 'evaluationOrderUI'
    if not cmds.window(win, q=True, ex=True):
        raise UserInputError('Evaluation Order UI is not open!!')

    # Get root object
    rootList = cmds.textScrollList('evalOrderTSL', q=True, ai=True)
    if not rootList: raise UserInputError('Specify a hierarchy root!')

    # Build hierarchy list
    gEvalOrder = glTools.tools.evaluationOrder.EvaluationOrder(rootList[0], debug=True)

    # Display evaluation order list in UI
    evalOrderUIrefreshList()


def evalOrderUIreorderIK():
    """
    UI method for Evaluation Order setup tools
    Reorder the evaluation order based on IK dependencies
    """
    global gEvalOrder

    # Check window
    win = 'evaluationOrderUI'
    if not cmds.window(win, q=True, ex=True):
        raise UserInputError('Evaluation Order UI is not open!!')

    # Reorder using IK
    gEvalOrder.ikReorder()

    # Display evaluation order list in UI
    evalOrderUIrefreshList()


def evalOrderUIreorderConstraints():
    """
    UI method for Evaluation Order setup tools
    Reorder the evaluation order based on constraint dependencies
    """
    global gEvalOrder

    # Check window
    win = 'evaluationOrderUI'
    if not cmds.window(win, q=True, ex=True):
        raise UserInputError('Evaluation Order UI is not open!!')

    # Reorder using IK
    gEvalOrder.constraintReorder()

    # Display evaluation order list in UI
    evalOrderUIrefreshList()


def evalOrderUIreduceToSelection():
    """
    UI method for Evaluation Order setup tools
    Reduce the evaluation order list to the selected objects
    """
    global gEvalOrder

    # Check window
    win = 'evaluationOrderUI'
    if not cmds.window(win, q=True, ex=True):
        raise UserInputError('Evaluation Order UI is not open!!')

    # Get selection
    sel = cmds.ls(sl=True)
    if not sel: return

    # Get evalOrder list
    evalOrderList = gEvalOrder.hierarchy.generationList()
    evalIntersectList = [i for i in evalOrderList if sel.count(i)]

    # Display evaluation order list in UI
    evalOrderUIrefreshList(evalIntersectList)


def evalOrderUIaddAttr():
    """
    UI method for Evaluation Order setup tools
    Add the evaluation order list as an attribute to the root object
    """
    global gEvalOrder

    # Check window
    win = 'evaluationOrderUI'
    if not cmds.window(win, q=True, ex=True):
        raise UserInputError('Evaluation Order UI is not open!!')

    # Get evaluation order list
    evalOrderList = gEvalOrder.hierarchy.generationList()
    if not evalOrderList: raise UserInputError('Evaluation order list invalid!!')
    # Determine hierarchy root
    evalOrderRoot = evalOrderList[0]

    # Get intersectionList
    intersectList = cmds.textScrollList('evalOrderTSL', q=True, ai=True)
    if not intersectList: return

    # Add list attribute to root object
    gEvalOrder.setAttr(evalOrderRoot, intersectList=intersectList, evalOrderList=evalOrderList)


def matchRulesUI():
    """
    Main UI method for Pose Match setup tools
    """
    # Window
    win = 'matchRulesUI'
    if cmds.window(win, q=True, ex=True): cmds.deleteUI(win)
    win = cmds.window(win, t='Pose Match Rules')

    # Form Layout
    evaluationOrderFL = cmds.formLayout(numberOfDivisions=100)

    # Pivot Object
    pivotTFB = cmds.textFieldButtonGrp('matchRulesPivotTFB', label='Pivot Object', text='', buttonLabel='Load Selected')

    # Mirror Axis
    axisList = ['X', 'Y', 'Z']
    axisOMG = cmds.optionMenuGrp('matchRulesAxisOMG', label='Mirror Axis')
    for axis in axisList: cmds.menuItem(label=axis)

    # Mirror Mode
    modeList = ['World', 'Local']
    modeOMG = cmds.optionMenuGrp('matchRulesModeOMG', label='Mirror Mode')
    for mode in modeList: cmds.menuItem(label=mode)

    # Search/Replace Field
    searchTFG = cmds.textFieldGrp('matchRulesSearchTFG', label='Search', text='lf_')
    replaceTFG = cmds.textFieldGrp('matchRulesReplaceTFG', label='Replace', text='rt_')

    # Separator
    sep = cmds.separator(height=10, style='single')

    # Buttons
    twinMatchB = cmds.button('matchRulesTwinMatchB', l='Setup Twin Match',
                           c='glTools.ui.poseMatch.setTwinMatchAttrsFromUI()')
    selfPivotB = cmds.button('matchRulesSelfPivotB', l='Setup Self Pivot',
                           c='glTools.ui.poseMatch.setSelfPivotAttrsFromUI()')
    closeB = cmds.button('matchRulesCloseB', l='Close', c='cmds.deleteUI("' + win + '")')

    # UI Callbacks
    cmds.textFieldButtonGrp(pivotTFB, e=True, bc='glTools.ui.utils.loadTypeSel("' + pivotTFB + '","","transform")')

    # Form Layout - MAIN
    cmds.formLayout(evaluationOrderFL, e=True, af=[(pivotTFB, 'left', 5), (pivotTFB, 'top', 5), (pivotTFB, 'right', 5)])
    cmds.formLayout(evaluationOrderFL, e=True, af=[(axisOMG, 'left', 5), (axisOMG, 'right', 5)])
    cmds.formLayout(evaluationOrderFL, e=True, ac=[(axisOMG, 'top', 5, pivotTFB)])
    cmds.formLayout(evaluationOrderFL, e=True, af=[(modeOMG, 'left', 5), (modeOMG, 'right', 5)])
    cmds.formLayout(evaluationOrderFL, e=True, ac=[(modeOMG, 'top', 5, axisOMG)])
    cmds.formLayout(evaluationOrderFL, e=True, af=[(searchTFG, 'left', 5), (searchTFG, 'right', 5)])
    cmds.formLayout(evaluationOrderFL, e=True, ac=[(searchTFG, 'top', 5, modeOMG)])
    cmds.formLayout(evaluationOrderFL, e=True, af=[(replaceTFG, 'left', 5), (replaceTFG, 'right', 5)])
    cmds.formLayout(evaluationOrderFL, e=True, ac=[(replaceTFG, 'top', 5, searchTFG)])
    cmds.formLayout(evaluationOrderFL, e=True, af=[(sep, 'left', 5), (sep, 'right', 5)])
    cmds.formLayout(evaluationOrderFL, e=True, ac=[(sep, 'top', 5, replaceTFG)])
    cmds.formLayout(evaluationOrderFL, e=True, af=[(twinMatchB, 'left', 5)], ap=[(twinMatchB, 'right', 5, 50)])
    cmds.formLayout(evaluationOrderFL, e=True, ac=[(twinMatchB, 'top', 5, sep)])
    cmds.formLayout(evaluationOrderFL, e=True, af=[(selfPivotB, 'right', 5)], ap=[(selfPivotB, 'left', 5, 50)])
    cmds.formLayout(evaluationOrderFL, e=True, ac=[(selfPivotB, 'top', 5, sep)])
    cmds.formLayout(evaluationOrderFL, e=True, af=[(closeB, 'left', 5), (closeB, 'right', 5)])
    cmds.formLayout(evaluationOrderFL, e=True, ac=[(closeB, 'top', 5, selfPivotB)])

    # Show Window
    cmds.showWindow(win)


def setTwinMatchAttrsFromUI():
    """
    UI method for Pose Match setup tools
    Setup pose twin attributes from UI
    """
    # Get selection
    sel = cmds.ls(sl=True, type=['transform', 'joint'])
    if not sel: return

    # Window
    win = 'matchRulesUI'
    if not cmds.window(win, q=True, ex=True): raise UserInputError('Pose Match UI does not exist!!')

    # Pivot
    pivotObj = str(cmds.textFieldButtonGrp('matchRulesPivotTFB', q=True, text=True))

    # Axis
    axis = str(cmds.optionMenuGrp('matchRulesAxisOMG', q=True, v=True)).lower()

    # Mode
    mode = cmds.optionMenuGrp('matchRulesModeOMG', q=True, sl=True) - 1

    # Search/Replace
    search = str(cmds.textFieldGrp('matchRulesSearchTFG', q=True, text=True))
    replace = str(cmds.textFieldGrp('matchRulesReplaceTFG', q=True, text=True))

    # Set match rules attributes
    glTools.tools.match.Match().setTwinMatchAttrs(sel, pivotObj, axis, mode, search, replace)


def setSelfPivotAttrsFromUI():
    """
    UI method for Pose Match setup tools
    Setup self pivot pose attributes from UI
    """
    # Get selection
    sel = cmds.ls(sl=True, type=['transform', 'joint'])
    if not sel: return

    # Window
    win = 'matchRulesUI'
    if not cmds.window(win, q=True, ex=True): raise UserInputError('Pose Match UI does not exist!!')

    # Axis
    axis = str(cmds.optionMenuGrp('matchRulesAxisOMG', q=True, v=True)).lower()

    # Mode
    mode = cmds.optionMenuGrp('matchRulesModeOMG', q=True, sl=True) - 1

    # Set match rules attributes
    glTools.tools.match.Match().setSelfPivotAttrs(sel, axis, mode)
