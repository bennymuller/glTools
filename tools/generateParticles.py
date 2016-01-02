import maya.mel as mel
import maya.cmds as cmds


def locatorParticlesUI():
    """
    """
    # Define window
    locParticleUI = 'locatorParticleWindow'
    if cmds.window(locParticleUI, q=True, ex=True): cmds.deleteUI(locParticleUI)
    locParticleUI = cmds.window(locParticleUI, t='Generate Particles')

    # UI Layout
    cmds.columnLayout(adj=False, cal='left')
    partiTFG = cmds.textFieldGrp('locParticle_particleTFG', label='Particle', text='', cw=[(1, 100)])
    radiusFFG = cmds.floatSliderGrp('locParticle_radiusFSG', label='radius', f=True, min=0.1, max=10.0, fmn=0.01,
                                  fmx=100.0, pre=2, v=1.0, cw=[(1, 100)])
    rotateLocCBG = cmds.checkBoxGrp('locParticle_rotateCBG', label='Add rotatePP', ncb=1, v1=0, cw=[(1, 100)])
    scaleLocCBG = cmds.checkBoxGrp('locParticle_scaleCBG', label='Add scalePP', ncb=1, v1=0, cw=[(1, 100)])
    selfCollideCBG = cmds.checkBoxGrp('locParticle_selfCollideCBG', label='self collide', ncb=1, v1=0, cw=[(1, 100)])

    cmds.button(l='Create Particles', c='glTools.tools.generateParticles.locatorParticlesFromUI()')

    # Popup menu
    cmds.popupMenu(parent=partiTFG)
    for p in cmds.ls(type=['particle', 'nParticle']):
        cmds.menuItem(p, c='cmds.textFieldGrp("' + partiTFG + '",e=True,text="' + p + '")')

    # Show Window
    cmds.showWindow(locParticleUI)


def locatorParticlesFromUI():
    """
    """
    # Define window
    locParticleUI = 'locatorParticleWindow'
    if not cmds.window(locParticleUI, q=True, ex=True): return

    # Get user selection
    sel = cmds.ls(sl=True)
    if len(sel) == 1:
        if not cmds.objExists(sel[0] + '.localScale'):
            sel = cmds.listRelatives(sel[0], c=True, pa=True)
    locList = [i for i in sel if cmds.objExists(i + '.localScale')]

    # Get Particle
    particle = cmds.textFieldGrp('locParticle_particleTFG', q=True, text=True)
    if not particle: particle = 'nParticle1'
    radius = cmds.floatSliderGrp('locParticle_radiusFSG', q=True, v=True)
    selfCollide = cmds.checkBoxGrp('locParticle_selfCollideCBG', q=True, v1=True)
    rt = cmds.checkBoxGrp('locParticle_rotateCBG', q=True, v1=True)
    sc = cmds.checkBoxGrp('locParticle_scaleCBG', q=True, v1=True)

    # Execute generate particle command
    locatorParticles(locList, particle, radius, selfCollide, rotatePP=rt, scalePP=sc)


def locatorParticles(locList, particle, radius=1, selfCollide=False, rotatePP=False, scalePP=False):
    """
    """
    # Check locator list
    if not locList: return

    # Check particles
    if not particle: particle = 'particle1'
    if not cmds.objExists(particle):
        particle = cmds.nParticle(n=particle)[0]

    # Set Particle Object Attrs
    cmds.setAttr(particle + '.particleRenderType', 4)
    cmds.setAttr(particle + '.radius', cmds.floatSliderGrp('locParticle_radiusFSG', q=True, v=True))
    cmds.setAttr(particle + '.selfCollide', cmds.checkBoxGrp('locParticle_selfCollideCBG', q=True, v1=True))

    # Create particles
    ptList = [cmds.pointPosition(i) for i in locList]
    cmds.emit(o=particle, pos=ptList)

    # Add and Set RotatePP/ScalePP Values
    if rotatePP:

        # Check rotatePP attrs
        if not cmds.objExists(particle + '.rotatePP'):
            addRotatePP(particle)

        # Set rotatePP attrs
        for i in range(len(locList)):
            rot = cmds.getAttr(locList[i] + '.r')
            cmds.particle(particle, e=True, at='rotatePP', id=i, vv=rot[0])

    if scalePP:

        # Check scalePP attrs
        if not cmds.objExists(particle + '.scalePP'):
            addScalePP(particle)

        # Set scalePP attrs
        for i in range(len(locList)):
            scl = cmds.getAttr(locList[i] + '.s')
            cmds.particle(particle, e=True, at='scalePP', id=i, vv=scl[0])

    # Save Initial State
    cmds.saveInitialState(particle)


