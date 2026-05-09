from dataclasses import dataclass


@dataclass
class RuntimeTransportMessage:
    sender_agent: str
    receiver_agent: str
    task_id: str
    payload: dict


class A2ARuntimeTransport:
    def send(self, message: RuntimeTransportMessage) -> None:
        raise NotImplementedError("A2A runtime transport not connected")
