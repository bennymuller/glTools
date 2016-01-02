import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import glTools.utils.matrix
import glTools.utils.mathUtils


class UserInputError(Exception):
    pass


def faceForward(transform, aimAxis='z', upAxis='y', upVector=(0, 1, 0), upVectorType='vector', upVectorObject='',
                previousFrameVelocity=False, key=False):
    """
    Rotate the specified transform towards the direction of its movement.
    @param transform: The transform to face forward
    @type transform: str
    @param aimAxis: The axis of the transform to aim forward
    @type aimAxis: str
    @param upAxis: The axis of the transform to aim towards the upVector
    @type upAxis: str
    @param upVector: The axis of the transform to aim towards the upVector
    @type upVector: tuple or list
    @param upVectorType: The method used to calculate the upVector
    @type upVectorType: str
    @param upVectorObject: The object to derive the upVector from
    @type upVectorObject: str
    @param previousFrameVelocity: Use the velocity of the previous frame instead of the current frame
    @type previousFrameVelocity: bool
    @param key: Set a key for the rotation attributes
    @type key: bool
    """
    # Check transform
    if not cmds.objExists(transform):
        raise UserInputError('Object "' + transform + '" does not exist!!')
    # Check upVectorObject
    if upVectorType == 'object' and not cmds.objExists(upVectorObject):
        raise UserInputError('UpVector object "' + upVectorObject + '" does not exist!!')

    # Get Rotate Values
    rotate = faceForwardRotation(transform, aimAxis, upAxis, upVector, upVectorType, upVectorObject,
                                 previousFrameVelocity)
    # Set Rotate Values
    cmds.setAttr(transform + '.rotate', rotate[0], rotate[1], rotate[2])
    # Set Rotate Keys
    if key:
        cmds.setKeyframe(transform + '.rotateX', rotate[0])
        cmds.setKeyframe(transform + '.rotateY', rotate[1])
        cmds.setKeyframe(transform + '.rotateZ', rotate[2])


def faceForwardRotation(transform, aimAxis='z', upAxis='y', upVector=(0, 1, 0), upVectorType='vector',
                        upVectorObject='', previousFrameVelocity=False, time=None):
    """
    Get the rotation values required for the specified transform so that a given axis is aimed in the direction of its movement
    @param transform: The transform to face forward
    @type transform: str
    @param aimAxis: The axis of the transform to aim forward
    @type aimAxis: str
    @param upAxis: The axis of the transform to aim towards the upVector
    @type upAxis: str
    @param upVector: The axis of the transform to aim towards the upVector
    @type upVector: tuple or list
    @param upVectorType: The method used to calculate the upVector
    @type upVectorType: str
    @param upVectorObject: The object to derive the upVector from
    @type upVectorObject: str
    @param previousFrameVelocity: Use the velocity of the previous frame instead of the current frame
    @type previousFrameVelocity: bool
    @param time: The frame to calculate the face forward rotation for. If left at default, will use the current frame.
    @type time: int or float
    """
    # Check transform
    if not cmds.objExists(transform):
        raise UserInputError('Object "' + transform + '" does not exist!!')
    # Check upVectorObject
    if upVectorType == 'object' and not cmds.objExists(upVectorObject):
        raise UserInputError('UpVector object "' + upVectorObject + '" does not exist!!')

    # Get transform parent
    parent = ''
    parentList = cmds.listRelatives(transform, p=True, pa=True)
    if parentList: parent = parentList[0]

    # Get frame
    frame = cmds.currentTime(q=True)
    if time != None: frame = time

    # Get transform matrices for current frame
    tMatrix = glTools.utils.matrix.getMatrix(transform=transform, time=frame)
    pMatrix = OpenMaya.MMatrix.identity
    if parent: pMatrix = glTools.utils.matrix.getMatrix(transform=parent, time=frame)

    # Get position for current frame
    tx = cmds.getAttr(transform + '.tx', t=frame)
    ty = cmds.getAttr(transform + '.ty', t=frame)
    tz = cmds.getAttr(transform + '.tz', t=frame)
    cPos = OpenMaya.MPoint(tx, ty, tz, 1.0)

    # Get position for next frame
    tx = cmds.getAttr(transform + '.tx', t=frame + 1)
    ty = cmds.getAttr(transform + '.ty', t=frame + 1)
    tz = cmds.getAttr(transform + '.tz', t=frame + 1)
    nPos = OpenMaya.MPoint(tx, ty, tz, 1.0)

    # Get aimVector
    aimVector = (0, 0, 0)
    # Check forward velocity
    velocity = nPos - cPos
    # Check backward velocity
    if not velocity.length() or previousFrameVelocity:
        tx = cmds.getAttr(transform + '.tx', t=frame - 1)
        ty = cmds.getAttr(transform + '.ty', t=frame - 1)
        tz = cmds.getAttr(transform + '.tz', t=frame - 1)
        nPos = OpenMaya.MPoint(tx, ty, tz, 1.0)
        pVelocity = cPos - nPos
        if pVelocity.length(): velocity = pVelocity
    # Check velocity length
    if velocity.length():
        aimVec = velocity.normal()
        aimVector = (aimVec.x, aimVec.y, aimVec.z)
    else:
        return cmds.getAttr(transform + '.rotate')[0]

    # Get upVector
    if upVectorType == 'current':
        upVec = OpenMaya.MVector(upVector[0], upVector[1], upVector[2]) * tMatrix
        upVector = (upVec.x, upVec.y, upVec.z)
    elif upVectorType == 'object':
        tPos = cmds.xform(transform, q=True, ws=True, rp=True)
        uPos = cmds.xform(upVectorObject, q=True, ws=True, rp=True)
        upVector = glTools.utils.mathUtils.offsetVector(tPos, uPos)
    elif upVectorType == 'objectUp':
        upMatrix = glTools.utils.matrix.getMatrix(transform=transform, time=f)
        upVec = OpenMaya.MVector(upVector[0], upVector[1], upVector[2]) * upMatrix
        upVector = (upVec.x, upVec.y, upVec.z)
    elif upVectorType == 'vector':
        pass

    # Build Rotation Matrix
    rMatrix = glTools.utils.matrix.buildRotation(aimVector, upVector, aimAxis, upAxis)
    if parent: rMatrix *= pMatrix.inverse()
    rotate = glTools.utils.matrix.getRotation(rMatrix, cmds.getAttr(transform + '.ro'))

    # Return result
    return rotate


