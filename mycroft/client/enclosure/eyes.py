# Copyright 2017 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from mycroft.client.enclosure import Enclosure

'''
API for the functions that affect the Mark 1 eyes.
NOTE: current state management is poorly implemented,
will be changed in the future.
'''


class EnclosureEyes(Enclosure):
    """
    Listens to enclosure commands for Mycroft's Eyes.

    Performs the associated command on Arduino by writing on the Serial port.
    """

    def __init__(self, ws, writer):
        super(EnclosureEyes, self).__init__(ws, "eyes")
        self.writer = writer

    def on(self, event=None):
        self.writer.write("eyes.on")

    def off(self, event=None):
        self.writer.write("eyes.off")

    def blink(self, event=None):
        side = "b"
        if event and event.data:
            side = event.data.get("side", side)
        self.writer.write("eyes.blink=" + side)

    def narrow(self, event=None):
        self.writer.write("eyes.narrow")

    def look(self, event=None):
        if event and event.data:
            side = event.data.get("side", "")
            self.writer.write("eyes.look=" + side)

    def color(self, event=None):
        r, g, b = 255, 255, 255
        if event and event.data:
            r = int(event.data.get("r", r))
            g = int(event.data.get("g", g))
            b = int(event.data.get("b", b))
        color = (r * 65536) + (g * 256) + b
        self.writer.write("eyes.color=" + str(color))

    def set_pixel(self, event=None):
        idx = 0
        r, g, b = 255, 255, 255
        if event and event.data:
            idx = int(event.data.get("idx", idx))
            r = int(event.data.get("r", r))
            g = int(event.data.get("g", g))
            b = int(event.data.get("b", b))
        color = (r * 65536) + (g * 256) + b
        self.writer.write("eyes.set=" + str(idx) + "," + str(color))

    def fill(self, event=None):
        amount = 0
        if event and event.data:
            percent = int(event.data.get("percentage", 0))
            amount = int(round(23.0 * percent / 100.0))
        self.writer.write("eyes.fill=" + str(amount))

    def brightness(self, event=None):
        level = 30
        if event and event.data:
            level = event.data.get("level", level)
        self.writer.write("eyes.level=" + str(level))

    def volume(self, event=None):
        volume = 4
        if event and event.data:
            volume = event.data.get("volume", volume)
        self.writer.write("eyes.volume=" + str(volume))

    def reset(self, event=None):
        self.writer.write("eyes.reset")

    def spin(self, event=None):
        self.writer.write("eyes.spin")

    def timed_spin(self, event=None):
        length = 5000
        if event and event.data:
            length = event.data.get("length", length)
        self.writer.write("eyes.spin=" + str(length))
