from datetime import datetime
from enum import Enum
from pydantic import BaseModel, RootModel, Field, model_validator, field_validator, computed_field
from typing import Optional

# from tcsession import Centrale


class ZoneStatusEnum(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    ISOLATED = "ISOLATED"
    UNKNOWN = "UNKNOWN"


class TcsMonitor(BaseModel):
    alertLive: bool
    alertMem: bool
    alive: bool
    anomalyLive: bool
    anomalyMem: bool
    armed: bool
    batteryLive: bool
    batteryMem: bool
    crc: int
    datetime: datetime
    fail: bool
    fw: str
    identSign: str
    isolation: bool
    maintenance: bool
    mask: bool
    powerlessLive: bool
    powerlessMem: bool
    robbery: bool
    tamperLive: bool
    tamperMem: bool


class TcsTpstatusObject(BaseModel):
    description: Optional[str] = ""
    icon: str
    idx: int


class TcsTpstatusObjectZones(TcsTpstatusObject):
    zones: list[int]


class TcsTpstatusZones(TcsTpstatusObject):
    allocated: bool
    camera: str
    inFail: bool
    inLowBattery: bool
    inSupervision: bool
    status: ZoneStatusEnum

    @computed_field
    @property
    def open(self) -> bool:
        return self.status == ZoneStatusEnum.OPEN


class TcsTpBase(BaseModel):
    code: None | str
    codes: None | list[TcsTpstatusObject]
    description: str
    icon: str
    idx: int
    ip: None | str
    keys: list[TcsTpstatusObject]
    passphTCS: None | str
    port: int
    programs: list[TcsTpstatusObjectZones]
    rcmds: list[TcsTpstatusObject]
    sn: str
    type: int
    zones: list[TcsTpstatusZones]


class TcsTpstatus(TcsTpBase):
    progress: int


class TcsTpReply(TcsTpBase):
    remotes: list
    status: None | TcsTpstatus = Field(default=None)


class TcsTpRequest(TcsTpBase):
    background_syncing: None | bool = False
    remotes: list = []
    syncCRC: None | bool = None
    use_fingerprint: None | bool = False
    valid_data: None | bool = True

    @field_validator("remotes", "keys", "codes", "rcmds")
    @classmethod
    def emptylist(cls, v, info):
        return []

    @model_validator(mode="before")
    @classmethod
    def get_programs(cls, data):
        data["programs"] = data["status"]["programs"]
        data["zones"] = data["status"]["zones"]

        return data


class TcsTpsList(RootModel):
    root: list[TcsTpReply]


class TcsProgramObj(BaseModel):
    alarm: bool
    free: bool
    memAlarm: bool
    prealarm: bool
    status: int


class TcsProgram(RootModel):
    root: list[TcsProgramObj]


class TcsZoneObj(TcsTpstatusZones):
    inPairedDeviceSupervision: bool


class TcsZones(RootModel):
    root: list[TcsZoneObj]


class TcsLog(BaseModel):
    category: int
    clip: bool
    clipPath: str
    datetime: datetime
    descr: str
    evento: int
    indice1: int
    indice2: int
    indice3: int
    visibility: int

    @model_validator(mode="before")
    @classmethod
    def generate_datetime(cls, data):
        dtstr = f"{data['date']} {data['time']}"

        data["datetime"] = datetime.strptime(dtstr, "%d/%m/%y %H:%M:%S")

        return data


class TcsLogs(RootModel):
    root: list[TcsLog]
