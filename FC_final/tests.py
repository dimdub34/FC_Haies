from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Submission(Demographics, timeout_happened=True)
        yield Submission(Final, check_html=False)
