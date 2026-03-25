from . import *

class PlayerBot(Bot):
    def play_round(self):
        if self.round_number == 1:
            yield Intro
            yield Instructions
            yield Submission(InstructionsWaitMonitor, check_html=False)
            yield Submission(Understanding, timeout_happened=True)
        yield Submission(Decision, timeout_happened=True)
        yield Results
        if self.round_number == C.NUM_ROUNDS:
            yield Final