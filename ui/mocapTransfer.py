import maya.cmds as cmds
import glTools.anim.mocap_utils
import glTools.ui.utils


def create():
    """
    Mocap Transfer UI.
    """
    # ============
    # - Build UI -
    # ============

    # Window
    window = 'mocapTransferUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, title='Mocap/Anim Transfer', sizeable=True)

    # FormLayout
    FL = cmds.formLayout(numberOfDivisions=100)

    # Buttons
    transferB = cmds.button(label='Transfer', c='glTools.ui.mocapTransfer.transferFromUI()')
    closeB = cmds.button(label='Close', c='cmds.deleteUI("' + window + '")')

    # FrameLayout
    cmds.setParent(FL)
    rangeLayout = cmds.frameLayout(label='Bake Range', borderStyle='in')

    # TabLayout
    cmds.setParent(FL)
    tabLayout = cmds.tabLayout('mocapXferTabLayout', innerMarginWidth=5, innerMarginHeight=5)

    cmds.formLayout(FL, e=True, af=[(closeB, 'left', 5), (closeB, 'right', 5), (closeB, 'bottom', 5)])
    cmds.formLayout(FL, e=True, af=[(transferB, 'left', 5), (transferB, 'right', 5)],
                  ac=[(transferB, 'bottom', 5, closeB)])
    cmds.formLayout(FL, e=True, af=[(tabLayout, 'left', 5), (tabLayout, 'right', 5), (tabLayout, 'top', 5)])
    cmds.formLayout(FL, e=True, af=[(rangeLayout, 'left', 5), (rangeLayout, 'right', 5)],
                  ac=[(rangeLayout, 'top', 5, tabLayout), (rangeLayout, 'bottom', 5, transferB)])

    # ----------------
    # - Range Layout -
    # ----------------

    cmds.setParent(rangeLayout)

    # FormLayout
    bakeRangeFL = cmds.formLayout(numberOfDivisions=100)

    mocap_rangeCBG = cmds.checkBoxGrp('xferMocap_bakeRangeCBG', label='Specify Bake Range:', numberOfCheckBoxes=1,
                                    value1=0)
    mocap_startEndIFG = cmds.intFieldGrp('xferMocap_startEndCBG', label='Bake Range Start/End:', numberOfFields=2,
                                       value1=0, value2=0, en=False)
    mocap_staticChanCBG = cmds.checkBoxGrp('xferMocap_staticChanCBG', label='Delete Static Channels:',
                                         numberOfCheckBoxes=1, value1=0)

    cmds.formLayout(bakeRangeFL, e=True,
                  af=[(mocap_rangeCBG, 'left', 5), (mocap_rangeCBG, 'right', 5), (mocap_rangeCBG, 'top', 5)])
    cmds.formLayout(bakeRangeFL, e=True, af=[(mocap_startEndIFG, 'left', 5), (mocap_startEndIFG, 'right', 5)],
                  ac=[(mocap_startEndIFG, 'top', 5, mocap_rangeCBG)])
    cmds.formLayout(bakeRangeFL, e=True, af=[(mocap_staticChanCBG, 'left', 5), (mocap_staticChanCBG, 'right', 5)],
                  ac=[(mocap_staticChanCBG, 'top', 5, mocap_startEndIFG)])

    # UI Element Callbacks
    cmds.checkBoxGrp(mocap_rangeCBG, e=True, cc='glTools.ui.mocapTransfer.toggleBakeRange()')

    # ---------------------
    # - FROM Mocap Layout -
    # ---------------------

    cmds.setParent(tabLayout)

    # FormLayout
    fromMocapFL = cmds.formLayout(numberOfDivisions=100)

    # Layout Elements
    fromMocap_mocapTFB = cmds.textFieldButtonGrp('fromMocap_mocapTFB', label='Mocap NS:', text='', buttonLabel='<<<')
    fromMocap_rigTFB = cmds.textFieldButtonGrp('fromMocap_rigTFB', label='Rig NS:', text='', buttonLabel='<<<')
    fromMocap_SEP = cmds.separator(height=10, style='single')
    fromMocap_xferToRBG = cmds.radioButtonGrp('fromMocap_xferToRBG', label='Transfer To:', numberOfRadioButtons=2,
                                            labelArray2=['Controls', 'Overrides'], select=2)
    fromMocap_xferHandCBG = cmds.checkBoxGrp('fromMocap_xferHandCBG', label='Transfer Fingers:', numberOfCheckBoxes=1,
                                           value1=0)

    cmds.formLayout(fromMocapFL, e=True, af=[(fromMocap_mocapTFB, 'left', 5), (fromMocap_mocapTFB, 'right', 5),
                                           (fromMocap_mocapTFB, 'top', 5)])
    cmds.formLayout(fromMocapFL, e=True, af=[(fromMocap_rigTFB, 'left', 5), (fromMocap_rigTFB, 'right', 5)],
                  ac=[(fromMocap_rigTFB, 'top', 5, fromMocap_mocapTFB)])
    cmds.formLayout(fromMocapFL, e=True, af=[(fromMocap_SEP, 'left', 5), (fromMocap_SEP, 'right', 5)],
                  ac=[(fromMocap_SEP, 'top', 5, fromMocap_rigTFB)])
    cmds.formLayout(fromMocapFL, e=True, af=[(fromMocap_xferToRBG, 'left', 5), (fromMocap_xferToRBG, 'right', 5)],
                  ac=[(fromMocap_xferToRBG, 'top', 5, fromMocap_SEP)])
    cmds.formLayout(fromMocapFL, e=True, af=[(fromMocap_xferHandCBG, 'left', 5), (fromMocap_xferHandCBG, 'right', 5)],
                  ac=[(fromMocap_xferHandCBG, 'top', 5, fromMocap_xferToRBG)])

    # UI Element Callbacks
    cmds.textFieldButtonGrp(fromMocap_mocapTFB, e=True,
                          bc='glTools.ui.utils.loadNsSel("' + fromMocap_mocapTFB + '",topOnly=False)')
    cmds.textFieldButtonGrp(fromMocap_rigTFB, e=True,
                          bc='glTools.ui.utils.loadNsSel("' + fromMocap_rigTFB + '",topOnly=False)')

    # -------------------
    # - TO Mocap Layout -
    # -------------------

    cmds.setParent(tabLayout)

    # FormLayout
    toMocapFL = cmds.formLayout(numberOfDivisions=100)

    # Layout Elements
    toMocap_rigTFB = cmds.textFieldButtonGrp('toMocap_rigTFB', label='Rig NS:', text='', buttonLabel='<<<')
    toMocap_mocapTFB = cmds.textFieldButtonGrp('toMocap_mocapTFB', label='Mocap NS:', text='', buttonLabel='<<<')

    cmds.formLayout(toMocapFL, e=True,
                  af=[(toMocap_rigTFB, 'left', 5), (toMocap_rigTFB, 'right', 5), (toMocap_rigTFB, 'top', 5)])
    cmds.formLayout(toMocapFL, e=True, af=[(toMocap_mocapTFB, 'left', 5), (toMocap_mocapTFB, 'right', 5)],
                  ac=[(toMocap_mocapTFB, 'top', 5, toMocap_rigTFB)])

    # UI Element Callbacks
    cmds.textFieldButtonGrp(toMocap_rigTFB, e=True,
                          bc='glTools.ui.utils.loadNsSel("' + toMocap_rigTFB + '",topOnly=False)')
    cmds.textFieldButtonGrp(toMocap_mocapTFB, e=True,
                          bc='glTools.ui.utils.loadNsSel("' + toMocap_mocapTFB + '",topOnly=False)')

    # ---------------------
    # - Rig TO Rig Layout -
    # ---------------------

    cmds.setParent(tabLayout)

    # FormLayout
    rigToRigFL = cmds.formLayout(numberOfDivisions=100)

    # Layout Elements
    rigToRig_srcTFB = cmds.textFieldButtonGrp('rigToRig_srcTFB', label='Source Rig NS:', text='', buttonLabel='<<<')
    rigToRig_dstTFB = cmds.textFieldButtonGrp('rigToRig_dstTFB', label='Destination Rig NS:', text='', buttonLabel='<<<')
    rigToRig_SEP = cmds.separator(height=10, style='single')
    rigToRig_xferToRBG = cmds.radioButtonGrp('rigToRig_xferToRBG', label='Transfer To:', numberOfRadioButtons=2,
                                           labelArray2=['Controls', 'Overrides'], select=1)
    rigToRig_xferHandCBG = cmds.checkBoxGrp('rigToRig_xferHandCBG', label='Transfer Fingers:', numberOfCheckBoxes=1,
                                          value1=0)
    rigToRig_xferAllTransCBG = cmds.checkBoxGrp('rigToRig_xferAllTransCBG', label='Transfer AllTrans:',
                                              numberOfCheckBoxes=1, value1=0)

    cmds.formLayout(rigToRigFL, e=True,
                  af=[(rigToRig_srcTFB, 'left', 5), (rigToRig_srcTFB, 'right', 5), (rigToRig_srcTFB, 'top', 5)])
    cmds.formLayout(rigToRigFL, e=True, af=[(rigToRig_dstTFB, 'left', 5), (rigToRig_dstTFB, 'right', 5)],
                  ac=[(rigToRig_dstTFB, 'top', 5, rigToRig_srcTFB)])
    cmds.formLayout(rigToRigFL, e=True, af=[(rigToRig_SEP, 'left', 5), (rigToRig_SEP, 'right', 5)],
                  ac=[(rigToRig_SEP, 'top', 5, rigToRig_dstTFB)])
    cmds.formLayout(rigToRigFL, e=True, af=[(rigToRig_xferToRBG, 'left', 5), (rigToRig_xferToRBG, 'right', 5)],
                  ac=[(rigToRig_xferToRBG, 'top', 5, rigToRig_SEP)])
    cmds.formLayout(rigToRigFL, e=True, af=[(rigToRig_xferHandCBG, 'left', 5), (rigToRig_xferHandCBG, 'right', 5)],
                  ac=[(rigToRig_xferHandCBG, 'top', 5, rigToRig_xferToRBG)])
    cmds.formLayout(rigToRigFL, e=True,
                  af=[(rigToRig_xferAllTransCBG, 'left', 5), (rigToRig_xferAllTransCBG, 'right', 5)],
                  ac=[(rigToRig_xferAllTransCBG, 'top', 5, rigToRig_xferHandCBG)])

    # UI Element Callbacks
    cmds.textFieldButtonGrp(rigToRig_srcTFB, e=True,
                          bc='glTools.ui.utils.loadNsSel("' + rigToRig_srcTFB + '",topOnly=False)')
    cmds.textFieldButtonGrp(rigToRig_dstTFB, e=True,
                          bc='glTools.ui.utils.loadNsSel("' + rigToRig_dstTFB + '",topOnly=False)')

    # ---------------------
    # - Label Layout Tabs -
    # ---------------------

    cmds.tabLayout(tabLayout, e=True,
                 tabLabel=((fromMocapFL, 'From Mocap'), (toMocapFL, 'To Mocap'), (rigToRigFL, 'Rig To Rig')))

    # ==============
    # - Display UI -
    # ==============

    initializeBakeRange()

    cmds.window(window, e=True, wh=[445, 330])
    cmds.showWindow(window)


