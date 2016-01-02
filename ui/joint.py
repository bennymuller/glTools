import maya.cmds as cmds
import glTools.utils.joint
import glTools.utils.mathUtils
import glTools.utils.stringUtils


class UserInputError(Exception): pass


class UIError(Exception): pass


def jointOrientUI():
    """
    UI for jointOrient()
    """
    # Window
    window = 'jointOrientUI'
    if cmds.window(window, q=True, ex=1): cmds.deleteUI(window)
    window = cmds.window(window, t='Joint Orient Tool')

    # UI Elements
    # ---
    width = 272
    height = 459
    cw1 = 90
    cw2 = 60
    cw3 = 60
    cw4 = 50

    # Layout
    CL = cmds.columnLayout(w=width, adj=True)

    # Aim Method
    aimRBG = cmds.radioButtonGrp('jointOrientAimRBG', nrb=3, l='Aim Method', la3=['Axis', 'Object', 'Cross'], sl=1,
                               cc='glTools.ui.joint.jointOrientRefreshUI_aimMethod()',
                               cw=[(1, cw1), (2, cw2), (3, cw3)])

    # Aim Axis Direction Layout
    axisFL = cmds.frameLayout('jointOrientAxisFL', l='Orientation Axis', w=(width - 8), h=90, cll=0)
    axisCL = cmds.columnLayout(adj=True)

    primAxisPosRBG = cmds.radioButtonGrp('jointOrientPrimAxisRBG', nrb=3, l='Primary Axis', la3=['X', 'Y', 'Z'], sl=1,
                                       cc='glTools.ui.joint.jointOrientRefreshUI_aimAxis()',
                                       cw=[(1, cw1), (2, cw2), (3, cw3), (4, cw4)])
    primAxisNegRBG = cmds.radioButtonGrp('jointOrientPrimAxisNegRBG', nrb=3, scl=primAxisPosRBG, l='',
                                       la3=['-X', '-Y', '-Z'], cc='glTools.ui.joint.jointOrientRefreshUI_aimAxis()',
                                       cw=[(1, cw1), (2, cw2), (3, cw3), (4, cw4)])
    aimAxisRBG = cmds.radioButtonGrp('jointOrientAimAxisRBG', nrb=2, l='Aim Axis', la2=['Y', 'Z'], sl=1,
                                   cw=[(1, cw1), (2, cw2)])

    cmds.setParent('..')
    cmds.setParent('..')

    # Aim Axis Direction Layout
    aimAxisFL = cmds.frameLayout('jointOrientAimAxisFL', l='Orientation Aim Axis', w=(width - 8), h=70, cll=0)
    aimAxisCL = cmds.columnLayout(adj=True)

    oriAxisPosRBG = cmds.radioButtonGrp('jointOrientOriAxisPosRBG', nrb=3, l='Aim Direction', la3=['+X', '+Y', '+Z'],
                                      sl=1, cw=[(1, cw1), (2, cw2), (3, cw3), (4, cw4)])
    oriAxisNegRBG = cmds.radioButtonGrp('jointOrientOriAxisNegRBG', nrb=3, scl=oriAxisPosRBG, l='',
                                      la3=['-X', '-Y', '-Z'], cw=[(1, cw1), (2, cw2), (3, cw3), (4, cw4)])

    cmds.setParent('..')
    cmds.setParent('..')

    # Aim Object Layout
    aimObjFL = cmds.frameLayout('jointOrientAimObjFL', l='Aim Object', w=(width - 8), h=55, cll=0)
    aimObjCL = cmds.columnLayout(adj=True)
    aimObjCreateB = cmds.button(l='Create Aim Object', w=(width - 12), c='glTools.ui.joint.jointOrientCreateControl()')

    cmds.setParent('..')
    cmds.setParent('..')

    # Cross Product Layout
    crossProdFL = cmds.frameLayout('jointOrientCrossProdFL', l='Cross Product', w=(width - 8), h=70, cll=0)
    crossProdCL = cmds.columnLayout(adj=True)
    crossProdCBG = cmds.checkBoxGrp('jointOrientCrossProdCBG', l='Invert Result', ncb=1, cw=[(1, cw1), (2, cw2)])
    crossProdRBG = cmds.radioButtonGrp('jointOrientCrossProdRBG', l='Joint As', nrb=3, la3=['Base', 'Apex', 'Tip'], sl=2,
                                     cw=[(1, cw1), (2, cw2), (3, cw3), (4, cw4)])

    cmds.setParent('..')
    cmds.setParent('..')

    # Rotate Joint Orientation
    # rotJointOriFL = cmds.frameLayout('jointOrientRotOriFL',l='Rotate Joint Orientation',w=(width-8),h=55,cll=0)
    rotJointOriFL = cmds.frameLayout('jointOrientRotOriFL', l='Rotate Joint Orientation', cll=0)
    rotJointOriRCL = cmds.rowColumnLayout(nr=3)
    cmds.text(l=' X - ')
    cmds.text(l=' Y - ')
    cmds.text(l=' Z - ')
    cmds.button(w=80, l='-90', c='glTools.ui.joint.jointOrientRotateOrient(-90,0,0)')
    cmds.button(w=80, l='-90', c='glTools.ui.joint.jointOrientRotateOrient(0,-90,0)')
    cmds.button(w=80, l='-90', c='glTools.ui.joint.jointOrientRotateOrient(0,0,-90)')
    cmds.button(w=80, l='180', c='glTools.ui.joint.jointOrientRotateOrient(180,0,0)')
    cmds.button(w=80, l='180', c='glTools.ui.joint.jointOrientRotateOrient(0,180,0)')
    cmds.button(w=80, l='180', c='glTools.ui.joint.jointOrientRotateOrient(0,0,180)')
    cmds.button(w=80, l='+90', c='glTools.ui.joint.jointOrientRotateOrient(90,0,0)')
    cmds.button(w=80, l='+90', c='glTools.ui.joint.jointOrientRotateOrient(0,90,0)')
    cmds.button(w=80, l='+90', c='glTools.ui.joint.jointOrientRotateOrient(0,0,90)')

    cmds.setParent('..')
    cmds.setParent('..')

    # Toggle Axis View
    cmds.button(l='Toggle Local Axis Display', w=(width - 8), c='cmds.toggle(localAxis=True)')
    # Orient Joint
    cmds.button(l='Orient Joint', w=(width - 8), c='glTools.ui.joint.jointOrientFromUI()')
    # Close UI
    cmds.button(l='Close', c='cmds.deleteUI("' + window + '")')

    # Prepare Window
    cmds.window(window, e=True, w=width, h=height)
    cmds.frameLayout(aimObjFL, e=True, en=False)
    cmds.frameLayout(crossProdFL, e=True, en=False)

    # Show Window
    cmds.showWindow(window)


