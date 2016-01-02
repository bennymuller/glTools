import maya.mel as mel
import maya.cmds as cmds
import glTools.ui.utils
import os


def workfileBatchUI():
    """
    Workfile Batch Window
    """
    # Window
    window = 'workfileBatchUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Workfile Batch Manager')

    # Layout
    FL = cmds.formLayout()

    # ===============
    # - UI Elements -
    # ===============

    cw = 100

    # WorkFile List
    workfileTXT = cmds.text(label='Workfile List')
    workfileTSL = cmds.textScrollList('workfileBatchTSL', allowMultiSelection=True)
    workfileAddB = cmds.button(label='Add',
                             c='glTools.tools.workfileBatch.workfileBatchUI_addFiles("' + workfileTSL + '")')
    workfileDelB = cmds.button(label='Remove', c='glTools.ui.utils.removeFromTSL("' + workfileTSL + '")')

    workfileListSep = cmds.separator(style='single')

    pyCmdFileTFB = cmds.textFieldButtonGrp('wfBatch_pyCmdFileTFB', label='PyCmdFile', text='', buttonLabel='...',
                                         cw=(1, cw))
    cmds.textFieldButtonGrp(pyCmdFileTFB, e=True,
                          bc='glTools.tools.workfileBatch.workfileBatchUI_addPyCmd("' + pyCmdFileTFB + '")')

    pyCmdFileSep = cmds.separator(style='single')

    versionUpCBG = cmds.checkBoxGrp('wfBatch_versionUpCBG', numberOfCheckBoxes=1, label='Version Up', v1=False,
                                  cw=(1, cw))
    snapshotCBG = cmds.checkBoxGrp('wfBatch_snapshotCBG', numberOfCheckBoxes=1, label='Snapshot', v1=False, cw=(1, cw))
    publishCBG = cmds.checkBoxGrp('wfBatch_publishCBG', numberOfCheckBoxes=1, label='Publish', v1=False, cw=(1, cw),
                                en=False)

    publishNotesTXT = cmds.text(label='Snapshot/Publish Notes')
    publishNotesSF = cmds.scrollField('wfBatch_publishNoteSF', editable=True, wordWrap=True,
                                    text='Snapshot generated from workfile batch process.', en=False)

    workfileBatchB = cmds.button(label='Batch', c='glTools.tools.workfileBatch.workfileBatchFromUI()')
    workfileCloseB = cmds.button(label='Close', c='cmds.deleteUI("' + window + '")')

    # ========================
    # - UI Callback Commands -
    # ========================

    cmds.checkBoxGrp(snapshotCBG, e=True, cc='glTools.tools.workfileBatch.workfileBatchUI_toggleSnapshot()')

    # ================
    # - Form Layouts -
    # ================

    cmds.formLayout(FL, e=True, af=[(workfileTXT, 'top', 5), (workfileTXT, 'left', 5), (workfileTXT, 'right', 5)])
    cmds.formLayout(FL, e=True, af=[(workfileTSL, 'left', 5), (workfileTSL, 'right', 5)],
                  ac=[(workfileTSL, 'top', 5, workfileTXT), (workfileTSL, 'bottom', 5, workfileAddB)])
    cmds.formLayout(FL, e=True, af=[(workfileAddB, 'left', 5)], ac=[(workfileAddB, 'bottom', 5, workfileListSep)],
                  ap=[(workfileAddB, 'right', 5, 50)])
    cmds.formLayout(FL, e=True, af=[(workfileDelB, 'right', 5)], ac=[(workfileDelB, 'bottom', 5, workfileListSep)],
                  ap=[(workfileDelB, 'left', 5, 50)])
    cmds.formLayout(FL, e=True, af=[(workfileListSep, 'left', 5), (workfileListSep, 'right', 5)],
                  ac=[(workfileListSep, 'bottom', 5, pyCmdFileTFB)])
    cmds.formLayout(FL, e=True, af=[(pyCmdFileTFB, 'left', 5), (pyCmdFileTFB, 'right', 5)],
                  ac=[(pyCmdFileTFB, 'bottom', 5, pyCmdFileSep)])
    cmds.formLayout(FL, e=True, af=[(pyCmdFileSep, 'left', 5), (pyCmdFileSep, 'right', 5)],
                  ac=[(pyCmdFileSep, 'bottom', 5, versionUpCBG)])
    cmds.formLayout(FL, e=True, af=[(versionUpCBG, 'left', 5), (versionUpCBG, 'right', 5)],
                  ac=[(versionUpCBG, 'bottom', 5, snapshotCBG)])
    cmds.formLayout(FL, e=True, af=[(snapshotCBG, 'left', 5), (snapshotCBG, 'right', 5)],
                  ac=[(snapshotCBG, 'bottom', 5, publishCBG)])
    cmds.formLayout(FL, e=True, af=[(publishCBG, 'left', 5), (publishCBG, 'right', 5)],
                  ac=[(publishCBG, 'bottom', 5, publishNotesTXT)])
    cmds.formLayout(FL, e=True, af=[(publishNotesTXT, 'left', 5), (publishNotesTXT, 'right', 5)],
                  ac=[(publishNotesTXT, 'bottom', 5, publishNotesSF)])
    cmds.formLayout(FL, e=True, af=[(publishNotesSF, 'left', 5), (publishNotesSF, 'right', 5)],
                  ac=[(publishNotesSF, 'bottom', 5, workfileBatchB)])
    cmds.formLayout(FL, e=True, af=[(workfileBatchB, 'left', 5), (workfileBatchB, 'bottom', 5)],
                  ap=[(workfileBatchB, 'right', 5, 50)])
    cmds.formLayout(FL, e=True, af=[(workfileCloseB, 'right', 5), (workfileCloseB, 'bottom', 5)],
                  ap=[(workfileCloseB, 'left', 5, 50)])

    # ===============
    # - Show Window -
    # ===============

    cmds.showWindow(window)


