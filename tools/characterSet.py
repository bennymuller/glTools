import maya.mel as mel
import maya.cmds as cmds
import glTools.utils.clip
import glTools.utils.characterSet
import glTools.utils.namespace


def charSetSelectUI():
    """
    """
    # Window
    window = 'charSetSelectUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Character Set Selector', wh=[350, 500])

    # Layout
    FL = cmds.formLayout(numberOfDivisions=100)

    # ===============
    # - UI Elements -
    # ===============

    # Create Character Set List
    charList = cmds.ls(type='character') or []
    charListTSL = cmds.textScrollList('charSetSelect_charListTSL', ams=False)
    for char in charList: cmds.textScrollList(charListTSL, e=True, a=char)

    # Create List Callback
    cmds.textScrollList(charListTSL, e=True,
                      sc='import glTools.tools.characterSet;reload(glTools.tools.characterSet);glTools.tools.characterSet.setCurrentFromUI()')

    # Pop-up Menu
    cmds.popupMenu(p=charListTSL)
    cmds.menuItem('Set from Selection', c='glTools.tools.characterSet.setCurrentFromSelection()')

    # ===============
    # - Form Layout -
    # ===============
    cmds.formLayout(FL, e=True, af=[(charListTSL, 'top', 5), (charListTSL, 'left', 5), (charListTSL, 'right', 5),
                                  (charListTSL, 'bottom', 5)])

    # ===============
    # - Show Window -
    # ===============

    cmds.showWindow(window)


def setCurrentFromUI():
    """
    """
    # Get Selected Character Set From UI
    char = cmds.textScrollList('charSetSelect_charListTSL', q=True, si=True)[0]
    glTools.utils.characterSet.setCurrent(char)


def setCurrentFromSelection():
    """
    """
    # Get Selected Character Set From Scene
    sel = cmds.ls(sl=1)
    NSlist = glTools.utils.namespace.getNSList(sel, topOnly=True)
    if not NSlist:
        print('No selected namespaces! Unable to set current character set...')

    # Find Character Sets in Selected Namespace
    char = cmds.ls(NSlist[0] + ':*', type='character')
    if not char:
        print('No character set in selected namespace! Unable to set current character set...')

    # Get UI Character Set List
    charListTSL = cmds.textScrollList('charSetSelect_charListTSL', q=True, ai=True)
    if char[0] in charListTSL:
        cmds.textScrollList('charSetSelect_charListTSL', e=True, si=char[0])
    else:
        print('Character set "' + char[0] + '" not found in UI list! Skipping UI selection...')

    # Set Current Character Set
    glTools.utils.characterSet.setCurrent(char[0])