def jointOrientFromUI(close=False):
    """
    Execute jointOrient() from UI
    """
    # Window
    window = 'jointOrientUI'
    if not cmds.window(window, q=True, ex=1): raise UIError('JointOrient UI does not exist!!')

    # Build Axis List
    axisList = ['x', 'y', 'z', '-x', '-y', '-z']

    # Build UpAxis List
    upAxisList = [('y', 'z'), ('x', 'z'), ('x', 'y')]

    # Build Axis Dictionary
    axisDict = {'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1), '-x': (-1, 0, 0), '-y': (0, -1, 0), '-z': (0, 0, -1)}

    # Get joint selection
    jntList = cmds.ls(sl=True, type='joint')
    if not jntList: return

    # Aim Method
    aimMethod = cmds.radioButtonGrp('jointOrientAimRBG', q=True, sl=True)

    # Get Axis Selection
    aimAx = cmds.radioButtonGrp('jointOrientPrimAxisRBG', q=True, sl=True)
    upAx = cmds.radioButtonGrp('jointOrientAimAxisRBG', q=True, sl=True)
    # Build Axis Values
    aimAxis = axisList[aimAx - 1]
    upAxis = upAxisList[aimAx - 1][upAx - 1]

    # Axis
    upVector = (0, 1, 0)
    if aimMethod == 1:

        # Check joint selection
        if not jntList: raise UserInputError('Invalid joint selection!!')
        # Get UpVector Selection
        upVec = cmds.radioButtonGrp('jointOrientOriAxisPosRBG', q=True, sl=True)
        if not upVec: upVec = cmds.radioButtonGrp('jointOrientOriAxisNegRBG', q=True, sl=True) + 3
        # Build UpAxis Value
        upVector = axisDict[axisList[upVec - 1]]

        # Execute Command
        for jnt in jntList:
            glTools.utils.joint.orient(jnt, aimAxis=aimAxis, upAxis=upAxis, upVec=upVector)

    # Object
    elif aimMethod == 2:

        # Check for orient control selection
        cccList = cmds.ls('*_ori01_orientControl', sl=True)
        for ccc in cccList:
            if cmds.objExists(ccc + '.joint'):
                cJnt = cmds.listConnections(ccc + '.joint', s=True, d=False, type='joint')
                if not cJnt: continue
                if not jntList.count(cJnt[0]): jntList.append(cJnt[0])

        # Determine orient control
        for jnt in jntList:
            prefix = glTools.utils.stringUtils.stripSuffix(jnt)
            ctrlGrp = prefix + '_ori01_orientGrp'
            oriCtrl = prefix + '_ori01_orientControl'
            upLoc = prefix + '_up01_orientLoc'
            if (not cmds.objExists(ctrlGrp)) or (not cmds.objExists(oriCtrl)) or (not cmds.objExists(upLoc)):
                print('Joint "' + jnt + '" has no orient control!! Unable to orient joint!!')
                continue
            # Extract upVector from orient control
            jPos = cmds.xform(jnt, q=True, ws=True, rp=True)
            upPos = cmds.xform(upLoc, q=True, ws=True, rp=True)
            upVector = glTools.utils.mathUtils.offsetVector(upPos, jPos)

            # Execute Command
            glTools.utils.joint.orient(jnt, aimAxis=aimAxis, upAxis=upAxis, upVec=upVector)

            # Delete orient control
            cmds.delete(ctrlGrp)

    # Cross
    elif aimMethod == 3:

        # Invert
        invert = cmds.checkBoxGrp('jointOrientCrossProdCBG', q=True, v1=True)
        # Joint As
        jointAs = cmds.radioButtonGrp('jointOrientCrossProdRBG', q=True, sl=True)

        # Get Cross vector
        for jnt in jntList:

            # Check for child joint
            if not cmds.listRelatives(jnt, c=True):
                glTools.utils.joint.orient(jnt)
                continue
            if jointAs == 1:  # BASE
                bJnt = jnt
                aJnt = cmds.listRelatives(jnt, c=True, pa=True, type='joint')
                if not aJnt: raise UserInputError(
                    'Insufficient joint connectivity to determine apex from base "' + jnt + '"!!')
                aJnt = aJnt[0]
                tJnt = cmds.listRelatives(aJnt, c=True, pa=True, type='joint')
                if not tJnt: raise UserInputError(
                    'Insufficient joint connectivity to determine tip from apex "' + aJnt + '"!!')
                tJnt = tJnt[0]
            elif jointAs == 2:  # APEX
                bJnt = cmds.listRelatives(jnt, c=True, pa=True, type='joint')
                if not bJnt: raise UserInputError(
                    'Insufficient joint connectivity to determine base from base "' + jnt + '"!!')
                bJnt = bJnt[0]
                aJnt = jnt
                tJnt = cmds.listRelatives(jnt, p=True, pa=True, type='joint')
                if not tJnt: raise UserInputError(
                    'Insufficient joint connectivity to determine tip from apex "' + jnt + '"!!')
                tJnt = tJnt[0]
            elif jointAs == 3:  # TIP
                tJnt = jnt
                aJnt = cmds.listRelatives(jnt, p=True, pa=True, type='joint')
                if not tJnt: raise UserInputError(
                    'Insufficient joint connectivity to determine apex from tip "' + jnt + '"!!')
                aJnt = aJnt[0]
                bJnt = cmds.listRelatives(aJnt, p=True, pa=True, type='joint')
                if not bJnt: raise UserInputError(
                    'Insufficient joint connectivity to determine base from apex "' + aJnt + '"!!')
                bJnt = bJnt[0]

            # Get joint positions
            bPos = cmds.xform(bJnt, q=True, ws=True, rp=True)
            aPos = cmds.xform(aJnt, q=True, ws=True, rp=True)
            tPos = cmds.xform(tJnt, q=True, ws=True, rp=True)
            # Calculate cross product
            vec1 = glTools.utils.mathUtils.offsetVector(aPos, bPos)
            vec2 = glTools.utils.mathUtils.offsetVector(tPos, aPos)
            cross = glTools.utils.mathUtils.crossProduct(vec1, vec2)
            # Invert
            if invert: cross = (-cross[0], -cross[1], -cross[2])

            # Execute Command
            glTools.utils.joint.orient(jnt, aimAxis=aimAxis, upAxis=upAxis, upVec=cross)

    # Select Joint Children
    cmds.select(cmds.listRelatives(jntList, c=True, type='joint'))

    # Cleanup
    if close: cmds.deleteUI(window)


def jointOrientRefreshUI_aimMethod():
    """
    Refresh Aim Axis list based on Primary Axis selection.
    """
    aimMethod = cmds.radioButtonGrp('jointOrientAimRBG', q=True, sl=True)
    cmds.frameLayout('jointOrientAimAxisFL', e=True, en=(aimMethod == 1))
    cmds.frameLayout('jointOrientAimObjFL', e=True, en=(aimMethod == 2))
    cmds.frameLayout('jointOrientCrossProdFL', e=True, en=(aimMethod == 3))


def jointOrientRefreshUI_aimAxis():
    """
    Refresh Aim Axis list based on Primary Axis selection.
    """
    # Get Orient Axis Label Index
    labelIndex = cmds.radioButtonGrp('jointOrientPrimAxisRBG', q=True, sl=True)
    if not labelIndex: labelIndex = cmds.radioButtonGrp('jointOrientPrimAxisNegRBG', q=True, sl=True) + 3
    labelArray = [('Y', 'Z'), ('X', 'Z'), ('X', 'Y')] * 2
    cmds.radioButtonGrp('jointOrientAimAxisRBG', e=True, la2=labelArray[labelIndex - 1])


def jointOrientRotateOrient(rx, ry, rz):
    """
    Incremental joint orient rotation for selected joints
    @param rx: Joint orient rotation around the X axis
    @type rx: float
    @param ry: Joint orient rotation around the Y axis
    @type ry: float
    @param rz: Joint orient rotation around the Z axis
    @type rz: float
    """
    jntList = cmds.ls(sl=True, type='joint')
    for jnt in jntList:
        childList = cmds.parent(cmds.listRelatives(jnt, c=True, pa=True), w=True)
        jOri = cmds.getAttr(jnt + '.jo')[0]
        cmds.setAttr(jnt + '.jo', jOri[0] + rx, jOri[1] + ry, jOri[2] + rz)
        cmds.parent(childList, jnt)
    cmds.select(jntList)


def jointOrientCreateControl():
    """
    Create joint orient control for each selected joint
    """
    # Check Window
    window = 'jointOrientUI'
    upAxis = (0, 1, 0)
    if cmds.window(window, q=True, ex=1):
        # Build UpAxis List
        upAxisList = [((0, 1, 0), (0, 0, 1)), ((1, 0, 0), (0, 0, 1)), ((1, 0, 0), (0, 1, 0))]
        # Get Axis Selection
        aimAx = cmds.radioButtonGrp('jointOrientPrimAxisRBG', q=True, sl=True)
        upAx = cmds.radioButtonGrp('jointOrientAimAxisRBG', q=True, sl=True)
        # Build Axis Values
        upAxis = upAxisList[aimAx - 1][upAx - 1]

    # Create control
    jntList = cmds.ls(sl=True, type='joint')
    ctrlList = []
    for jnt in jntList:

        # Get child joint
        cJnt = cmds.listRelatives(jnt, c=True, pa=True)
        if not cJnt: continue

        # Generate control prefix
        prefix = glTools.utils.stringUtils.stripSuffix(jnt)

        # Check for existing orien control
        if cmds.objExists(prefix + '_ori01_orientGrp'):
            print('Orient control already exists for joint "' + jnt + '"!!')
            continue

        # Create orient control
        circle = cmds.circle(c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=1, d=3, ut=0, tol=0.01, s=8, ch=1,
                           n=prefix + '_ori01_orientControl')
        for ch in ['tx', 'ty', 'tz', 'rx', 'rz', 'sx', 'sy', 'sz']: cmds.setAttr(circle[0] + '.' + ch, l=True, k=False)

        # Create orient UP locator
        upLoc = cmds.spaceLocator(n=prefix + '_up01_orientLoc')
        cmds.parent(upLoc[0], circle[0])
        cmds.setAttr(upLoc[0] + '.tz', 1.0)
        cmds.connectAttr(upLoc[0] + '.tz', circle[1] + '.radius', f=True)
        for ch in ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']: cmds.setAttr(upLoc[0] + '.' + ch, l=True, k=False)

        # Create orient control group
        ctrlGrp = cmds.group(em=True, n=prefix + '_ori01_orientGrp')
        cmds.parent(circle[0], ctrlGrp)

        # Position control group
        cmds.delete(cmds.pointConstraint(jnt, ctrlGrp))
        cmds.delete(cmds.aicmdsonstraint(cJnt[0], ctrlGrp, aimVector=(0, 1, 0), upVector=(0, 0, 1), wu=upAxis, wuo=jnt,
                                   wut='objectrotation'))

        # Scale control elements
        dist = glTools.utils.mathUtils.distanceBetween(cmds.xform(jnt, q=True, ws=True, rp=True),
                                                       cmds.xform(cJnt[0], q=True, ws=True, rp=True))
        cmds.setAttr(upLoc[0] + '.tz', dist * 0.5)

        # Lock orient control group
        cmds.parent(ctrlGrp, jnt)
        for ch in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']: cmds.setAttr(ctrlGrp + '.' + ch, l=True,
                                                                                     k=False)

        # Add message connection form joint to orient control
        cmds.addAttr(circle[0], ln='joint', at='message')
        cmds.connectAttr(jnt + '.message', circle[0] + '.joint', f=True)

        # Append control list
        ctrlList.append(circle[0])

    # Select controls
    cmds.select(ctrlList)
