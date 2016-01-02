import maya.cmds as cmds
import glTools.ui.utils
import glTools.utils.base
import glTools.utils.mesh


class UIError(Exception): pass


# Global point list
interactiveSnapSrcList = []
interactiveSnapDstList = []


def interactiveSnapToMeshUI():
    """
    UI for snapToMesh()
    """
    # Window
    window = 'interactiveSnapUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Snap To Mesh - Interactive')

    # Layout
    FL = cmds.formLayout(numberOfDivisions=100)

    # UI Elements
    # ---

    # Target Mesh
    snapMeshTFB = cmds.textFieldButtonGrp('interactiveSnapMeshTFB', label='Target Mesh', text='',
                                        buttonLabel='Load Selected')

    # Slider
    snapFSG = cmds.floatSliderGrp('interactiveSnapFSG', label='Drag:', field=False, minValue=0.0, maxValue=1.0, value=0)
    snapRangeFFG = cmds.floatFieldGrp('interactiveSnapRangeFSG', numberOfFields=2, label='Slider Min/Max', value1=0.0,
                                    value2=1.0)

    # UI Callbacks
    cmds.textFieldButtonGrp(snapMeshTFB, e=True, bc='glTools.ui.utils.loadMeshSel("' + snapMeshTFB + '")')
    cmds.floatSliderGrp('interactiveSnapFSG', e=True, cc='glTools.ui.mesh.interactiveSnapChangeCommand()')
    cmds.floatSliderGrp('interactiveSnapFSG', e=True, dc='glTools.ui.mesh.interactiveSnapDragCommand()')

    # Buttons
    cancelB = cmds.button('interactiveSnapCancelB', l='Cancel', c='cmds.deleteUI("' + window + '")')

    # Form Layout - MAIN
    cmds.formLayout(FL, e=True, af=[(snapMeshTFB, 'top', 5), (snapMeshTFB, 'left', 5), (snapMeshTFB, 'right', 5)])
    cmds.formLayout(FL, e=True, af=[(snapFSG, 'left', 5), (snapFSG, 'right', 5)], ac=[(snapFSG, 'top', 5, snapMeshTFB)])
    cmds.formLayout(FL, e=True, af=[(snapRangeFFG, 'left', 5), (snapRangeFFG, 'right', 5)],
                  ac=[(snapRangeFFG, 'top', 5, snapFSG)])
    cmds.formLayout(FL, e=True, af=[(cancelB, 'left', 5), (cancelB, 'right', 5), (cancelB, 'bottom', 5)])

    # Show Window
    cmds.showWindow(window)


def interactiveSnapUpdateCommand():
    """
    """
    global interactiveSnapSrcList
    global interactiveSnapDstList

    # Clear global lists
    interactiveSnapSrcList = []
    interactiveSnapDstList = []

    # Get current selection
    sel = cmds.ls(sl=1, fl=1)
    if not sel: return

    # Get target mesh
    mesh = cmds.textFieldGrp('interactiveSnapMeshTFB', q=True, text=True)

    # Rebuild global lists
    for i in sel:
        pnt = glTools.utils.base.getPosition(i)
        cpos = glTools.utils.mesh.closestPoint(mesh, pnt)
        interactiveSnapSrcList.append(pnt)
        interactiveSnapDstList.append(cpos)


def interactiveSnapChangeCommand():
    """
    """
    global interactiveSnapSrcList
    global interactiveSnapDstList

    # Clear global lists
    interactiveSnapSrcList = []
    interactiveSnapDstList = []


