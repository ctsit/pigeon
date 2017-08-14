from copy import copy
from traceback import format_exc

class RiskManager(object):
    def __init__(self, plan):
        self.plans = [plan]
        self.exceptions_encountered = []

    def add_backup(self, backup_plan):
        self.plans.append(backup_plan)

    def __call__(self):
        ran_out_of_plans = True
        for index, plan in enumerate( self.plans ):
            try:
                if index == 0:
                    return ( plan(), not ran_out_of_plans )
                else:
                    return ( plan(self.exceptions_encountered[-1]), not ran_out_of_plans )
            except Exception as ex:
                self.exceptions_encountered.append(format_exc())

        return ( self.exceptions_encountered, ran_out_of_plans )


