"""Butt Hub"""

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from voluptuous.validators import Number
from homeassistant.core import HomeAssistant
import logging
import threading
from datetime import timedelta
from homeassistant.core import CALLBACK_TYPE, callback
import asyncio
import struct

_LOGGER = logging.getLogger(__name__)


class ButtHub(DataUpdateCoordinator[dict]):
    """Thread safe wrapper class for pymodbus."""

    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        host: str,
        port: Number,
        scan_interval: Number,
    ):
        """Initialize the Modbus hub."""
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=timedelta(seconds=scan_interval),
        )

        # self._client = ModbusTcpClient(host=host, port=port, timeout=5)
        self.host = host
        self.port = port
        self._lock = threading.Lock()

        self.data: dict = {}

    @callback
    def async_remove_listener(self, update_callback: CALLBACK_TYPE) -> None:
        """Remove data update listener."""
        super().async_remove_listener(update_callback)

        """No listeners left then close connection"""
        if not self._listeners:
            self.close()

    def close(self) -> None:
        """Disconnect client."""
        with self._lock:
            self._client.close()

    async def async_send_command(self, command, host, port):
        data = None
        try:
            reader, writer = await asyncio.open_connection(host, port)
            writer.write(command)
            await writer.drain()

            # Lese das empfangene Byte-Array (hier ein Beispiel für 8 Bytes)
            data = await reader.read(1024)

            # Schließe den Writer
            writer.close()
            await writer.wait_closed()

        except Exception as e:
            _LOGGER.error("Reading data failed! BUTT Server is unreachable.")

        if data is None:
            data = b""

        return data

    async def _async_update_data(self) -> dict:
        data = {}
        try:
            data = await self.hass.async_add_executor_job(self.read_data)
        except Exception as e:
            _LOGGER.error(e)

        return {**data}

    async def connect(self):
        _LOGGER.info("Connect...")
        await self.async_send_command(b"\x01", self.host, self.port)

    async def disconnect(self):
        _LOGGER.info("Disconnect...")
        await self.async_send_command(b"\x02", self.host, self.port)

    async def start_record(self):
        _LOGGER.info("Start recording...")
        await self.async_send_command(b"\x03", self.host, self.port)

    async def stop_record(self):
        _LOGGER.info("Stop recording...")
        await self.async_send_command(b"\x04", self.host, self.port)

    def read_data(self) -> dict:

        data = {}

        data["ipadress"] = self.host
        data["port"] = self.port

        result = asyncio.run(self.async_send_command(b"\x05", self.host, self.port))

        if len(result) == 0:
            return data

        STATUS_CONNECTED = 0
        STATUS_CONNECTING = 1
        STATUS_RECORDING = 2
        STATUS_SIGNAL_DETECTED = 3
        STATUS_SILENCE_DETECTED = 4
        STATUS_EXTENDED_PACKET = 31
        STATUS_PACKET_VERSION = 3

        (status,) = struct.unpack("<I", result[:4])  # uint32 -> I 4
        status_connected: bool = (status & (1 << STATUS_CONNECTED)) > 0
        status_connecting: bool = (status & (1 << STATUS_CONNECTING)) > 0
        status_recording: bool = (status & (1 << STATUS_RECORDING)) > 0
        status_signal_detected: bool = (status & (1 << STATUS_SIGNAL_DETECTED)) > 0
        status_silence_detected: bool = (status & (1 << STATUS_SILENCE_DETECTED)) > 0
        status_extended_packet: bool = (status & (1 << STATUS_EXTENDED_PACKET)) > 0

        data["connected"] = status_connected
        data["connecting"] = status_connecting
        data["recording"] = status_recording
        data["signaldetected"] = status_signal_detected
        data["silencedetected"] = status_silence_detected
        data["extendedpacket"] = status_extended_packet

        if status_extended_packet:
            (
                version,  # uint16 -> H 2
                volume_left,  # int16 h 2
                volume_right,  # int16 h 2
                stream_seconds,  # uint32 -> I 4
                stream_kByte,  # uint32 -> I 4
                record_seconds,  # uint32 -> I 4
                record_kByte,  # uint32 -> I 4
                song_length,  # uint16 -> H 2
                rec_path_length,  # uint16 -> H 2
                listeners,  # int32 -> i 4
            ) = struct.unpack("<HhhIIIIHHi", result[4:34])

            if song_length > 0:
                song = struct.unpack(f"{song_length}s", result[34 : 34 + song_length])
            else:
                song = ""

            if rec_path_length > 0:
                rec_path = struct.unpack(
                    f"{rec_path_length}s",
                    result[34 + song_length : 34 + song_length + rec_path_length],
                )
            else:
                rec_path = ""

            data["streamseconds"] = stream_seconds
            data["streamkbytes"] = stream_kByte
            data["recordseconds"] = record_seconds
            data["recordkbytes"] = record_kByte
            data["volumeleft"] = volume_left * 0.1
            data["volumeright"] = volume_right * 0.1
            data["song"] = song[0].rstrip(b"\x00").decode("utf-8")
            data["recordpath"] = rec_path[0].rstrip(b"\x00").decode("utf-8")
            data["listeners"] = listeners
            data["version"] = version

        return data
