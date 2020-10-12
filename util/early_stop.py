from __future__ import print_function
from collections import deque

class TrainEarlyStopOnLosses(object):
    """Estimate if early stop conditions on losses fullfiled
    """
    def __init__(self, stop_conditions, max_mem, stop_on_all_conditions):
        """Initialize the TrainEarlyStopOnLosses( class

        Parameters:
            stop_conditions (dict) - defintion of stops conditions with entries name_of_loss : max_change or name_of_Loss:[min_value,max_value]
            max_mem (int) - number of previous losses considered
            stop_on_all_conditions - if stop is on all conditions fullfilled (otherwise on any)
        """
        self.stop_conditions = stop_conditions
        self.max_mem = max_mem
        self.stop_on_all_conditions = stop_on_all_conditions
        self.recent_losses = dict()

    # check early stop, storage losses
    def check(self, model):
        """checks if early stop

        Parameters:
            model
        Returns:
            boolean
                True if early stop conditions fullfilled
        """
        early_stop_flag = False

        if len(self.stop_conditions) > 0:

            losses = model.get_current_losses()

            # check on start if properly configured
            if len(self.recent_losses) == 0:
                self. __check_config(losses)

            stop_on_losses = []
            for loss in self.stop_conditions:

                stop_on_losses.append(False)

                if loss not in self.recent_losses:
                    self.recent_losses[loss] = deque([], self.max_mem)

                self.recent_losses[loss].append(losses[loss])

                if len(self.recent_losses[loss]) >= self.max_mem:
                    min_mem_loss = max(self.recent_losses[loss])
                    max_mem_loss = min(self.recent_losses[loss])

                    # min max loss given
                    if isinstance(self.stop_conditions[loss], list) or isinstance(self.stop_conditions[loss], tuple):
                        if min_mem_loss > self.stop_conditions[loss][0] and max_mem_loss < self.stop_conditions[loss][1]:
                            stop_on_losses[-1] = True

                    # max diff given
                    if isinstance(self.stop_conditions[loss], float):
                        if abs(max_mem_loss - min_mem_loss) <= 2 * self.stop_conditions[loss]:
                            stop_on_losses[-1] = True

            if self.stop_on_all_conditions:
                if all(stop_on_losses):
                    print('all stop criteria fulfilled : stop')
                    early_stop_flag = True
            else:
                if any(stop_on_losses):
                    print('at least one stop criterion fulfilled : stop')
                    early_stop_flag = True

        return early_stop_flag

    # early stop config sanity check
    def __check_config(self, losses):

        if len(self.stop_conditions) > 0:
            # early stop sanity check of conditions
            if self.max_mem <= 0:
                raise Exception("stop condition needs at least one prev data")

            for loss in self.stop_conditions:
                if loss not in losses:
                    raise Exception("unrecognized stop condition : %s" % format(loss, ))

                # min max
                if isinstance(self.stop_conditions[loss], list) or isinstance(self.stop_conditions[loss],
                                                                              tuple):
                    if self.stop_conditions[loss][0] >= self.stop_conditions[loss][1]:
                        raise Exception(
                            "wrong stop condition : %s   bounds must be in order and not equal" % format(loss, ))
                if self.stop_conditions[loss][1] <= 0:
                    raise Exception(
                        "wrong stop condition : %s   upper bound cannot be negative or zero" % format(loss, ))

                # diff
                if isinstance(self.stop_conditions[loss], float):
                    if self.stop_conditions[loss] <= 0:
                        raise Exception("wrong stop condition : %s  cannot be negative or zero" % format(loss, ))