def particleLocatorsUI():
    """
    """
    # Get current frame range
    start = cmds.playbackOptions(q=True, min=True)
    end = cmds.playbackOptions(q=True, max=True)

    # Define window
    particleLocatorsUI = 'particleLocatorsWindow'
    if cmds.window(particleLocatorsUI, q=True, ex=True): cmds.deleteUI(particleLocatorsUI)
    particleLocatorsUI = cmds.window(particleLocatorsUI, t='Generate Locators')

    # UI Layout
    cmds.columnLayout(adj=False, cal='left')
    partiTFG = cmds.textFieldGrp('partiLoc_particleTFG', label='Particle', text='', cw=[(1, 120)])
    prefixTFG = cmds.textFieldGrp('partiLoc_prefixTFG', label='Prefix', text='', cw=[(1, 120)])
    bakeAnicmdsBG = cmds.checkBoxGrp('partiLoc_bakeAnicmdsBG', label='Bake Animation', ncb=1, v1=0, cw=[(1, 120)])
    startEndIFG = cmds.intFieldGrp('partiLoc_startEndISG', nf=2, label='Frame Range', v1=start, v2=end, cw=[(1, 120)])

    rotateLocCBG = cmds.checkBoxGrp('partiLoc_rotateCBG', label='Rotate (rotatePP)', ncb=1, v1=0, cw=[(1, 120)])
    scaleLocCBG = cmds.checkBoxGrp('partiLoc_scaleCBG', label='Scale (scalePP)', ncb=1, v1=0, cw=[(1, 120)])

    cmds.button(l='Create Locators', c='glTools.tools.generateParticles.particleLocatorsFromUI()')

    # Popup menu
    cmds.popupMenu(parent=partiTFG)
    for p in cmds.ls(type=['particle', 'nParticle']):
        cmds.menuItem(p, c='cmds.textFieldGrp("' + partiTFG + '",e=True,text="' + p + '")')

    # Show Window
    cmds.showWindow(particleLocatorsUI)


def particleLocatorsFromUI():
    """
    """
    # Define window
    particleLocatorsUI = 'particleLocatorsWindow'
    if not cmds.window(particleLocatorsUI, q=True, ex=True): return

    # Get Particle
    particle = cmds.textFieldGrp('partiLoc_particleTFG', q=True, text=True)
    if not particle: raise Exception('Particle "' + particle + '" does not exist!!')

    # Get Options
    prefix = cmds.textFieldGrp('partiLoc_prefixTFG', q=True, text=True)
    bake = cmds.checkBoxGrp('partiLoc_bakeAnicmdsBG', q=True, v1=True)
    st = cmds.intFieldGrp('partiLoc_startEndISG', q=True, v1=True)
    en = cmds.intFieldGrp('partiLoc_startEndISG', q=True, v2=True)
    rotate = cmds.checkBoxGrp('partiLoc_rotateCBG', q=True, v1=True)
    scale = cmds.checkBoxGrp('partiLoc_scaleCBG', q=True, v1=True)

    # Create Locators
    particleLocators(particle, bakeSimulation=bake, rotate=rotate, scale=scale, start=st, end=en, prefix=prefix)


