from ai.behavior_tree import *


class Selector(NodeTree):
    """
    Implementation of NodeTree, this class represent a control node, the selector.
    """
    def __init__(self):
        super().__init__()


    def tick(self, dt):
        """
        This function override NodeTree.tick().
        The selector run the tick of all nodes until one return success.
        Then return success. If none of theme return success, then failure.
        If a node doesn't have finish it's tick, we return running.
        
        Parameters :
            dt (int) : Delta time.

        Return : 
            State (int) : Must be NodeTree.RUNNING, NodeTree.SUCCESS or NodeTree.FAILURE.
        """
        for node in super().get_nodes():
            status = node.tick(dt)

            if status == NodeTree.RUNNING:
                return NodeTree.RUNNING

            if status == NodeTree.SUCCESS:
                return NodeTree.SUCCESS

        return NodeTree.FAILURE