import maya.mel as mel
import maya.cmds as cmds
import glTools.ui.utils
import os.path


def import2dTrackUI():
    """
    """
    # Build UI Window
    window = 'import2dTrackUI'
    if cmds.window(window, q=True, ex=True): cmds.deleteUI(window)
    window = cmds.window(window, title='Import 2D Track', wh=[500, 350])

    # Build UI Elements
    cmds.columnLayout(adjustableColumn=True)
    perspCamListTSL = cmds.textScrollList('importTrack_camListTSL', numberOfRows=8, ams=False)
    fileTFB = cmds.textFieldButtonGrp('importTrack_fileTFB', label='2D Track File', buttonLabel='Browse')
    cmds.textFieldButtonGrp(fileTFB, e=True, bc='glTools.ui.utils.loadFilePath("' + fileTFB + '",fileFilter="*.*")')
    cmds.textFieldGrp('importTrack_nameTFG', label="Point Name", text='trackPoint1')
    cmds.floatFieldGrp('importTrack_widthFFG', numberOfFields=1, label='Source Pixel Width', value1=2348)
    cmds.floatFieldGrp('importTrack_heightFFG', numberOfFields=1, label='Source Pixel Height', value1=1566)
    cmds.button(label='Import Track',
              c='import glTools.tools.import2dTrack;reload(glTools.tools.import2dTrack);glTools.tools.import2dTrack.import2dTrack()')
    cmds.button(label='Close', c='cmds.deleteUI("' + window + '")')

    # Build Camera List
    camList = cmds.listCameras(p=True)
    for cam in camList: cmds.textScrollList(perspCamListTSL, e=True, a=cam)

    # Show Window
    cmds.showWindow(window)


def import2dTrack():
    """
    """
    # Get UI Elements
    perspCamListUI = 'importTrack_camListTSL'
    fileUI = 'importTrack_fileTFB'
    pixelWidthUI = 'importTrack_widthFFG'
    pixelHeightUI = 'importTrack_heightFFG'
    pointNameUI = 'importTrack_nameTFG'

    # Get UI Values
    w = cmds.floatFieldGrp(pixelWidthUI, q=True, v1=True)
    h = cmds.floatFieldGrp(pixelHeightUI, q=True, v1=True)
    cam = cmds.textScrollList(perspCamListUI, q=True, si=True)[0]
    filePath = cmds.textFieldButtonGrp(fileUI, q=True, text=True)
    pointName = cmds.textFieldGrp(pointNameUI, q=True, text=True)

    # Ensure Camera Transform is Selected
    if cmds.objectType(cam) == 'camera':
        cam = cmds.listRelatives(cam, p=True)[0]

    # Check Track File Path
    if not os.path.isfile(filePath):
        raise Exception('Invalid file path "' + filePath + '"!')

    # Build Track Point Scene Elements
    point = cmds.spaceLocator(n=pointName)[0]
    plane = cmds.nurbsPlane(ax=(0, 0, 1), w=1, lr=1, d=1, u=1, v=1, ch=1, n=pointName + 'Plane')[0]
    print plane

    # Position Track Plane
    plane = cmds.parent(plane, cam)[0]
    cmds.setAttr(plane + '.translate', 0, 0, -5)
    cmds.setAttr(plane + '.rotate', 0, 0, 0)
    for attr in ['.tx', '.ty', '.rx', '.ry', '.rz']:
        cmds.setAttr(plane + attr, l=True)

    # Add FOV Attributes
    if not cmds.objExists(cam + '.horizontalFOV'):
        cmds.addAttr(cam, ln='horizontalFOV', at='double')
    if not cmds.objExists(cam + '.verticalFOV'):
        cmds.addAttr(cam, ln='verticalFOV', at='double')

    # Create FOV Expression
    expStr = '// Get Horizontal and Vertical FOV\r\n\r\n'
    expStr += 'float $focal =' + cam + '.focalLength;\r\n'
    expStr += 'float $aperture = ' + cam + '.horizontalFilmAperture;\r\n\r\n'
    expStr += 'float $fov = (0.5 * $aperture) / ($focal * 0.03937);\r\n'
    expStr += '$fov = 2.0 * atan ($fov);\r\n'
    expStr += cam + '.horizontalFOV = 57.29578 * $fov;\r\n\r\n'
    expStr += 'float $aperture = ' + cam + '.verticalFilmAperture;\r\n\r\n'
    expStr += 'float $fov = (0.5 * $aperture) / ($focal * 0.03937);\r\n'
    expStr += '$fov = 2.0 * atan ($fov);\r\n'
    expStr += cam + '.verticalFOV = 57.29578 * $fov;\r\n\r\n'
    expStr += '// Scale plane based on FOV\r\n\r\n'
    expStr += 'float $dist = ' + plane + '.translateZ;\r\n'
    expStr += 'float $hfov = ' + cam + '.horizontalFOV / 2;\r\n'
    expStr += 'float $vfov = ' + cam + '.verticalFOV / 2;\r\n\r\n'
    expStr += 'float $hyp = $dist / cos(deg_to_rad($hfov));\r\n'
    expStr += 'float $scale = ($hyp * $hyp) - ($dist * $dist);\r\n'
    expStr += plane + '.scaleX = (sqrt($scale)) * 2;\r\n\r\n'
    expStr += 'float $hyp = $dist / cos(deg_to_rad($vfov));\r\n'
    expStr += 'float $scale = ($hyp * $hyp) - ($dist * $dist);\r\n'
    expStr += plane + '.scaleY = (sqrt($scale)) * 2;'
    cmds.expression(s=expStr, o=plane, n='planeFOV_exp', ae=1, uc='all')

    # Open Track Data File
    count = 0
    f = open(filePath, 'r')

    # Build Track Path Curve
    crvCmd = 'curveOnSurface -d 1 '
    for line in f:
        u, v = line.split()
        crvCmd += '-uv ' + str(float(u) * (1.0 / w)) + ' ' + str(float(v) * (1.0 / h)) + ' '
        count += 1
    crvCmd += plane
    print crvCmd
    path = mel.eval(crvCmd)

    # Close Track Data File
    f.close()

    # Rebuild Curve
    cmds.rebuildCurve(path, fitRebuild=False, keepEndPoints=True, keepRange=True, spans=0, degree=3)

    # Attach Track Point to Path
    motionPath = cmds.pathAnimation(point, path, fractionMode=False, follow=False, startTimeU=1, endTimeU=count)
    exp = cmds.listConnections(motionPath + '.uValue')
    if exp: cmds.delete(exp)
    cmds.setKeyframe(motionPath, at='uValue', t=1, v=0)
    cmds.setKeyframe(motionPath, at='uValue', t=count, v=count - 1)
