import maya.OpenMaya as OpenMaya


def outputRenderLayers():
    # Iterate through all render layers.
    iterator = OpenMaya.MItDependencyNodes(OpenMaya.MFn.kRenderLayer)
    print iterator

    # Loop though iterator objects
    while not iterator.isDone():

        # Attach a function set to the layer
        fn = OpenMaya.MFnDependencyNode(iterator.item())

        # Ignore the default render layers
        if( fn.name() == "defaultRenderLayer" ):
            iterator.next()
            continue

        elif(fn.name() == "globalRender"):
            iterator.next()
            continue

        print 'render layer name:', fn.name()

        # get connections to attributes on the layer node.
        # The LayerConnections will be a set of attributes
        # on the LayerNode that are connected to something else.
        LayerConnections = OpenMaya.MPlugArray()
        fn.getConnections(LayerConnections)

        connectedList = []

        for c in LayerConnections:
            ConnectedNodes = OpenMaya.MPlugArray()
            c.connectedTo(ConnectedNodes, False, True)

            print ConnectedNodes.length()

            for n in ConnectedNodes:
                fnItem = OpenMaya.MFnDependencyNode(n.node())
                print 'render layer member', fnItem.name()
                connectedList.append(fnItem.name())

        print connectedList

        # Iterate next.
        iterator.next()


outputRenderLayers()
