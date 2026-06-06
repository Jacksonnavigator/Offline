"""
Text-to-Speech engine using Piper TTS for offline speech synthesis
"""

import subprocess
import os
from pathlib import Path
from typing import Optional, List
from utils.logger import get_logger

logger = get_logger(__name__)


class PiperTTSEngine:
    """Text-to-Speech engine using Piper TTS"""
    
    def __init__(self, voice: str = "en_US-amy-medium", rate: float = 1.0):
        """
        Initialize Piper TTS engine
        
        Args:
            voice: Voice model to use (e.g., 'en_US-amy-medium')
            rate: Speech rate multiplier (0.5 to 2.0)
        """
        self.voice = voice
        self.rate = max(0.5, min(2.0, rate))  # Clamp between 0.5 and 2.0
        self.models_dir = Path("./models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.audio_dir = Path("./audio")
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.piper_executable = None
        self.is_playing = False
        
        self._check_piper_available()
        logger.info(f"PiperTTSEngine initialized with voice: {voice}, rate: {rate}")
    
    def _check_piper_available(self):
        """Check if Piper TTS is available in system PATH or locally"""
        try:
            # Try to find piper command
            result = subprocess.run(['piper', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.piper_executable = 'piper'
                logger.info("Piper TTS found in system PATH")
                return True
        except:
            pass
        
        # Try local models directory
        local_piper = self.models_dir / 'piper'
        if local_piper.exists():
            self.piper_executable = str(local_piper)
            logger.info("Piper TTS found locally")
            return True
        
        logger.warning("Piper TTS not found. Text-to-speech may not work.")
        return False
    
    def speak_text(self, text: str, output_file: Optional[str] = None) -> Optional[str]:
        """
        Convert text to speech and save as audio file
        
        Args:
            text: Text to convert
            output_file: Output audio file path (optional, auto-generates if not provided)
        
        Returns:
            Path to generated audio file or None if failed
        """
        try:
            if not self.piper_executable:
                logger.error("Piper TTS not available")
                return None
            
            if not text or not text.strip():
                logger.warning("Empty text provided")
                return None
            
            # Generate output file path if not provided
            if output_file is None:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
                output_file = str(self.audio_dir / f"speech_{timestamp}.wav")
            
            # Ensure output directory exists
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            
            # Use Piper to generate speech
            # This command pipes text to Piper and saves as WAV
            command = f'echo "{text.replace(chr(34), chr(92) + chr(34))}" | {self.piper_executable} -m {self.voice} -f {output_file}'
            
            # For cross-platform compatibility
            if os.name == 'nt':  # Windows
                result = subprocess.run(
                    command, 
                    shell=True, 
                    capture_output=True, 
                    text=True, 
                    timeout=30
                )
            else:  # Unix-like
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            
            if result.returncode == 0 and Path(output_file).exists():
                logger.info(f"Speech synthesized: {output_file}")
                return output_file
            else:
                logger.error(f"Piper TTS failed: {result.stderr}")
                return None
        
        except subprocess.TimeoutExpired:
            logger.error("Piper TTS timed out")
            return None
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            return None
    
    def play_text(self, text: str) -> bool:
        """
        Synthesize and play text (requires audio playback capability)
        
        Args:
            text: Text to speak
        
        Returns:
            True if started successfully
        """
        try:
            audio_file = self.speak_text(text)
            if audio_file:
                return self.play_audio_file(audio_file)
            return False
        except Exception as e:
            logger.error(f"Error playing text: {e}")
            return False
    
    def play_audio_file(self, audio_file: str) -> bool:
        """
        Play audio file
        
        Args:
            audio_file: Path to audio file
        
        Returns:
            True if playback started
        """
        try:
            # Try multiple audio players
            if os.name == 'nt':  # Windows
                # Use Windows Media Player or similar
                os.startfile(audio_file)
                return True
            else:  # Unix-like
                # Try common Linux audio players
                players = ['paplay', 'aplay', 'ffplay']
                for player in players:
                    try:
                        subprocess.Popen([player, audio_file])
                        logger.info(f"Playing audio with {player}: {audio_file}")
                        return True
                    except:
                        continue
                
                logger.warning("No audio player found")
                return False
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            return False
    
    def stop_speech(self) -> bool:
        """
        Stop current speech playback
        
        Returns:
            True if successful
        """
        try:
            if os.name == 'nt':
                subprocess.run(['taskkill', '/IM', 'wmplayer.exe'], capture_output=True)
            else:
                subprocess.run(['pkill', 'paplay'], capture_output=True)
                subprocess.run(['pkill', 'aplay'], capture_output=True)
                subprocess.run(['pkill', 'ffplay'], capture_output=True)
            
            self.is_playing = False
            logger.info("Speech stopped")
            return True
        except Exception as e:
            logger.error(f"Error stopping speech: {e}")
            return False
    
    def set_voice(self, voice: str) -> bool:
        """
        Set voice model
        
        Args:
            voice: Voice model identifier
        
        Returns:
            True if voice set successfully
        """
        try:
            # Validate voice exists (could be extended with voice list checking)
            self.voice = voice
            logger.info(f"Voice set to: {voice}")
            return True
        except Exception as e:
            logger.error(f"Error setting voice: {e}")
            return False
    
    def set_rate(self, rate: float) -> bool:
        """
        Set speech rate
        
        Args:
            rate: Speech rate multiplier (0.5 to 2.0)
        
        Returns:
            True if rate set successfully
        """
        try:
            self.rate = max(0.5, min(2.0, rate))
            logger.info(f"Speech rate set to: {self.rate}")
            return True
        except Exception as e:
            logger.error(f"Error setting rate: {e}")
            return False
    
    def get_available_voices(self) -> List[str]:
        """
        Get list of available voices
        
        Returns:
            List of voice identifiers
        """
        # This would typically list voices from Piper data directory
        # For now, return common voices
        common_voices = [
            'en_US-amy-medium',
            'en_US-arctic-medium',
            'en_US-cmu-arctic-fast',
            'en_GB-alan-medium',
            'en_GB-jenny_dioco-medium',
            'es-spain-male-medium',
            'fr-france-male-medium',
            'de-germany-male-medium',
            'it-italy-male-medium',
        ]
        return common_voices
    
    def is_ready(self) -> bool:
        """
        Check if TTS engine is ready
        
        Returns:
            True if ready
        """
        return self.piper_executable is not None
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            self.stop_speech()
            logger.info("Piper TTS cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up: {e}")
