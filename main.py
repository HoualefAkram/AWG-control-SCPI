import usb.core
import usb.util
import time


class OwonAG051:
    """
    SCPI Controller for OWON AG051 Function Generator via USB.
    """

    OUT_ENDPOINT = 0x03  # Bulk OUT
    IN_ENDPOINT = 0x81  # Bulk IN

    def __init__(self, vendor_id=0x5345, product_id=0x1234, timeout=1000):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.timeout = timeout
        self.dev = usb.core.find(idVendor=vendor_id, idProduct=product_id)

        if self.dev is None:
            raise ValueError(
                "OWON AG051 not found. Check USB connection and driver (WinUSB)."
            )

        self.dev.set_configuration()
        print("Connected:", self.query("*IDN?"))

    # ----------------------------- USB IO -----------------------------

    def send(self, cmd: str):
        """
        Send SCPI command (no response expected).
        """
        self.dev.write(self.OUT_ENDPOINT, cmd + "\r")
        time.sleep(0.05)  # short delay to ensure command is processed

    def query(self, cmd: str) -> str:
        """
        Send SCPI command and return the response (if any).
        """
        self.dev.write(self.OUT_ENDPOINT, cmd + "\r")
        try:
            data = self.dev.read(self.IN_ENDPOINT, 4096, self.timeout)
            return data.tobytes().decode("utf-8", errors="ignore").strip()
        except usb.core.USBTimeoutError:
            return ""  # Some commands don’t return anything

    # ------------------------- SCPI Commands --------------------------

    def reset(self):
        """Reset instrument to default state."""
        self.send("*RST")
        time.sleep(0.5)

    def set_function(self, shape="SINE"):
        """Set waveform function type."""
        self.send(f":FUNCtion {shape}")

    def set_frequency(self, freq_hz: float):
        """Set output frequency in Hz."""
        self.send(f":FUNCtion:FREQuency {freq_hz}")

    def set_amplitude(self, amplitude_vpp: float):
        """Set amplitude in volts peak-to-peak."""
        self.send(f":FUNCtion:AMPLitude {amplitude_vpp}")

    def set_offset(self, offset_v: float):
        """Set DC offset in volts."""
        self.send(f":FUNCtion:OFFSet {offset_v}")

    def output_on(self):
        """Enable output channel."""
        self.send(":CHANnel ON")

    def output_off(self):
        """Disable output channel."""
        self.send(":CHANnel OFF")

    # --------------------------- High-level ---------------------------

    def configure_waveform(self, shape="SINE", freq=1000, ampl=2.0, offset=0.0):
        """
        Configure full waveform in one call.
        """
        self.set_function(shape)
        self.set_frequency(freq)
        self.set_amplitude(ampl)
        self.set_offset(offset)

    def info(self):
        """Print device info and firmware version."""
        print(self.query("*IDN?"))


# ------------------------------- Example -------------------------------

if __name__ == "__main__":
    gen = OwonAG051()

    gen.reset()
    # gen.configure_waveform(shape="SINE", freq=1000, ampl=2.0, offset=0.0)
    # gen.output_on()

    # time.sleep(2)

    # gen.set_amplitude(4.0)  # change amplitude to 4 Vpp dynamically
    # time.sleep(2)

    # gen.output_off()
