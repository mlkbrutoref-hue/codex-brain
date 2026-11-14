from enum import Enum
from app.operational.config import ActionType


class OperationMode(str, Enum):
    NORMAL = 'NORMAL'
    CAUTIOUS = 'CAUTIOUS'
    RECOVERY = 'RECOVERY'
    PAUSED = 'PAUSED'


class OperationModeEngine:
    def __init__(self):
        self.mode = OperationMode.NORMAL
        self.failures = 0
        self.unknown = False

    def evaluate(self, context):
        if context.get('kill_switch') or context.get('circuit') == 'OPEN' or context.get('deadline_expired') or context.get('budget_empty'):
            self.mode = OperationMode.PAUSED
        elif self.unknown or context.get('unknown') or not context.get('adb_healthy', True) or not context.get('app_healthy', True) or context.get('version_changed'):
            self.mode = OperationMode.RECOVERY
        elif self.failures or context.get('unexpected_screen') or context.get('budget_low'):
            self.mode = OperationMode.CAUTIOUS
        else:
            self.mode = OperationMode.NORMAL
        return self.mode

    def can_execute(self, action_type):
        if self.mode == OperationMode.PAUSED:
            return False
        if self.mode == OperationMode.RECOVERY:
            return action_type == ActionType.READ_STATE
        return True

    def on_success(self, event=None):
        self.failures = 0

    def on_failure(self, error):
        self.failures += 1
        self.mode = OperationMode.CAUTIOUS

    def on_unknown_result(self, event=None):
        self.unknown = True
        self.mode = OperationMode.RECOVERY
