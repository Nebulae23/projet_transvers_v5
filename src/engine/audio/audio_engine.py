# src/engine/audio/audio_engine.py
from ctypes import *
from typing import Dict, Optional
import pyOpenAL
from openal import *
import pyfmodex as fmod

class AudioEngine:
    def __init__(self):
        # Initialize OpenAL
        self.al_device = alcOpenDevice(None)
        if not self.al_device:
            raise RuntimeError("Failed to open OpenAL device")
            
        self.al_context = alcCreateContext(self.al_device, None)
        if not self.al_context:
            alcCloseDevice(self.al_device)
            raise RuntimeError("Failed to create OpenAL context")
            
        alcMakeContextCurrent(self.al_context)
        
        # Initialize FMOD
        self.fmod_system = fmod.System()
        self.fmod_system.init(32, fmod.INIT_NORMAL)
        
        # Sound buffers and sources
        self.buffers: Dict[str, int] = {}
        self.sources: Dict[str, int] = {}
        
    def load_sound(self, sound_id: str, file_path: str) -> bool:
        # Load sound using OpenAL for spatial audio
        buffer = alGenBuffers(1)
        
        try:
            with open(file_path, 'rb') as f:
                wave_data = f.read()
                alBufferData(buffer, AL_FORMAT_STEREO16, wave_data, len(wave_data), 44100)
                self.buffers[sound_id] = buffer
                return True
        except Exception as e:
            alDeleteBuffers(1, buffer)
            print(f"Failed to load sound {sound_id}: {e}")
            return False
            
    def create_source(self, source_id: str) -> Optional[int]:
        source = alGenSources(1)
        alSourcef(source, AL_PITCH, 1.0)
        alSourcef(source, AL_GAIN, 1.0)
        alSource3f(source, AL_POSITION, 0.0, 0.0, 0.0)
        alSource3f(source, AL_VELOCITY, 0.0, 0.0, 0.0)
        alSourcei(source, AL_LOOPING, AL_FALSE)
        
        self.sources[source_id] = source
        return source
        
    def play_sound(self, sound_id: str, source_id: str):
        if sound_id in self.buffers and source_id in self.sources:
            alSourcei(self.sources[source_id], AL_BUFFER, self.buffers[sound_id])
            alSourcePlay(self.sources[source_id])
            
    def update_listener(self, position, velocity, orientation):
        alListener3f(AL_POSITION, *position)
        alListener3f(AL_VELOCITY, *velocity)
        alListenerfv(AL_ORIENTATION, orientation)
        
    def cleanup(self):
        for source in self.sources.values():
            alDeleteSources(1, source)
        for buffer in self.buffers.values():
            alDeleteBuffers(1, buffer)
            
        alcMakeContextCurrent(None)
        alcDestroyContext(self.al_context)
        alcCloseDevice(self.al_device)
        
        self.fmod_system.release()