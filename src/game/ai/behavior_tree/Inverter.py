from ai.behavior_tree import *

class Inverter(NodeTreeSingleChild):
    """
    Implemetation of NodeTreeSingleChild, this class represent an inverter.

    Attributes:
        _fun (function(int)) : Function launched in tick.
    """

    
    def __init__(self, fun):
        super().__init__()
        self._fun = fun


    def tick(self, dt):
        """
        This function override NodeTree.tick().
        Run its child and reverse return value :
            If return success, then return failure.
            If return failure, then return success.

        On running, return running.
        
        Parameters :
            dt (int) : Delta time.

        Return : 
            State (int) : Must be NodeTree.RUNNING, NodeTree.SUCCESS or NodeTree.FAILURE.
        """

        status = super().get_nodes()[0].tick(dt)

        if status == NodeTree.RUNNING:
            return status

        elif status == NodeTree.FAILURE:
            return NodeTree.SUCCESS
                
        return NodeTree.FAILURE