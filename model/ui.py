import maya.cmds as cmds


def displayListWindow(itemList, title):
    """
    @param itemList:
    @param title:
    """
    # Check itemList
    if not itemList: return

    # Window
    window = 'displayListWindowUI'
    if cmds.window(window, q=True, ex=True): cmds.deleteUI(window)
    window = cmds.window(window, t=title, s=True)

    # Layout
    FL = cmds.formLayout(numberOfDivisions=100)

    # UI Elements
    TSL = cmds.textScrollList('displayListWindowTSL', allowMultiSelection=True)
    for item in itemList: cmds.textScrollList(TSL, e=True, a=item)
    cmds.textScrollList(TSL, e=True, sc='glTools.ui.utils.selectFromTSL("' + TSL + '")')
    closeB = cmds.button('displayListWindowB', l='Close', c='cmds.deleteUI("' + window + '")')

    # Form Layout
    cmds.formLayout(FL, e=True, af=[(TSL, 'top', 5), (TSL, 'left', 5), (TSL, 'right', 5)])
    cmds.formLayout(FL, e=True, af=[(closeB, 'bottom', 5), (closeB, 'left', 5), (closeB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(TSL, 'bottom', 5, closeB)])

    # Display Window
    cmds.showWindow(window)


def reportWindow(msg, title):
    """
    @param msg:
    @param title:
    """
    # Check message
    if not msg: return

    # Window
    window = 'reportWindowUI'
    if cmds.window(window, q=True, ex=True): cmds.deleteUI(window)
    window = cmds.window(window, t=title, s=True)

    # Layout
    FL = cmds.formLayout(numberOfDivisions=100)

    # UI Elements
    reportSF = cmds.scrollField('reportWindowSF', editable=False, wordWrap=True, text=msg)
    closeB = cmds.button('reportWindowB', l='Close', c='cmds.deleteUI("' + window + '")')

    # Form Layout
    cmds.formLayout(FL, e=True, af=[(reportSF, 'top', 5), (reportSF, 'left', 5), (reportSF, 'right', 5)])
    cmds.formLayout(FL, e=True, af=[(closeB, 'bottom', 5), (closeB, 'left', 5), (closeB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(reportSF, 'bottom', 5, closeB)])

    # Display Window
    cmds.showWindow(window)
