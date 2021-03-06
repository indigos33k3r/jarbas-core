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
#
import re
import time
from threading import Lock

from mycroft.configuration import Configuration
from mycroft.tts import TTSFactory
from mycroft.util import create_signal, check_for_signal
from mycroft.util.log import LOG
from mycroft.messagebus.message import Message
from mycroft.metrics import report_timing, Stopwatch

ws = None  # TODO:18.02 - Rename to "messagebus"
config = None
tts = None
tts_hash = None
lock = Lock()

_last_stop_signal = 0
speak_flag = True


def set_speak_flag(event):
    global speak_flag
    speak_flag = True
    speak_status(event)


def unset_speak_flag(event):
    global speak_flag
    speak_flag = False
    speak_status(event)


def speak_status(event):
    global speak_flag, ws
    data = {"enabled": speak_flag}
    ws.emit(Message("speak.status", data))


def _start_listener(message):
    """
        Force Mycroft to start listening (as if 'Hey Mycroft' was spoken)
    """
    create_signal('startListening')


def handle_speak(event):
    """
        Handle "speak" message
    """
    config = Configuration.get()
    Configuration.init(ws)
    global _last_stop_signal

    # Get conversation ID
    if event.context and 'ident' in event.context:
        ident = event.context['ident']
    else:
        ident = 'unknown'

    with lock:
        stopwatch = Stopwatch()
        stopwatch.start()
        ws.emit(Message("mycroft.audio.speech.start", event.data))
        utterance = event.data['utterance']
        if event.data.get('expect_response', False):
            # When expect_response is requested, the listener will be restarted
            # at the end of the next bit of spoken audio.
            ws.once('recognizer_loop:audio_output_end', _start_listener)
        mute = event.data.get('mute', False)

        # This is a bit of a hack for Picroft.  The analog audio on a Pi blocks
        # for 30 seconds fairly often, so we don't want to break on periods
        # (decreasing the chance of encountering the block).  But we will
        # keep the split for non-Picroft installs since it give user feedback
        # faster on longer phrases.
        #
        # TODO: Remove or make an option?  This is really a hack, anyway,
        # so we likely will want to get rid of this when not running on Mimic
        if (config.get('enclosure', {}).get('platform') != "picroft" and
                len(re.findall('<[^>]*>', utterance)) == 0):
            start = time.time()
            chunks = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s',
                              utterance)
            for chunk in chunks:
                try:
                    mute_and_speak(chunk, ident)
                except KeyboardInterrupt:
                    raise
                except:
                    LOG.error('Error in mute_and_speak', exc_info=True)
                if _last_stop_signal > start or check_for_signal('buttonPress'):
                    break
        else:
            mute_and_speak(utterance, ident, mute)

        stopwatch.stop()
    report_timing(ident, 'speech', stopwatch, {'utterance': utterance,
                                               'tts': tts.__class__.__name__})


def mute_and_speak(utterance, ident, mute=False):
    """
        Mute mic and start speaking the utterance using selected tts backend.

        Args:
            utterance:  The sentence to be spoken
            ident:      Ident tying the utterance to the source query
    """
    global tts_hash
    LOG.info("Speak: " + utterance)
    if not speak_flag:
        return
    # update TTS object if configuration has changed
    if tts_hash != hash(str(config.get('tts', ''))):
        global tts
        # Stop tts playback thread
        tts.playback.stop()
        tts.playback.join()
        # Create new tts instance
        tts = TTSFactory.create()
        tts.init(ws)
        tts_hash = hash(str(config.get('tts', '')))

    try:
        if not mute:
            tts.execute(utterance, ident)
    finally:
        lock.release()


def handle_stop(event):
    """
        handle stop message
    """
    global _last_stop_signal
    if check_for_signal("isSpeaking", -1):
        _last_stop_signal = time.time()
        tts.playback.clear_queue()
        tts.playback.clear_visimes()


def init(websocket):
    """
        Start speach related handlers
    """

    global ws
    global tts
    global tts_hash
    global config

    ws = websocket
    Configuration.init(ws)
    config = Configuration.get()
    ws.on('mycroft.stop', handle_stop)
    ws.on('mycroft.audio.speech.stop', handle_stop)
    ws.on('mycroft.mic.listen', _start_listener)
    ws.on('speak', handle_speak)
    ws.on('speak.enable', set_speak_flag)
    ws.on('speak.disable', unset_speak_flag)
    ws.on('speak.status.request', speak_status)
    tts = TTSFactory.create()
    tts.init(ws)
    tts_hash = config.get('tts')


def shutdown():
    if tts:
        tts.playback.stop()
        tts.playback.join()