def particleLocators(particle, bakeSimulation=False, rotate=False, scale=False, start=0, end=-1, prefix=''):
    """
    """
    # Check Particle
    if not cmds.objExists(particle):
        raise Exception('Object "' + nParticle + '" is not a valid particle or nParticle object!')

    # Check Prefix
    if not prefix: prefix = particle

    # Get particle count
    count = cmds.getAttr(particle + '.count')
    if not count: raise Exception('Invalid particle count! (' + count + ')')

    # Create locators
    partiLocs = [cmds.spaceLocator(n=prefix + '_loc' + str(i))[0] for i in range(count)]
    partiLocsGrp = prefix + '_locGrp'
    if not cmds.objExists(partiLocsGrp): partiLocsGrp = cmds.group(em=True, n=partiLocsGrp)
    cmds.parent(partiLocs, partiLocsGrp)

    # For each particle, set locator position
    for i in range(count):
        pt = cmds.pointPosition(particle + '.pt[' + str(i) + ']')
        cmds.setAttr(partiLocs[i] + '.t', *pt)
        if rotate:
            rt = cmds.particle(particle, q=True, at='rotatePP', id=i)
            cmds.setAttr(partiLocs[i] + '.r', *rt)
        if scale:
            sc = cmds.particle(particle, q=True, at='scalePP', id=i)
            cmds.setAttr(partiLocs[i] + '.s', *sc)

    # Bake Simulation
    if (bakeSimulation):

        # Append particle expression
        expStr = '\n\n//--\n'
        expStr += 'int $id = id;\n'
        expStr += 'vector $pos = pos;\n'
        expStr += 'string $loc = ("' + prefix + '_loc"+$id);\n'
        expStr += 'if(`objExists $loc`){'
        expStr += '\t move -a ($pos.x) ($pos.y) ($pos.z) $loc;\n'
        if rotate:
            expStr += '\tvector $rot = rotatePP;\n'
            expStr += '\t rotate -a ($rot.x) ($rot.y) ($rot.z) $loc;\n'
        if scale:
            expStr += '\tvector $scl = scalePP;\n'
            expStr += '\t scale -a ($scl.x) ($scl.y) ($scl.z) $loc;\n'
        expStr += '}'

        # Old expression string
        oldRadStr = cmds.dynExpression(particle, q=True, s=True, rad=True)

        # Apply particle expression
        cmds.dynExpression(particle, s=oldRadStr + expStr, rad=True)

        # Bake to keyframes
        if end < start:
            start = cmds.playbackOptions(q=True, min=True)
            end = cmds.playbackOptions(q=True, max=True)
        bakeAttrs = ['tx', 'ty', 'tz']
        if rotate: bakeAttrs.extend(['rx', 'ry', 'rz'])
        if scale: bakeAttrs.extend(['sx', 'sy', 'sz'])
        cmds.bakeSimulation(partiLocs, at=bakeAttrs, t=(start, end))

        # Restore particle expression
        cmds.dynExpression(particle, s=oldRadStr, rad=True)


def addRotatePP(particle):
    """
    Add a per particle vector(Array) attribute named "rotatePP", to the specified particle object.
    An initial state attribute "rotatePP0" will also be created.
    @param particle: The particle or nParticle object to add the attribute to
    @type particle: str
    """
    # Check Particle
    if not cmds.objExists(particle):
        raise Exception('Particle "' + particle + '" does not exist!')
    if cmds.objectType(particle) == 'transform':
        particleShape = cmds.listRelatives(particle, s=True)
        if not particleShape:
            raise Exception('Unable to determine particle shape from transform "' + particle + '"!')
        else:
            particle = particleShape[0]
    if (cmds.objectType(particle) != 'particle') and (cmds.objectType(particle) != 'nParticle'):
        raise Exception('Object "' + particle + '" is not a valid particle or nParticle object!')

    # Add rotatePP attribute
    if not cmds.objExists(particle + '.rotatePP0'):
        cmds.addAttr(particle, ln='rotatePP0', dt='vectorArray')
    if not cmds.objExists(particle + '.rotatePP'):
        cmds.addAttr(particle, ln='rotatePP', dt='vectorArray')

    # Return Result
    return particle + '.rotatePP'


def addScalePP(particle):
    """
    Add a per particle vector(Array) attribute named "scalePP", to the specified particle object.
    An initial state attribute "scalePP0" will also be created.
    @param particle: The particle or nParticle object to add the attribute to
    @type particle: str
    """
    # Check Particle
    if not cmds.objExists(particle):
        raise Exception('Particle "' + particle + '" does not exist!')
    if cmds.objectType(particle) == 'transform':
        particleShape = cmds.listRelatives(particle, s=True)
        if not particleShape:
            raise Exception('Unable to determine particle shape from transform "' + particle + '"!')
        else:
            particle = particleShape[0]
    if (cmds.objectType(particle) != 'particle') and (cmds.objectType(particle) != 'nParticle'):
        raise Exception('Object "' + particle + '" is not a valid particle or nParticle object!')

    # Add rotatePP attribute
    if not cmds.objExists(particle + '.scalePP0'):
        cmds.addAttr(particle, ln='scalePP0', dt='vectorArray')
    if not cmds.objExists(particle + '.scalePP'):
        cmds.addAttr(particle, ln='scalePP', dt='vectorArray')

    # Return Result
    return particle + '.scalePP'
