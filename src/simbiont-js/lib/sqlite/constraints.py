#  constraints.py
#
#  Copyright 2017 The University of Sydney
#  Author: Jan P Buchmann <jan.buchmann@sydney.edu.au>
#  Description:
#
#  Version: 0

class Constraint:

    def __init__(self):
      self.constraint = ''

    def get_definition(self):
      return self.constraint

class Conflict:

  def __init__(self, clause='ABORT'):
    self.conflict_clause = clause

  def get_conflict(self):
    return " ON CONFLICT " + self.conflict_clause

class UniqueConstraint(Constraint):

  def __init__(self, conflict_clause):
    super(UniqueConstraint, self).__init__()
    self.constraint = 'UNIQUE'
    self.conflict = Conflict(clause=conflict_clause)

  def get_definition(self):
    return self.constraint + " " + self.conflict.get_conflict()

class DefaultConstraint(Constraint):

  def __init__(self, value):
    super(DefaultConstraint, self).__init__()
    self.constraint = 'DEFAULT'
    self.value = value

  def get_definition(self):
    return self.constraint + " " + self.value
