"""
Check status of CC jobs. Currently blocked, bc we need to set up a Database running on
this pod to store information about running jobs.
"""


class CheckStatus:

    def __init__(self, app, compute_id):

        self.app = app
        self.compute_id = compute_id

