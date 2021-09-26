from typing import Iterator, Optional

from voluptuous import All
from voluptuous import Optional as OptionalField
from voluptuous import Range
from voluptuous import Required as RequiredField
from voluptuous import Schema
from voluptuous.validators import Length

SCHEMA = Schema(
    {
        OptionalField("baud", default=115200): int,
        RequiredField("channels"): All(
            [
                Schema(
                    {
                        OptionalField("name"): All(str, Length(min=1)),
                        OptionalField("net_metered", default=False): bool,
                        RequiredField("number"): All(int, Range(min=1, max=32)),
                    }
                )
            ]
        ),
        OptionalField("name"): All(str, Length(min=1)),
        RequiredField("url"): str,
    },
)


class ChannelConfig:
    def __init__(self, channel: dict):
        self._name = (
            channel["name"] if "name" in channel else f"channel_{channel['number']}"
        )
        self._net_metered = channel["net_metered"]
        self._number = channel["number"]

    @property
    def name(self) -> str:
        return self._name

    @property
    def net_metered(self) -> bool:
        return self._net_metered

    @property
    def number(self) -> int:
        return self._number


class ChannelsConfig:
    def __init__(self, channels: dict):
        self._channels: dict[int, ChannelConfig] = {
            c["number"]: ChannelConfig(c) for c in channels
        }

    def __getitem__(self, key: int) -> ChannelConfig:
        assert key in self._channels
        return self._channels[key]

    def __len__(self) -> int:
        return len(self._channels)

    def __iter__(self) -> Iterator[ChannelConfig]:
        return iter(self._channels.values())


class DeviceConfig:
    schema = SCHEMA

    def __init__(self, device: dict):
        self._baud = device["baud"]
        self._channels = ChannelsConfig(device["channels"])
        self._name: Optional[str] = device.get("name")
        self._url = device["url"]

    @property
    def baud(self) -> int:
        """Return baud rate."""
        return self._baud

    @property
    def channels(self) -> ChannelsConfig:
        """Return the monitored channel configurations."""
        return self._channels

    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def url(self) -> str:
        """Return pySerial url of the serial device to connect to."""
        return self._url
