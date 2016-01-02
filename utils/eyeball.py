import maya.cmds as cmds
import maya.mel as mel


class UserInputError(Exception): pass


def create(piv=[0, 0, 0], axis=[0, 0, -1], rad=1, dilate_ctrl='', prefix='eyeball'):
    # ------------------------
    # Generate Profile Curve

    # sphere
    eye_sphere = cmds.sphere(p=piv, ax=axis, r=rad, n=prefix + '_history')
    # curve from sphere
    eye_crv = cmds.duplicateCurve(eye_sphere[0] + '.v[0]')
    eye_crv[0] = cmds.rename(eye_crv[0], prefix + '_pfl01_crv')
    # rebuild curve 0-1
    cmds.rebuildCurve(eye_crv[0], rpo=1, end=1, kcp=1, kr=0, d=3, tol=0.01)

    # ------------------------
    # Extract Curve Segments

    # detach curve
    eye_crv_detach = cmds.detachCurve(eye_crv[0] + '.u[0.125]', eye_crv[0] + '.u[0.25]', rpo=0, ch=1)
    eye_crv_detach[0] = cmds.rename(eye_crv_detach[0], prefix + '_pl01_crv')
    eye_crv_detach[1] = cmds.rename(eye_crv_detach[1], prefix + '_ir01_crv')
    eye_crv_detach[2] = cmds.rename(eye_crv_detach[2], prefix + '_sc01_crv')
    eye_crv_detach[3] = cmds.rename(eye_crv_detach[3], prefix + '_cr01_dtc')
    # rebuild curve segments
    pupil_rebuild = cmds.rebuildCurve(eye_crv_detach[0], rpo=1, end=1, kep=1, kt=1, kr=0, s=2, d=3, tol=0.01)
    iris_rebuild = cmds.rebuildCurve(eye_crv_detach[1], rpo=1, end=1, kep=1, kt=1, kr=0, s=2, d=3, tol=0.01)
    sclera_rebuild = cmds.rebuildCurve(eye_crv_detach[2], rpo=1, end=1, kep=1, kt=1, kr=0, s=4, d=3, tol=0.01)
    pupil_rebuild[1] = cmds.rename(pupil_rebuild[1], prefix + '_pl01_rbc')
    iris_rebuild[1] = cmds.rename(iris_rebuild[1], prefix + '_ir01_rbc')
    sclera_rebuild[1] = cmds.rename(sclera_rebuild[1], prefix + '_sc01_rbc')

    # ------------------------
    # Generate Eye Surfaces

    # revolve
    pupil_revolve = cmds.revolve(eye_crv_detach[0], po=0, rn=0, ut=0, tol=0.01, degree=3, s=8, ulp=1, ax=[0, 0, 1])
    iris_revolve = cmds.revolve(eye_crv_detach[1], po=0, rn=0, ut=0, tol=0.01, degree=3, s=8, ulp=1, ax=[0, 0, 1])
    sclera_revolve = cmds.revolve(eye_crv_detach[2], po=0, rn=0, ut=0, tol=0.01, degree=3, s=8, ulp=1, ax=[0, 0, 1])
    # rename surfaces
    pupil_revolve[0] = cmds.rename(pupil_revolve[0], prefix + '_pl01_srf')
    pupil_revolve[1] = cmds.rename(pupil_revolve[1], prefix + '_pl01_rvl')
    iris_revolve[0] = cmds.rename(iris_revolve[0], prefix + '_ir01_srf')
    iris_revolve[1] = cmds.rename(iris_revolve[1], prefix + '_ir01_rvl')
    sclera_revolve[0] = cmds.rename(sclera_revolve[0], prefix + '_sc01_srf')
    sclera_revolve[1] = cmds.rename(sclera_revolve[1], prefix + '_sc01_rvl')
    # Connect Revolve Pivot
    cmds.connectAttr(eye_sphere[0] + '.t', pupil_revolve[1] + '.pivot', f=1)
    cmds.connectAttr(eye_sphere[0] + '.t', iris_revolve[1] + '.pivot', f=1)
    cmds.connectAttr(eye_sphere[0] + '.t', sclera_revolve[1] + '.pivot', f=1)

    # ------------------------
    # Connect Dilate Control

    if len(dilate_ctrl):

        # Verify Control
        if not cmds.objExists(dilate_ctrl):
            raise UserInputError('Object ' + dilate_ctrl + ' does not exist!')

        # Check Attributes Exist
        if not cmds.objExists(dilate_ctrl + '.iris'):
            cmds.addAttr(dilate_ctrl, ln='iris', min=0, max=4, dv=1)
            cmds.setAttr(dilate_ctrl + '.iris', k=1)
        if not cmds.objExists(dilate_ctrl + '.pupil'):
            cmds.addAttr(dilate_ctrl, ln='pupil', min=0, max=1, dv=0.5)
            cmds.setAttr(dilate_ctrl + '.pupil', k=1)

        # Connect Attributes
        iris_md = cmds.createNode('multDoubleLinear', n=prefix + '_irs01_mdl')
        pupil_md = cmds.createNode('multDoubleLinear', n=prefix + '_ppl01_mdl')
        cmds.connectAttr(dilate_ctrl + '.iris', iris_md + '.input1')
        cmds.setAttr(iris_md + '.input2', 0.25)
        cmds.connectAttr(iris_md + '.output', eye_crv_detach[3] + '.parameter[1]')
        cmds.connectAttr(dilate_ctrl + '.pupil', pupil_md + '.input1')
        cmds.connectAttr(iris_md + '.output', pupil_md + '.input2')
        cmds.connectAttr(pupil_md + '.output', eye_crv_detach[3] + '.parameter[0]')


def setup_aim(lf_pivot, rt_pivot, head_ccc, aim_dist, prefix):
    aim_axis = [0.0, 0.0, 1.0]
    up_axis = [0.0, 1.0, 0.0]
    worldUp_axis = up_axis

    # LEFT
    eye_pos = cmds.xform(lf_pivot, q=1, ws=1, rp=1)
    # create eye aim transform
    eye_aim = cmds.group(em=1, n='lf_eye01_am01_loc')
    cmds.xform(eye_aim, ws=1, t=(eye_pos[0], eye_pos[1], (eye_pos[2] + aim_dist)))
    # create aim constraint
    aim_con = cmds.aicmdsonstraint(eye_aim, lf_pivot, aim=aim_axis, u=up_axis, wu=worldUp_axis, wuo=head_ccc,
                               wut='objectrotation')

    # RIGHT
    eye_pos = cmds.xform(rt_pivot, q=1, ws=1, rp=1)
    # create eye aim transform
    eye_aim = cmds.group(em=1, n='rt_eye01_am01_loc')
    cmds.xform(eye_aim, ws=1, t=(eye_pos[0], eye_pos[1], (eye_pos[2] + aim_dist)))
    # create aim constraint
    aim_con = cmds.aicmdsonstraint(eye_aim, rt_pivot, aim=aim_axis, u=up_axis, wu=worldUp_axis, wuo=head_ccc,
                               wut='objectrotation')
