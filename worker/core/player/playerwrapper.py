import errno
import logging
import os
import shutil
import subprocess

import pyvirtualdisplay

from utils import configreader

class PlayerWrapper:

    def __init__(self):
        self.__logger = logging.getLogger(__class__.__name__)
        self.__playercfg = configreader.load_configs("LibrasPlayer")
        self.__ffmpegcfg = configreader.load_configs("FFmpeg")
        self.__temp_dir = self.__playercfg.get("TempDir", "/tmp")

    def __start_frames_capture(
        self,
        input_file: str,
        correlation_tag: str,
        player_params: dict
    ) -> str:

        frames_dir = os.path.join(self.__temp_dir, correlation_tag, "frames")
        frames_path = os.path.join(frames_dir, "img_%08d.png")

        display_width = self.__playercfg.get("DisplayWidth", "640")
        display_height = self.__playercfg.get("DisplayHeight", "480")

        avatar_param = (player_params.get("avatar")
                        or self.__playercfg.get("Avatar", "icaro"))

        animation_speed = (player_params.get("speed")
                           or self.__playercfg.get("AnimationSpeed", "60"))

        subtitle_param = (player_params.get("caption")
                          or self.__playercfg.get("Caption", "subtitle_on"))

        unity_cmd = [
            self.__playercfg.get("PlayerBin", "None"),
            correlation_tag,
            input_file,
            frames_dir,
            display_width,
            display_height,
            animation_speed,
            self.__playercfg.get("VideoFramerate", "24"),
            avatar_param,
            subtitle_param]

        xephyr = pyvirtualdisplay.Display(
            visible=False,
            size=(display_width, display_height))

        xephyr.start()

        try:
            if not os.path.exists(frames_dir):
                os.makedirs(frames_dir)

            subprocess.check_call(unity_cmd, stdout=open(os.devnull, "w"))

        except OSError as error:
            if error.errno == errno.ENOENT:
                self.__logger.exception("Player '{0}' not found.".format(*unity_cmd))
            else:
                self.__logger.exception("An unexpected exception occurred.")
            frames_path = ""

        except subprocess.CalledProcessError:
            self.__logger.exception("'{0}' could not be executed".format(*unity_cmd))
            frames_path = ""

        finally:
            xephyr.stop()
            return frames_path

    def __start_video_rendering(
        self,
        frames_path: str, 
        correlation_tag: str
    ) -> str:

        video_name = "{}.{}".format(correlation_tag, "mp4")
        video_path = os.path.join(self.__temp_dir, correlation_tag, video_name)

        ffmpeg_cmd = [
            self.__ffmpegcfg.get("FFmpegBin", "None"),
            "-y", 
            "-loglevel", "quiet",
            "-start_number", "20",
            "-r", self.__ffmpegcfg.get("VideoFramerate", "24"),
            "-i", frames_path,
            "-c:v", self.__ffmpegcfg.get("VideoCodec", "libx264"),
            "-pix_fmt", self.__ffmpegcfg.get("PixelFormat", "yuv420p"),
            video_path]

        try:
            subprocess.check_call(ffmpeg_cmd, stdout=open(os.devnull, "w"))

        except OSError as error:
            if error.errno == errno.ENOENT:
                self.__logger.exception("Renderer '{0}' not found.".format(*ffmpeg_cmd))
            else:
                self.__logger.exception("An unexpected exception occurred.")
            video_path = ""

        except subprocess.CalledProcessError:
            self.__logger.exception("'{0}' could not be executed".format(*ffmpeg_cmd))
            video_path = ""

        finally:
            shutil.rmtree(os.path.dirname(frames_path), ignore_errors=True)
            return video_path

    def run(
        self, 
        input_text: str,
        correlation_tag: str,
        options: dict = {}
    ) -> tuple:

        gloss_name = "{}.{}".format(correlation_tag, "txt")
        gloss_path = os.path.join(self.__temp_dir, correlation_tag, gloss_name)

        os.makedirs(os.path.dirname(gloss_path), exist_ok=True)
        with open(gloss_path, "w") as gfile:
            gfile.write("{}#0".format(input_text))

        frames = self.__start_frames_capture(gloss_path, correlation_tag, options)
        if not frames:
            return None

        libras_video = self.__start_video_rendering(frames, correlation_tag)
        if not libras_video:
            return None

        libras_video_size = 0
        try:
            libras_video_size = os.path.getsize(libras_video)
        except:
            self.__logger.warning("Libras video size was not calculated.")
            pass

        libras_video_duration = 0

        return  libras_video, libras_video_size, libras_video_duration
