# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = transaction_from_dict(json.loads(json_string))

from dataclasses import dataclass
from typing import Any, TypeVar, Type, cast


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class Transaction:
    agent: str
    amount: float
    transaction_id: str
    date: str
    phone_number: str

    @staticmethod
    def from_dict(obj: Any) -> 'Transaction':
        assert isinstance(obj, dict)
        agent = from_str(obj.get("agent"))
        amount = from_float(obj.get("amount"))
        transaction_id = from_str(obj.get("transaction_id"))
        date = from_str(obj.get("date"))
        phone_number = from_str(obj.get("phone_number"))
        return Transaction(agent, amount, transaction_id, date, phone_number)

    def to_dict(self) -> dict:
        result: dict = {}
        result["agent"] = from_str(self.agent)
        result["amount"] = to_float(self.amount)
        result["transaction_id"] = from_str(self.transaction_id)
        result["date"] = from_str(self.date)
        result["phone_number"] = from_str(self.phone_number)
        return result


def transaction_from_dict(s: Any) -> Transaction:
    return Transaction.from_dict(s)


def transaction_to_dict(x: Transaction) -> Any:
    return to_class(Transaction, x)
