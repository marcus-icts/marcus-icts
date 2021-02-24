class BaseException(Exception):
  def __repr__(self):
    return '{}: {}'.format(self.__class__.__name__, self.args)