def interactiveSnapDragCommand():
    """
    """
    global interactiveSnapSrcList
    global interactiveSnapDstList

    # Get current selection
    sel = cmds.ls(sl=1, fl=1)
    if not sel: return

    # Check global list validity
    if not interactiveSnapSrcList or not interactiveSnapDstList:
        interactiveSnapUpdateCommand()

    # Get Snap amount
    amount = cmds.floatSliderGrp('interactiveSnapFSG', q=True, v=True)

    # Move points
    pos = [0, 0, 0]
    for i in range(len(sel)):
        # Calculate new position
        pos[0] = interactiveSnapSrcList[i][0] + ((interactiveSnapDstList[i][0] - interactiveSnapSrcList[i][0]) * amount)
        pos[1] = interactiveSnapSrcList[i][1] + ((interactiveSnapDstList[i][1] - interactiveSnapSrcList[i][1]) * amount)
        pos[2] = interactiveSnapSrcList[i][2] + ((interactiveSnapDstList[i][2] - interactiveSnapSrcList[i][2]) * amount)

        # Set position
        cmds.move(pos[0], pos[1], pos[2], sel[i], ws=True, a=True)


def snapToMeshUI():
    """
    UI for snapToMesh()
    """
    # Window
    window = 'snapToMeshUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Snap To Mesh')

    # Layout
    FL = cmds.formLayout(numberOfDivisions=100)

    # UI Elements
    # ---

    # Mesh
    meshTFB = cmds.textFieldButtonGrp('snapToMeshTFB', label='Target Mesh', text='', buttonLabel='Load Selected')

    # Orient
    orientCBG = cmds.checkBoxGrp('snapToMeshOrientCBG', label='Orient To Face', ncb=1, v1=False)

    # ----------
    # - Orient -
    # ----------

    # Orient Frame
    orientFrameL = cmds.frameLayout('snapToMeshOriFL', l='Orient Options', cll=0, en=0)
    orientFormL = cmds.formLayout(numberOfDivisions=100)

    # OptionMenuGrp
    axList = ['X', 'Y', 'Z', '-X', '-Y', '-Z']
    orientNormAxisOMG = cmds.optionMenuGrp('snapToMeshNormOMG', label='Normal Axis', en=False)
    for ax in axList: cmds.menuItem(label=ax)
    orientUpVecAxisOMG = cmds.optionMenuGrp('snapToMeshUpVecOMG', label='UpVector Axis', en=False)
    for ax in axList: cmds.menuItem(label=ax)
    # Set Default Value
    cmds.optionMenuGrp('snapToMeshUpVecOMG', e=True, sl=2)

    # Up Vector
    upVectorFFG = cmds.floatFieldGrp('snapToMeshUpVecFFG', label='UpVector', nf=3, v1=0, v2=1, v3=0, en=0)
    upVectorObjectTFB = cmds.textFieldButtonGrp('snapToMeshUpVecObjTFG', label='WorldUpObject', text='',
                                              buttonLabel='Load Selected', en=0)

    cmds.setParent('..')
    cmds.setParent('..')

    # UI callback commands
    cmds.textFieldButtonGrp(meshTFB, e=True, bc='glTools.ui.utils.loadMeshSel("' + meshTFB + '")')
    cmds.checkBoxGrp(orientCBG, e=True,
                   cc='glTools.ui.utils.checkBoxToggleLayout("' + orientCBG + '","' + orientFrameL + '")')
    cmds.textFieldButtonGrp(upVectorObjectTFB, e=True, bc='glTools.ui.utils.loadObjectSel("' + upVectorObjectTFB + '")')

    # Buttons
    snapB = cmds.button('snapToMeshSnapB', l='Snap!', c='glTools.ui.mesh.snapToMeshFromUI(False)')
    snapCloseB = cmds.button('snapToMeshSnapCloseB', l='Snap and Close', c='glTools.ui.mesh.snapToMeshFromUI(True)')
    cancelB = cmds.button('snapToMeshCancelB', l='Cancel', c='cmds.deleteUI("' + window + '")')

    # Form Layout - MAIN
    cmds.formLayout(FL, e=True, af=[(meshTFB, 'top', 5), (meshTFB, 'left', 5), (meshTFB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(orientCBG, 'top', 5, meshTFB)], af=[(orientCBG, 'left', 5), (orientCBG, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(orientFrameL, 'top', 5, orientCBG), (orientFrameL, 'bottom', 5, snapB)],
                  af=[(orientFrameL, 'left', 5), (orientFrameL, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(snapB, 'bottom', 5, snapCloseB)], af=[(snapB, 'left', 5), (snapB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(snapCloseB, 'bottom', 5, cancelB)],
                  af=[(snapCloseB, 'left', 5), (snapCloseB, 'right', 5)])
    cmds.formLayout(FL, e=True, af=[(cancelB, 'left', 5), (cancelB, 'right', 5), (cancelB, 'bottom', 5)])

    # Form Layout - Orient
    cmds.formLayout(orientFormL, e=True,
                  af=[(orientNormAxisOMG, 'top', 5), (orientNormAxisOMG, 'left', 5), (orientNormAxisOMG, 'right', 5)])
    cmds.formLayout(orientFormL, e=True, ac=[(orientUpVecAxisOMG, 'top', 5, orientNormAxisOMG)])
    cmds.formLayout(orientFormL, e=True, af=[(orientUpVecAxisOMG, 'left', 5), (orientUpVecAxisOMG, 'right', 5)])

    cmds.formLayout(orientFormL, e=True, ac=[(upVectorFFG, 'top', 5, orientUpVecAxisOMG)])
    cmds.formLayout(orientFormL, e=True, af=[(upVectorFFG, 'left', 5), (upVectorFFG, 'right', 5)])

    cmds.formLayout(orientFormL, e=True, ac=[(upVectorObjectTFB, 'top', 5, upVectorFFG)])
    cmds.formLayout(orientFormL, e=True, af=[(upVectorObjectTFB, 'left', 5), (upVectorObjectTFB, 'right', 5)])

    # Show Window
    cmds.showWindow(window)


def snapToMeshFromUI(close=False):
    """
    Execute snapToMesh() from UI
    """
    # Window
    window = 'snapToMeshUI'
    if not cmds.window(window, q=True, ex=1): raise UIError('SnapToSurface UI does not exist!!')

    # Get UI data
    mesh = cmds.textFieldGrp('snapToMeshTFB', q=True, text=True)
    if not glTools.utils.mesh.isMesh(mesh):
        raise Exception('Object "' + mesh + '" is not a valid mesh!!')

    # Orient
    orient = cmds.checkBoxGrp('snapToMeshOrientCBG', q=True, v1=True)
    # Orient Options
    normAx = str.lower(str(cmds.optionMenuGrp('snapToMeshNormOMG', q=True, v=True)))
    upVecAx = str.lower(str(cmds.optionMenuGrp('snapToMeshUpVecOMG', q=True, v=True)))
    # Up Vector
    upVec = (
    cmds.floatFieldGrp('snapToMeshUpVecFFG', q=True, v1=True), cmds.floatFieldGrp('snapToMeshUpVecFFG', q=True, v2=True),
    cmds.floatFieldGrp('snapToMeshUpVecFFG', q=True, v3=True))
    upVecObj = cmds.textFieldButtonGrp('snapToMeshUpVecObjTFG', q=True, text=True)

    # Get User Selection
    sel = cmds.ls(sl=True, fl=True)

    # Execute Command
    glTools.utils.mesh.snapPtsToMesh(mesh, sel)
    # Orient
    if orient:
        for obj in sel:
            try:
                glTools.utils.mesh.orientToMesh(mesh=mesh, transform=obj, upVector=upVec, upVectorObject=upVecObj,
                                                normalAxis=normAx, upAxis=upVecAx)
            except:
                raise Exception('Object "' + obj + '" is not a valid transform!! Unable to orient!')

    # Cleanup
    if close: cmds.deleteUI(window)


def snapToClosestVertexUI():
    """
    UI for snapToClosestVertex()
    """
    # Window
    window = 'snapToClosestVtxUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Snap To Closest Vertex')

    # Layout
    FL = cmds.formLayout(numberOfDivisions=100)

    # ===============
    # - UI Elements -
    # ===============

    # Mesh
    meshTFB = cmds.textFieldButtonGrp('snapToMeshVtxTFB', label='Target Mesh', text='', buttonLabel='Load Selected')

    # UI callback commands
    cmds.textFieldButtonGrp(meshTFB, e=True, bc='glTools.ui.utils.loadMeshSel("' + meshTFB + '")')

    # Buttons
    snapB = cmds.button('snapToMeshSnapB', l='Snap To Vertex', c='glTools.ui.mesh.snapToClosestVertexFromUI(False)')
    cancelB = cmds.button('snapToMeshCancelB', l='Cancel', c='cmds.deleteUI("' + window + '")')

    # Form Layout - MAIN
    cmds.formLayout(FL, e=True, af=[(meshTFB, 'top', 5), (meshTFB, 'left', 5), (meshTFB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(snapB, 'bottom', 5, cancelB)], af=[(snapB, 'left', 5), (snapB, 'right', 5)])
    cmds.formLayout(FL, e=True, af=[(cancelB, 'left', 5), (cancelB, 'right', 5), (cancelB, 'bottom', 5)])

    # Show Window
    cmds.showWindow(window)


def snapToClosestVertexFromUI(close=False):
    """
    """
    # Window
    window = 'snapToClosestVtxUI'
    if not cmds.window(window, q=True, ex=1):
        raise UIError('SnapToClosestVertex UI does not exist!!')

    # Get UI data
    mesh = cmds.textFieldGrp('snapToMeshVtxTFB', q=True, text=True)

    for i in cmds.ls(sl=1, fl=1):
        # pt = cmds.pointPosition(i)
        pt = glTools.utils.base.getPosition(i)
        vtx = glTools.utils.mesh.closestVertex(mesh, pt)
        pos = cmds.pointPosition(mesh + '.vtx[' + str(vtx) + ']')
        cmds.move(pos[0], pos[1], pos[2], i, ws=True, a=True)


def attachToMeshUI():
    """
    UI for attachToMesh()
    """
    # Window
    window = 'attachToMeshUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Attach To Mesh')
    # Layout
    FL = cmds.formLayout(numberOfDivisions=100)
    # UI Elements
    # ---
    # Surface
    meshTFB = cmds.textFieldButtonGrp('attachToMeshTFB', label='Target Mesh', text='', buttonLabel='Load Selected')
    # Transform
    transformTFB = cmds.textFieldButtonGrp('attachToMeshTransformTFB', label='Transform', text='',
                                         buttonLabel='Load Selected')
    # Transform
    prefixTFG = cmds.textFieldGrp('attachToMeshPrefixTFG', label='Prefix', text='')
    # Orient
    orientCBG = cmds.checkBoxGrp('attachToMeshOrientCBG', label='Orient To Face', ncb=1, v1=False)

    # Orient Frame
    orientFrameL = cmds.frameLayout('attachToMeshOriFL', l='Orient Options', cll=0, en=0)
    orientFormL = cmds.formLayout(numberOfDivisions=100)
    # OMG
    axList = ['X', 'Y', 'Z', '-X', '-Y', '-Z']
    orientNormAxisOMG = cmds.optionMenuGrp('attachToMeshNormOMG', label='Normal Axis', en=False)
    for ax in axList: cmds.menuItem(label=ax)
    orientTanAxisOMG = cmds.optionMenuGrp('attachToMeshTanOMG', label='Tangent Axis', en=False)
    for ax in axList: cmds.menuItem(label=ax)
    # Set Default Value
    cmds.optionMenuGrp(orientTanAxisOMG, e=True, sl=2)

    cmds.setParent('..')
    cmds.setParent('..')

    # UI callback commands
    cmds.textFieldButtonGrp(meshTFB, e=True, bc='glTools.ui.utils.loadMeshSel("' + meshTFB + '")')
    cmds.textFieldButtonGrp(transformTFB, e=True,
                          bc='glTools.ui.utils.loadObjectSel("' + transformTFB + '","' + prefixTFG + '")')
    cmds.checkBoxGrp(orientCBG, e=True,
                   cc='glTools.ui.utils.checkBoxToggleLayout("' + orientCBG + '","' + orientFrameL + '")')

    # Buttons
    snapB = cmds.button('attachToMeshAttachB', l='Attach', c='glTools.ui.mesh.attachToMeshFromUI(False)')
    snapCloseB = cmds.button('attachToMeshAttachCloseB', l='Attach and Close',
                           c='glTools.ui.mesh.attachToMeshFromUI(True)')
    cancelB = cmds.button('attachToMeshCancelB', l='Cancel', c='cmds.deleteUI("' + window + '")')

    # Form Layout - MAIN
    cmds.formLayout(FL, e=True, af=[(meshTFB, 'top', 5), (meshTFB, 'left', 5), (meshTFB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(transformTFB, 'top', 5, meshTFB)])
    cmds.formLayout(FL, e=True, af=[(transformTFB, 'left', 5), (transformTFB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(prefixTFG, 'top', 5, transformTFB)])
    cmds.formLayout(FL, e=True, af=[(prefixTFG, 'left', 5), (prefixTFG, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(orientCBG, 'top', 5, prefixTFG)])
    cmds.formLayout(FL, e=True, af=[(orientCBG, 'left', 5), (orientCBG, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(orientFrameL, 'top', 5, orientCBG)])
    cmds.formLayout(FL, e=True, af=[(orientFrameL, 'left', 5), (orientFrameL, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(orientFrameL, 'bottom', 5, snapB)])
    cmds.formLayout(FL, e=True, ac=[(snapB, 'bottom', 5, snapCloseB)])
    cmds.formLayout(FL, e=True, af=[(snapB, 'left', 5), (snapB, 'right', 5)])
    cmds.formLayout(FL, e=True, ac=[(snapCloseB, 'bottom', 5, cancelB)])
    cmds.formLayout(FL, e=True, af=[(snapCloseB, 'left', 5), (snapCloseB, 'right', 5)])
    cmds.formLayout(FL, e=True, af=[(cancelB, 'left', 5), (cancelB, 'right', 5), (cancelB, 'bottom', 5)])

    # Form Layout - Orient
    cmds.formLayout(orientFormL, e=True,
                  af=[(orientNormAxisOMG, 'top', 5), (orientNormAxisOMG, 'left', 5), (orientNormAxisOMG, 'right', 5)])
    cmds.formLayout(orientFormL, e=True, ac=[(orientTanAxisOMG, 'top', 5, orientNormAxisOMG)])
    cmds.formLayout(orientFormL, e=True, af=[(orientTanAxisOMG, 'left', 5), (orientTanAxisOMG, 'right', 5)])

    # Show Window
    cmds.showWindow(window)


def attachToMeshFromUI(close=False):
    """
    Execute attachToMesh() from UI
    """
    # Window
    window = 'attachToMeshUI'
    if not cmds.window(window, q=True, ex=1): raise UIError('SnapToSurface UI does not exist!!')
    # Get UI data
    mesh = cmds.textFieldGrp('attachToMeshTFB', q=True, text=True)
    # Check surface
    if not glTools.utils.mesh.isMesh(mesh):
        raise Exception('Object "' + surface + '" is not a valid nurbs surface!!')
    # Transform
    obj = cmds.textFieldGrp('attachToMeshTransformTFB', q=True, text=True)
    # Prefix
    pre = cmds.textFieldGrp('attachToMeshPrefixTFG', q=True, text=True)
    # Orient
    orient = cmds.checkBoxGrp('attachToMeshOrientCBG', q=True, v1=True)
    # Orient Options
    normAx = str.lower(str(cmds.optionMenuGrp('attachToMeshNormOMG', q=True, v=True)))
    tanAx = str.lower(str(cmds.optionMenuGrp('attachToMeshTanOMG', q=True, v=True)))

    # Execute command
    glTools.utils.attach.attachToMesh(mesh=mesh, transform=obj, useClosestPoint=True, orient=orient, normAxis=normAx,
                                      tangentAxis=tanAx, prefix=pre)

    # Cleanup
    if close: cmds.deleteUI(window)
