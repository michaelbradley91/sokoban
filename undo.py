from typing import List, Callable, Tuple, Dict
from bisect import bisect


class UndoManager:
    """
    Allows for actions to be undone / rolled back to certain points.
    Note that if not enabled, registration and saving has no effect.
    """
    def __init__(self):
        # The current index in the undo history. (This is one ahead of the actual position in each list)
        self.__current_index: int = 0

        # Can enable and disable undo and redo history. This is done while undoing or redoing for example
        self.enabled: bool = True

        # A tuple of undo and redo actions
        self.__undo_actions: List[Callable] = []
        self.__redo_actions: List[Callable] = []

        # A dictionary to remember locations in the undo history by name
        self.__labels: Dict[str, List[int]] = dict()

    def register(self, undo: Callable, redo: Callable):
        """
        Register an undo and redo action so that the change can be reverted.
        :param undo: a function to call to undo the change
        :param redo: a function to call to redo the change.
        :return: nothing
        """
        if not self.enabled:
            return

        if self.__current_index < len(self.__undo_actions):
            self.__undo_actions: List[Callable] = self.__undo_actions[:self.__current_index]
            self.__redo_actions: List[Callable] = self.__redo_actions[:self.__current_index]
            # Clear out any labels referring to positions we can no longer reach
            for label in self.__labels:
                self.__labels[label] = self.__labels[label][:bisect(self.__labels[label], self.__current_index)]

        self.__undo_actions.append(undo)
        self.__redo_actions.append(redo)

        self.__current_index += 1

    def save_position(self, label: str):
        """
        Save the current position / state with the given label.
        The same label can be use3d more than once.
        :param label: the label to save against
        :return: nothing
        """
        if not self.enabled:
            return

        if label not in self.__labels:
            self.__labels[label] = [self.__current_index]
        else:
            if self.__current_index not in self.__labels[label]:
                self.__labels[label].append(self.__current_index)

    def delete_label(self, label: str):
        """
        Forget about a label to free memory
        :param label: the label to forget
        :return: nothing
        """
        self.__labels.pop(label, None)

    def undo(self, label: str):
        """
        Undo to the previous index stored against the given label.
        If the label does not exist or has no position to return to, this does nothing.
        :param label: the label to undo untuil
        :return: nothing
        """
        if label not in self.__labels or len(self.__labels[label]) == 0:
            return

        # Calculate the new position to go back to
        indices = self.__labels[label][:bisect(self.__labels[label], self.__current_index)]
        if not indices:
            return

        target_index = indices[-1]
        if target_index == self.__current_index:
            if len(indices) <= 1:
                return
            target_index = indices[-2]

        self.undo_to_index(target_index)

    def undo_to_index(self, target_index: int):
        """
        Undo to a specific index. Note that zero undoes everything.
        Raises a value error if the index is greater than current position, or the index is negative.
        :param target_index: the index to undo to
        :return: nothing
        """
        if target_index < 0:
            raise ValueError("Cannot undo to a negative index.")
        if target_index > self.__current_index:
            raise ValueError(f"Cannot undo as ahead of index. Current index is {self.__current_index} "
                             f"and requested index was {target_index}")

        # Undo until we return to the specified index
        self.enabled = False
        for index in reversed(range(target_index, self.__current_index)):
            self.__undo_actions[index]()

        self.enabled = True
        self.__current_index = target_index

    def redo(self, label: str):
        """
        Redo to the next index stored against the given label.
        If the label does not exist or has no position to return to, this does nothing.
        :param label: the label to redo until
        :return: nothing
        """
        if label not in self.__labels or len(self.__labels[label]) == 0:
            return

        # Calculate the position to go forward to
        indices = self.__labels[label][bisect(self.__labels[label], self.__current_index):]
        if not indices:
            return

        self.redo_to_index(indices[0])

    def redo_to_index(self, target_index: int):
        """
        Redo to a specific index.
        Raises a value error if the index is less than current position, or the index is greater than the largest known.
        :return: nothing
        """
        if target_index > len(self.__redo_actions):
            raise ValueError("Cannot redo beyond redo history.")
        if target_index < self.__current_index:
            raise ValueError(f"Cannot redo as behind index. Current index is {self.__current_index} "
                             f"and requested index was {target_index}")

        # Redo until we return to the specified index
        self.enabled = False
        for index in range(self.__current_index, target_index):
            self.__redo_actions[index]()

        self.enabled = True
        self.__current_index = target_index


def test_undo_manager():
    undo_manager = UndoManager()
    undo_manager.save_position("saved")
    ls = [1]
    undo_manager.register(ls.pop, lambda: ls.append(1))
    undo_manager.save_position("saved")
    ls.append(2)
    undo_manager.register(ls.pop, lambda: ls.append(2))
    undo_manager.save_position("saved")
    ls.append(3)
    undo_manager.register(ls.pop, lambda: ls.append(3))
    undo_manager.save_position("saved")

    undo_manager.undo("saved")
    assert ls == [1, 2]

    undo_manager.undo("saved")
    assert ls == [1]

    undo_manager.undo("saved")
    assert ls == []

    undo_manager.undo("saved")
    assert ls == []

    undo_manager.redo("saved")
    assert ls == [1]

    undo_manager.redo("saved")
    assert ls == [1, 2]

    undo_manager.redo("saved")
    assert ls == [1, 2, 3]

    undo_manager.redo("saved")
    assert ls == [1, 2, 3]

    undo_manager.undo("saved")
    undo_manager.undo("saved")
    assert ls == [1]

    ls.append(4)
    undo_manager.register(ls.pop, lambda: ls.append(4))
    undo_manager.save_position("saved")

    undo_manager.redo("saved")
    assert ls == [1, 4]

    undo_manager.undo("saved")
    assert ls == [1]

    undo_manager.undo("saved")
    assert ls == []

    undo_manager.redo("saved")
    assert ls == [1]

    undo_manager.redo("saved")
    assert ls == [1, 4]

    undo_manager.redo("saved")
    assert ls == [1, 4]

