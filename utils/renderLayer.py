import maya.OpenMaya as OpenMaya


def outputRenderLayers():
    # Iterate through all render layers.
    iterator = OpenMaya.MItDependencyNodes(OpenMaya.MFn.kRenderLayer)
    print iterator.item()

    # Loop though iterator objects
    while not iterator.isDone():

        # Attach a function set to the layer.
        fn = OpenMaya.MFnDependencyNode(iterator.item())

        # Ignore the default render layers
        if( fn.name() == "defaultRenderLayer" ):
            iterator.next()
            continue

        elif(fn.name() == "globalRender"):
            iterator.next()
            continue

        print 'render layer name:', fn.name()

        # Get connections to attributes on the layer node.
        # The LayerConnections will be a set of attributes on the LayerNode that are connected to something else.
        LayerConnections = OpenMaya.MPlugArray()
        fn.getConnections(LayerConnections)

        connectedList = []

        # Loop through all of the connections to the layer.
        for i in range(LayerConnections.length()):

            # Get the attribute plug on the other node so we can find out what it's connected to.
            ConnectedNodes = OpenMaya.MPlugArray()
            LayerConnections[i].connectedTo(ConnectedNodes, False, True)

            for j in range(ConnectedNodes.length()):
                fnItem = OpenMaya.MFnDependencyNode(ConnectedNodes[j].node())
                connectedList.append(fnItem.name())

        print connectedList

        # Iterate next.
        iterator.next()


outputRenderLayers()
