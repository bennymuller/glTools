import socket
import maya.cmds as cmds

maya = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def prankWindow(hardcoreMode=0):
    # Reset UI
    try:
        cmds.deleteUI("prankWindow")
    except:
        pass

# Create Window
window = cmds.window("prankWindow")
mainLayout = cmds.columnLayout("mainLayout", adj=1, p=window)
cmds.button("Disconnect", c='maya.close(); maya = socket.socket(socket.AF_INET, socket.SOCK_STREAM)', p=mainLayout)

# Duplicate the following line to create quick connection shortcuts here
cmds.button("Connect: Nilouco-pc", c='maya.connect(("nilouco-pc or IP address here",12543))', p=mainLayout)

# Do your stuff!
cmds.separator(h=10, p=mainLayout)
cmds.button("minimizeApp", c='maya.send("minimizeApp")', p=mainLayout)
cmds.button("restoreApp", c='maya.send("RaiseMainWindow")', p=mainLayout)
cmds.button("Clear selection", c='maya.send("select -cl")', p=mainLayout)
cmds.button("Select All", c='maya.send("select -all")', p=mainLayout)
cmds.button("fit Selected", c='maya.send("FrameSelected")', p=mainLayout)
cmds.button("frameAll", c='maya.send("FrameAll")', p=mainLayout)
cmds.button("fit Home", c='maya.send("viewSet -animate `optionVar -query animateRollViewCompass` -home")', p=mainLayout)
cmds.button("Toggle Component Mode", c='maya.send("toggleSelMode")', p=mainLayout)
cmds.button("TOOL: Translate", c='maya.send("setToolTo moveSuperContext")', p=mainLayout)
cmds.button("TOOL: Rotate", c='maya.send("setToolTo RotateSuperContext")', p=mainLayout)
cmds.button("TOOL: Scale", c='maya.send("setToolTo scaleSuperContext")', p=mainLayout)
cmds.button("Cycle BG color", c='maya.send("CycleBackgroundColor")', p=mainLayout)
cmds.button("Toggle Timeslider", c="maya.send('toggleUIComponentVisibility \"Time Slider\"')", p=mainLayout)
cmds.button("VIEWPORT: Toggle Viewcube", c="maya.send('ToggleViewCube')", p=mainLayout)
cmds.button("VIEWPORT: Wireframe", c="maya.send('DisplayWireframe')", p=mainLayout)
cmds.button("VIEWPORT: Shaded", c="maya.send('DisplayShaded')", p=mainLayout)
cmds.button("VIEWPORT: Toggle Views", c="maya.send('panePop')", p=mainLayout)
cmds.button("VIEWPORT: Maximize Viewport", c="maya.send('ToggleUIElements')", p=mainLayout)
cmds.button("Undo", c="maya.send('undo')", p=mainLayout)
cmds.button("Redo", c="maya.send('redo')", p=mainLayout)
cmds.button("Open Renderview", c="maya.send('RenderViewWindow')", p=mainLayout)
cmds.button("Open Rendernode", c="maya.send('createRenderNode \"-all\" \"\" \"\"')", p=mainLayout)
cmds.button("Open Help (F1)", c="maya.send('Help')", p=mainLayout)
cmds.button("Play forward timeline", c="maya.send('playButtonForward')", p=mainLayout)
cmds.button("Play backwards timeline", c="maya.send('playButtonBackward')", p=mainLayout)

# Hardcore ?!
cmds.separator(h=10, p=mainLayout)
cmds.button("NEW SCENE", c='maya.send("file -new -f")', en=hardcoreMode, p=mainLayout)
cmds.button("CLOSE MAYA", c='maya.send("quit -f")', en=hardcoreMode, p=mainLayout)
cmds.button("SHOW HOTBOX", c='maya.send("hotBox")', en=hardcoreMode, p=mainLayout)
cmds.button("OPEN NOTEPAD", c="maya.send('system \"start notepad\"')", en=hardcoreMode, p=mainLayout)

# Display window
cmds.showWindow(window)
