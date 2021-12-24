import threading
import time
from periphery import GPIO

from src.utils import Singleton


class SoftwarePWM(threading.Thread):

    def __init__(self, pin, frequency):
        self.baseTime = 1.0 / frequency
        self.maxCycle = 100.0
        self.sliceTime = self.baseTime / self.maxCycle
        self.pin = pin
        self.terminated = True
        self.toTerminate = False
        self.gpio = None

    def start(self, dutyCycle):
        """
        Start PWM output. Expected parameter is :
        - dutyCycle : percentage of a single pattern to set HIGH output on the GPIO pin

        Example : with a frequency of 1 Hz, and a duty cycle set to 25, GPIO pin will
        stay HIGH for 1*(25/100) seconds on HIGH output, and 1*(75/100) seconds on LOW output.
        """
        self.dutyCycle = dutyCycle
        self.gpio = GPIO("/dev/gpiochip0", self.pin, "out")
        self.terminated = False
        self.toTerminate = False
        self.thread = threading.Thread(None, self.run, None, (), {})
        self.thread.start()

    def run(self):
        """
        Run the PWM pattern into a background thread. This function should not be called outside of this class.
        """
        while not self.toTerminate:
            if self.dutyCycle > 0:
                self.gpio.write(True)
                time.sleep(self.dutyCycle * self.sliceTime)

            if self.dutyCycle < self.maxCycle:
                self.gpio.write(False)
                time.sleep((self.maxCycle - self.dutyCycle) * self.sliceTime)

        self.terminated = True

    def changeDutyCycle(self, dutyCycle):
        """
        Change the duration of HIGH output of the pattern. Expected parameter is :
        - dutyCycle : percentage of a single pattern to set HIGH output on the GPIO pin

        Example : with a frequency of 1 Hz, and a duty cycle set to 25, GPIO pin will
        stay HIGH for 1*(25/100) seconds on HIGH output, and 1*(75/100) seconds on LOW output.
        """
        self.dutyCycle = dutyCycle

    def changeFrequency(self, frequency):
        """
        Change the frequency of the PWM pattern. Expected parameter is :
        - frequency : the frequency in Hz for the PWM pattern. A correct value may be 100.

        Example : with a frequency of 1 Hz, and a duty cycle set to 25, GPIO pin will
        stay HIGH for 1*(25/100) seconds on HIGH output, and 1*(75/100) seconds on LOW output.
        """
        self.baseTime = 1.0 / frequency
        self.sliceTime = self.baseTime / self.maxCycle


    def stop(self):
        """
        Stops PWM output.
        """
        if not self.terminated:
            self.toTerminate = True
            while not self.terminated:
                # Just wait
                time.sleep(0.01)
            self.gpio.write(False)
            self.gpio.close()
            self.gpio = None


class ControllerPWM:
    def __init__(self, pin):
        self.pin = pin
        self.frequency = 480
        self.software_pwm = None
        self.angle = None

        self.delay_ms_1_grad = 100

    def set_angle(self, angle):
        if self.software_pwm is None:
            self.software_pwm = SoftwarePWM(self.pin, self.frequency)
        if self.software_pwm.terminated:
            self.software_pwm.start(angle)
        else:
            self.software_pwm.changeDutyCycle(angle)
        if self.angle is None:
            delay_ms = self.delay_ms_1_grad * 180
        else:
            delay_ms = self.delay_ms_1_grad * abs(self.angle - angle)
        self.angle = angle
        threading.Thread(target=self.disable_pwm, args=(delay_ms, )).start()

    def disable_pwm(self, delay_ms = 100):
        time.sleep(delay_ms / 1000)
        self.software_pwm.stop()


class Controller(metaclass=Singleton):

    def __init__(self, yaw_pin=20, pitch_pin=9, step_angle=2):
        """
        :param yaw_pin: влево вправо
        :param pitch_pin: вверх вниз
        """
        self.yaw_mutex = threading.Lock()
        self.pitch_mutex = threading.Lock()
        self.yaw_pin = yaw_pin
        self.pitch_pin = pitch_pin

        self.yaw_controller = ControllerPWM(self.yaw_pin)
        self.pitch_controller = ControllerPWM(self.pitch_pin)

        self.yaw_angle = 50
        self.pitch_angle = 50

        self.yaw_min = 0
        self.yaw_max = 100
        self.pitch_min = 0
        self.pitch_max = 100

        self.step_angle = step_angle

    def set_yaw_angle(self, angle):
        with self.yaw_mutex:
            self.yaw_controller.set_angle(angle)

    def set_pitch_angle(self, angle):
        with self.pitch_mutex:
            self.pitch_controller.set_angle(angle)

    def up(self, step=None):
        step = step if step is not None else self.step_angle
        self.pitch_angle = max(self.pitch_angle - step, self.pitch_min)
        print("up", self.pitch_angle)
        self.set_pitch_angle(self.pitch_angle)

    def down(self, step=None):
        step = step if step is not None else self.step_angle
        self.pitch_angle = min(self.pitch_angle + step, self.pitch_max)
        print("down", self.pitch_angle)
        self.set_pitch_angle(self.pitch_angle)

    def left(self, step=None):
        step = step if step is not None else self.step_angle
        self.yaw_angle = min(self.yaw_angle + step, self.yaw_max)
        print("left", self.yaw_angle)
        self.set_yaw_angle(self.yaw_angle)

    def right(self, step=None):
        step = step if step is not None else self.step_angle
        self.yaw_angle = max(self.yaw_angle - step, self.yaw_min)
        print("right", self.yaw_angle)
        self.set_yaw_angle(self.yaw_angle)


controller = Controller()