def workfileBatchUI_addFiles(TSL):
    """
    Open file dialog to select files to add to workfile batch list
    @param TSL: TextScrollList to add files to
    @type TSL: str
    """
    # Get Existing Workfile List
    workfileList = cmds.textScrollList(TSL, q=True, ai=True) or []

    # Get Workfile List
    fileFilter = 'Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb)'
    workfileSel = cmds.fileDialog2(fileFilter=fileFilter, dialogStyle=2, fileMode=4, cap='Workfile Batch - Add Files')

    # Add Files to List
    for workfile in workfileSel:
        if not workfile in workfileList:
            cmds.textScrollList(TSL, e=True, a=workfile)


def workfileBatchUI_addPyCmd(TFB):
    """
    Open file dialog to select python comand file to run on workfiles
    @param TFB: textFieldButtonGrp to add file to
    @type TFB: str
    """
    # Get Python Command File
    pyCmdFile = cmds.fileDialog2(fileFilter='*.py', dialogStyle=2, fileMode=1, cap='Workfile Batch - Select Command File')

    # Update textFieldButtonGrp
    if pyCmdFile: cmds.textFieldButtonGrp(TFB, e=True, text=pyCmdFile[0])


def workfileBatchUI_toggleSnapshot():
    """
    """
    snapshot = cmds.checkBoxGrp('wfBatch_snapshotCBG', q=True, v1=True)
    cmds.checkBoxGrp('wfBatch_publishCBG', e=True, en=snapshot)
    cmds.scrollField('wfBatch_publishNoteSF', e=True, en=snapshot)


def workfileBatchFromUI():
    """
    Workfile Batch From UI
    """
    # Get Workfile List
    workfileList = cmds.textScrollList('workfileBatchTSL', q=True, ai=True)

    # Get Workfile Batch Data
    cmdsFile = cmds.textFieldButtonGrp('wfBatch_pyCmdFileTFB', q=True, text=True)
    versionUp = cmds.checkBoxGrp('wfBatch_versionUpCBG', q=True, v1=True)
    snapshot = cmds.checkBoxGrp('wfBatch_snapshotCBG', q=True, v1=True)
    publish = cmds.checkBoxGrp('wfBatch_publishCBG', q=True, v1=True)
    publishNote = cmds.scrollField('wfBatch_publishNoteSF', q=True, text=True)

    # For Each Workfile
    for workfile in workfileList:
        workfileBatch(workfile=workfile,
                      cmdsFile=cmdsFile,
                      versionUp=versionUp,
                      snapshot=snapshot,
                      publish=publish,
                      publishNote=publishNote)


def workfileBatch(workfile, cmdsFile='', versionUp=False, snapshot=False, publish=False, publishNote=''):
    """
    Workfile batch.
    @param workfile: Workfile to batch process
    @type workfile: str
    @param cmdsFile: Optional python command file to run on workfile
    @type cmdsFile: str
    @param versionUp: Version up workfile
    @type versionUp: bool
    @param snapshot: Snapshot workfile
    @type snapshot: bool
    @param publish: Publish workfile
    @type publish: bool
    @param publishNote: Snapshot/Publish notes
    @type publishNote: str
    """
    # Build Workfile Batch Command
    workfileBatchCmd = "workfileBatch"
    workfileBatchCmd += " " + workfile
    workfileBatchCmd += " " + cmdsFile
    workfileBatchCmd += " " + str(int(versionUp))
    workfileBatchCmd += " " + str(int(snapshot))
    workfileBatchCmd += " " + str(int(publish))
    workfileBatchCmd += " '" + publishNote + "'"

    # Get Workfile Basename
    fileName = os.path.basename(workfile)

    # Execute Workfile Batch Command
    os.system('xterm -hold -T "' + fileName + '" -e "' + workfileBatchCmd + '" &')


def workfileBatchSubmit(workfile, cmdsFile='', versionUp=False, snapshot=False, publish=False, publishNote=''):
    """
    Workfile batch submit to qube.
    @param workfile: Workfile to batch process
    @type workfile: str
    @param cmdsFile: Optional python command file to run on workfile
    @type cmdsFile: str
    @param versionUp: Version up workfile
    @type versionUp: bool
    @param snapshot: Snapshot workfile
    @type snapshot: bool
    @param publish: Publish workfile
    @type publish: bool
    @param publishNote: Snapshot/Publish notes
    @type publishNote: str
    """
    # Build Workfile Batch Command
    workfileBatchCmd = "/"  ######!!!!!
    workfileBatchCmd += " " + workfile
    workfileBatchCmd += " " + cmdsFile
    workfileBatchCmd += " " + str(int(versionUp))
    workfileBatchCmd += " " + str(int(snapshot))
    workfileBatchCmd += " " + str(int(publish))
    workfileBatchCmd += " '" + publishNote + "'"

    # Submit Workfile Batch Command to Qube
    os.system('qbsub --name maya_workfile_batch --shell /bin/tcsh --cluster /ent/hbm/vfx  -e "' + workfileBatchCmd)
