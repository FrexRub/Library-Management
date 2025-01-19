from datetime import datetime

from pydantic import BaseModel, field_serializer


class ReceivingBaseSchemas(BaseModel):
    book_id: int


class ReceivingCreateSchemas(ReceivingBaseSchemas):
    pass


class ReceivingReturnSchemas(ReceivingBaseSchemas):
    pass


class OutReceivingSchemas(ReceivingBaseSchemas):
    user_id: int
    date_of_issue: datetime
    date_of_return: datetime

    @field_serializer("date_of_issue")
    def serialize_date_of_issue(self, dt: datetime, _info):
        return dt.strftime("%d-%b-%Y")

    @field_serializer("date_of_return")
    def serialize_date_of_return(self, dt: datetime, _info):
        return dt.strftime("%d-%b-%Y")