def transferFromUI():
    """
    Transfer mocap animation from UI input.
    """
    # Get Selected Tab
    selTab = cmds.tabLayout('mocapXferTabLayout', q=True, selectTabIndex=True)

    # Get Bake Range
    start = cmds.intFieldGrp('xferMocap_startEndCBG', q=True, v1=True)
    end = cmds.intFieldGrp('xferMocap_startEndCBG', q=True, v2=True)
    deleteStaticChannels = cmds.checkBoxGrp('xferMocap_staticChanCBG', q=True, v1=True)
    if not cmds.checkBoxGrp('xferMocap_bakeRangeCBG', q=True, value1=True):
        start = cmds.playbackOptions(q=True, min=True)
        end = cmds.playbackOptions(q=True, max=True)

    # FROM Mocap
    if selTab == 1:

        # Get Mocap to Rig Input
        mocapNS = cmds.textFieldButtonGrp('fromMocap_mocapTFB', q=True, text=True)
        rigNS = cmds.textFieldButtonGrp('fromMocap_rigTFB', q=True, text=True)
        toCtrls = cmds.radioButtonGrp('fromMocap_xferToRBG', q=True, select=True) == 1
        toHands = cmds.checkBoxGrp('fromMocap_xferHandCBG', q=True, value1=True)

        # Transfer Mocap to Rig
        glTools.anim.mocap_utils.transferMocapToRig(mocapNS=mocapNS,
                                                    rigNS=rigNS,
                                                    toCtrls=toCtrls,
                                                    bakeAnim=True,
                                                    bakeSim=True,
                                                    start=start,
                                                    end=end,
                                                    deleteStaticChannels=deleteStaticChannels)

        if toHands:
            glTools.anim.mocap_utils.transferHandAnim(mocapNS=mocapNS,
                                                      rigNS=rigNS,
                                                      start=start,
                                                      end=end,
                                                      deleteStaticChannels=deleteStaticChannels)

    # TO Mocap
    elif selTab == 2:

        # Get Anim to Mocap Input
        rigNS = cmds.textFieldButtonGrp('toMocap_rigTFB', q=True, text=True)
        mocapNS = cmds.textFieldButtonGrp('toMocap_mocapTFB', q=True, text=True)

        # Transfer Anim to Mocap
        glTools.anim.mocap_utils.transferAnimToMocap(rigNS=rigNS,
                                                     mocapNS=mocapNS,
                                                     bakeAnim=True,
                                                     bakeSim=True,
                                                     start=start,
                                                     end=end,
                                                     deleteStaticChannels=deleteStaticChannels)

    # Rig TO Rig
    elif selTab == 3:

        # Get Anim to Mocap Input
        srcNS = cmds.textFieldButtonGrp('rigToRig_srcTFB', q=True, text=True)
        dstNS = cmds.textFieldButtonGrp('rigToRig_dstTFB', q=True, text=True)
        toCtrls = cmds.radioButtonGrp('rigToRig_xferToRBG', q=True, select=True) == 1
        toHands = cmds.checkBoxGrp('rigToRig_xferHandCBG', q=True, value1=True)
        toAllTrans = cmds.checkBoxGrp('rigToRig_xferAllTransCBG', q=True, value1=True)

        # Transfer Anim to Mocap
        glTools.anim.mocap_utils.transferAnimToRig(srcNS=srcNS,
                                                   dstNS=dstNS,
                                                   attachCtrl=toCtrls,
                                                   attachFingers=toHands,
                                                   attachAllTrans=toAllTrans,
                                                   start=start,
                                                   end=end,
                                                   deleteStaticChannels=deleteStaticChannels)

    # Invalid Tab
    else:
        raise Exception('Invalid tab index!')

    # Return Result
    return


def initializeBakeRange():
    """
    Initialize bake anim range based on playback timeline min/max.
    """
    start = cmds.playbackOptions(q=True, min=True)
    end = cmds.playbackOptions(q=True, max=True)
    cmds.intFieldGrp('xferMocap_startEndCBG', e=True, v1=start, v2=end)


def toggleBakeRange():
    """
    Toggle bake anim range input.
    """
    enable = cmds.checkBoxGrp('xferMocap_bakeRangeCBG', q=True, value1=True)
    cmds.intFieldGrp('xferMocap_startEndCBG', e=True, en=enable)
    if not enable: initializeBakeRange()
