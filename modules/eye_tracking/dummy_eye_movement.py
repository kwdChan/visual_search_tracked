from psychopy import event
raise NotImplementedError
class DummyEyeMovementCursor:
    def __init__(self, win):
        self.win = win
        self.was_mouseVisiable = self.win.mouseVisible 
        self.win.mouseVisible = True
        self.mouse = event.Mouse(win=win)

    def __del__(self):
        self.win.mouseVisible = self.was_mouseVisiable

    def getNewestSample(self):
        self.mouse.getPos()
