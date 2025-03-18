from enum import Enum

# setup consts
class DEVICE_TYPE(str, Enum):
    GAME="game"
    CONTROL="control"

# game constants
class GAME_STATUS(str, Enum):
    ACTIVE= "active"
    HALTED= "halted"
    STOPPED= "stopped"
    DONE= "done"
class GAME_LEVELS(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
class GAME_MODES(str, Enum):
    ENtoZH = 'ENtoZH'
    ZHtoEN = 'ZHtoEN'

# mqtt consts
class MQTT_DATA_ACTIONS(str,Enum):
    NEW = "new"
    REMOVE = "remove"
    MATCHED = "matched"
    STATUS = "status"
class MQTT_COMMANDS(str, Enum):
    START = "start"
    PAUSE = "pause"
    STOP = "stop"
    RESET_DISPLAY = "reset_display"
    FLIP_VIEW = "flip_view"