def faceForwardAnim(transform, aimAxis='z', upAxis='y', upVector=(0, 1, 0), upVectorType='vector', upVectorObject='',
                    previousFrameVelocity=False, frameStart=-1, frameEnd=-1, sampleByFrame=0):
    """
    Key the rotation attributes of the specified transform so that a set axis is always
    aimed in the direction of its movement
    @param transform: The transform to face forward
    @type transform: str
    @param aimAxis: The axis of the transform to aim forward
    @type aimAxis: str
    @param upAxis: The axis of the transform to aim towards the upVector
    @type upAxis: str
    @param upVector: The axis of the transform to aim towards the upVector
    @type upVector: tuple or list
    @param upVectorType: The method used to calculate the upVector
    @type upVectorType: str
    @param upVectorObject: The object to derive the upVector from
    @type upVectorObject: str
    @param previousFrameVelocity: Use the velocity of the previous frame instead of the current frame
    @type previousFrameVelocity: bool
    @param frameStart: The first frame to calculate the face forward rotation for. If left at default, will use first frame in the timeline.
    @type frameStart: int
    @param frameEnd: The last frame to calculate the face forward rotation for. If left at default, will use last frame in the timeline.
    @type frameEnd: int
    @param sampleByFrame: How often to sample the face forward rotation. If left at default, will sample at every translate keyframe.
    @type sampleByFrame: int
    """
    # Check transform
    if not cmds.objExists(transform):
        raise UserInputError('Object "' + transform + '" does not exist!!')
    # Check upVectorObject
    if upVectorType == 'object' and not cmds.objExists(upVectorObject):
        raise UserInputError('UpVector object "' + upVectorObject + '" does not exist!!')

    # Get transform parent
    parent = ''
    parentList = cmds.listRelatives(transform, p=True, pa=True)
    if parentList: parent = parentList[0]

    # Get sample frames
    sFrames = []
    if frameStart < 0: frameStart = OpenMayaAnim.MAnicmdsontrol().minTime().value()
    if frameEnd < 0: frameEnd = OpenMayaAnim.MAnicmdsontrol().maxTime().value()
    if sampleByFrame:
        sFrames = range(frameStart, frameEnd + 1, sampleByFrame)
    else:
        tAnicmdsurve = cmds.listConnections([transform + '.tx', transform + '.ty', transform + '.tz'], s=True, d=True,
                                        type='anicmdsurve')
        if not tAnicmdsurve: raise UserInputError(
            'Object "' + transform + '" has no translate keys! Set sampleByFrame argument greater than zero!')
        [sFrames.append(i) for i in cmds.keyframe(tAnicmdsurve, q=True, tc=True, t=(frameStart, frameEnd)) if
         not sFrames.count(i)]

    # Sample frames
    for f in sFrames:
        # Get rotation values
        rotate = faceForwardRotation(transform, aimAxis, upAxis, upVector, upVectorType, upVectorObject,
                                     previousFrameVelocity, f)
        print rotate
        # Set rotation key
        cmds.setAttr(transform + '.rotateX', rotate[0])
        cmds.setKeyframe(transform, at='rotateX', t=f, v=rotate[0])
        cmds.setAttr(transform + '.rotateY', rotate[1])
        cmds.setKeyframe(transform, at='rotateY', t=f, v=rotate[1])
        cmds.setAttr(transform + '.rotateZ', rotate[2])
        cmds.setKeyframe(transform, at='rotateZ', t=f, v=rotate[2])

    # Filter Curves
    cmds.filterCurve([transform + '.rotateX', transform + '.rotateY', transform + '.rotateZ'])
