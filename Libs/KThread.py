from threading import Thread
import sys
import trace

class KThread(Thread):
  """A subclass of threading.Thread, with a kill()
method.
    Usage:
         - create a new Thread:
        task = KThread(target=executeChanges, args=(validate, self, whatToDO))
        task.start()
         - To cancel the thread:
        self.task.kill()
        self.task.join()
"""
  def __init__(self, *args, **keywords):
    Thread.__init__(self, *args, **keywords)
    self.killed = False
    
  def start(self):
    """Start the thread."""
    self.__run_backup = self.run
    self.run = self.__run     
    Thread.start(self)
    
  def __run(self):
    """Hacked run function, which installs the
trace."""
    sys.settrace(self.globaltrace)
    self.__run_backup()
    self.run = self.__run_backup
    
  def globaltrace(self, frame, why, arg):
    if why == 'call':
      return self.localtrace
    else:
      return None
      
  def localtrace(self, frame, why, arg):
    if self.killed:
      if why == 'line':
        raise SystemExit()
    return self.localtrace
    
  def kill(self):
    self.killed = True
