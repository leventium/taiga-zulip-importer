from enum import Enum
from typing import Dict
from pydantic import BaseModel, Field


class ActionType(str, Enum):
    create = "create"
    delete = "delete"
    change = "change"
    test = "test"


class TypeEnum(str, Enum):
    milestone = "milestone"
    userstory = "userstory"
    task = "task"
    issue = "issue"
    wikipage = "wikipage"
    test = "test"


class TaigaWebhook(BaseModel):
    action: ActionType = Field(description="Field contains notification type.")
    type: TypeEnum = Field(description="Field contains the type of object.")
    by: Dict = Field(description="Field contains the information of the user "
                     "thast generate the notification.")
    date: str = Field(description="Field contains the date and time of thwe "
                      "current notification.")
    data: Dict = Field(description="Field contains the current object "
                       "information.")
    change: Dict = Field(default={},
                         description="Field (only present on change "
                         "notifications) contains the information about "
                         "the changes made")
